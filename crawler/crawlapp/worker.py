import datetime
import logging
import time
import urllib

from bs4 import BeautifulSoup

from crawlapp.models import Crawl, Url


logger = logging.getLogger(__name__)


class Worker(object):
    NO_URLS = 'no urls'
    max_depth = 1
    
    def process(self):
        logger.info("Worker.process - Worker starting...")
        
        while True:
            logger.info("Worker.process - Worker processing...")
            
            process_iteration_result = self.process_iteration()
            
            if process_iteration_result == self.NO_URLS:
                time.sleep(5)
            
    def process_iteration(self):
        url_object = self.get_url_from_db()
        
        if url_object:
            try:
                logger.debug("Fetching url: %s ..." % url_object.url)
                response = self.fetch_url(url_object.url)
                url_object.content_type = response.headers['Content-Type']
                logger.info("(URL: %s) Response code = %r; content-type = %s" % 
                    (url_object.url, response.code, url_object.content_type))
                if 'text/html' in url_object.content_type:
                    self.parse_html(response, url_object)
            finally:
                url_object.visited = datetime.datetime.now()
                url_object.save()
                return url_object
        else:
            logger.warn("No URLs to process.")
            return self.NO_URLS
            
    def get_url_from_db(self):
        try:
            url_object = Url.objects.filter(visited=None)[0]
        except IndexError:
            return None
        else:
            logger.info("Worker.get_url_from_db - url = %s; depth = %d" % (url_object.url, url_object.depth))
            return url_object
            
    def fetch_url(self, url):
        return urllib.urlopen(url)
        
    def parse_html(self, response, url_object):
        soup = BeautifulSoup(response.read())
        
        # Look for images
        for img in soup.find_all('img'):
            url = img.get('src')
            url = urllib.basejoin(url_object.url, url)
            logger.info("(URL: %s) Found image: %s" % (url_object.url, url))
            new_url_object = Url.objects.create(crawl_id=url_object.crawl_id, url=url, depth=url_object.depth+1, parent=url_object)
            new_url_object.save()

        # Look for links to follow
        if url_object.depth < self.max_depth:
            for link in soup.find_all('a'):
                url = link.get('href')
                url = urllib.basejoin(url_object.url, url)
                logger.info("(URL: %s) Queueing url: %s" % (url_object.url, url))
                new_url_object = Url.objects.create(crawl_id=url_object.crawl_id, url=url, depth=url_object.depth+1, parent=url_object)
                new_url_object.save()
        else:
            logger.info("(URL: %s) Depth is %d - ignoring links" % (url_object.url, url_object.depth))
