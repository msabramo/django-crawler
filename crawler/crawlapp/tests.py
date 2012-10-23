import datetime
import json
import logging

logging.basicConfig(level=logging.INFO)

from mock import MagicMock, patch

from django.test import TestCase

from crawlapp.models import Crawl, Url
from crawlapp.worker import Worker


class SimpleTest(TestCase):
    
    def test_worker_crawl_no_urls(self):
        worker = Worker()
        self.assertEqual(worker.process_iteration(), Worker.NO_URLS)
        
        
    def test_worker_crawl_starting_with_one_url(self):
        # Set up crawl of one URL and do some initial checks
        crawl = self.crawl_setup()
        
        self.crawl_iteration_1(crawl)
        self.crawl_iteration_2(crawl)
        self.crawl_iteration_3(crawl)
        self.crawl_iteration_4(crawl)
        self.crawl_iteration_5(crawl)
        self.crawl_iteration_6(crawl)
        
        
    def crawl_setup(self):
        crawl = TestCrawl()
        
        url_object = crawl.add_url('http://notarealdomainjustfortesting.com/nopagehere', depth=0)
        
        self.assertEqual(crawl.num_total_urls(), 1)
        self.assertTrue(crawl.url_not_visited(url_object))
        self.assertStatusView(crawl, expected_in_progress=1, expected_completed=0)
        
        return crawl
        
        
    def crawl_iteration_1(self, crawl):
        # Mock response for http://notarealdomainjustfortesting.com/nopagehere
        mock_urlopen = MagicMock()
        mock_urlopen.return_value.code = 200
        mock_urlopen.return_value.headers = {'Content-Type': 'text/html; charset=ISO-8859-1'}
        mock_urlopen.return_value.read.return_value = """
<a href="/anotherpage">Click here</a>
<img src="img1.png" />
<img src="img2.png" />
"""

        with patch('urllib.urlopen', mock_urlopen):
            url_object = Worker().process_iteration()

        self.assertEqual(url_object.url, 'http://notarealdomainjustfortesting.com/nopagehere')        
        self.assertEqual(url_object.content_type, 'text/html; charset=ISO-8859-1')
        self.assertTrue(crawl.url_visited_recently(url_object))

        self.assertEqual(crawl.num_total_urls(), 4)
        self.assertStatusView(crawl, expected_in_progress=4, expected_completed=1)
        self.assertResultView(crawl, expected_image_urls=0)


    def crawl_iteration_2(self, crawl):
        # Mock response for http://notarealdomainjustfortesting.com/img1.png
        mock_urlopen = MagicMock()
        mock_urlopen.return_value.code = 200
        mock_urlopen.return_value.headers = {'Content-Type': 'image/png'}

        with patch('urllib.urlopen', mock_urlopen):
            url_object = Worker().process_iteration()
            
        self.assertEqual(url_object.url, 'http://notarealdomainjustfortesting.com/img1.png')
        self.assertEqual(url_object.content_type, 'image/png')
        self.assertTrue(crawl.url_visited_recently(url_object))
        
        self.assertEqual(crawl.num_total_urls(), 4)
        self.assertStatusView(crawl, expected_in_progress=4, expected_completed=2)
        self.assertResultView(crawl, expected_image_urls=1)
        
        
    def crawl_iteration_3(self, crawl):
        # Mock response for http://notarealdomainjustfortesting.com/img2.png
        mock_urlopen = MagicMock()
        mock_urlopen.return_value.code = 200
        mock_urlopen.return_value.headers = {'Content-Type': 'image/png'}

        with patch('urllib.urlopen', mock_urlopen):
            url_object = Worker().process_iteration()
        
        self.assertEqual(url_object.url, 'http://notarealdomainjustfortesting.com/img2.png')
        self.assertEqual(url_object.content_type, 'image/png')
        self.assertTrue(crawl.url_visited_recently(url_object))

        self.assertEqual(crawl.num_total_urls(), 4)
        self.assertStatusView(crawl, expected_in_progress=4, expected_completed=3)
        self.assertResultView(crawl, expected_image_urls=2)


    def crawl_iteration_4(self, crawl):
        # Mock response for http://notarealdomainjustfortesting.com/anotherpage
        mock_urlopen = MagicMock()
        mock_urlopen.return_value.code = 200
        mock_urlopen.return_value.headers = {'Content-Type': 'text/html; charset=ISO-8859-1'}
        mock_urlopen.return_value.read.return_value = """
<a href="/anotherpage">Click here</a>
<img src="img3.png" />
<img src="img4.jpg" />
"""

        with patch('urllib.urlopen', mock_urlopen):
            url_object = Worker().process_iteration()

        self.assertEqual(url_object.url, 'http://notarealdomainjustfortesting.com/anotherpage')        
        self.assertEqual(url_object.content_type, 'text/html; charset=ISO-8859-1')
        self.assertTrue(crawl.url_visited_recently(url_object))
        
        self.assertEqual(crawl.num_total_urls(), 6)
        self.assertStatusView(crawl, expected_in_progress=6, expected_completed=4)
        self.assertResultView(crawl, expected_image_urls=2)
        
        
    def crawl_iteration_5(self, crawl):
        # Mock response for http://notarealdomainjustfortesting.com/img3.png
        mock_urlopen = MagicMock()
        mock_urlopen.return_value.code = 200
        mock_urlopen.return_value.headers = {'Content-Type': 'image/png'}

        with patch('urllib.urlopen', mock_urlopen):
            url_object = Worker().process_iteration()
            
        self.assertEqual(url_object.url, 'http://notarealdomainjustfortesting.com/img3.png')
        self.assertEqual(url_object.content_type, 'image/png')
        self.assertTrue(crawl.url_visited_recently(url_object))
        
        self.assertEqual(crawl.num_total_urls(), 6)
        self.assertStatusView(crawl, expected_in_progress=6, expected_completed=5)
        self.assertResultView(crawl, expected_image_urls=3)
        
        
    def crawl_iteration_6(self, crawl):
        # Mock response for http://notarealdomainjustfortesting.com/img4.jpg
        url_object = self.do_iteration_with_mock(expected_code=200, expected_content_type='image/jpeg')
            
        self.assertEqual(url_object.url, 'http://notarealdomainjustfortesting.com/img4.jpg')
        self.assertEqual(url_object.content_type, 'image/jpeg')
        self.assertTrue(crawl.url_visited_recently(url_object))
        
        self.assertEqual(crawl.num_total_urls(), 6)
        self.assertStatusView(crawl, expected_in_progress=6, expected_completed=6)
        self.assertResultView(crawl, expected_image_urls=4)


    def do_iteration_with_mock(self, expected_code, expected_content_type, expected_content=None):
        mock_urlopen = MagicMock()
        mock_urlopen.return_value.code = expected_code
        mock_urlopen.return_value.headers = {'Content-Type': expected_content_type}
        mock_urlopen.return_value.read.return_value = expected_content_type

        with patch('urllib.urlopen', mock_urlopen):
            url_object = Worker().process_iteration()
            
        return url_object


    def assertStatusView(self, crawl, expected_in_progress, expected_completed):
        # Test that the status view returns the right data
        status_response = self.client.get('/status/%d/' % crawl.id)
        
        in_progress = json.loads(status_response.content)['in_progress']
        completed = json.loads(status_response.content)['completed']
        
        self.assertEqual(in_progress, expected_in_progress)
        self.assertEqual(completed, expected_completed)
        
        
    def assertResultView(self, crawl, expected_image_urls):
        result_response = self.client.get('/result/%d/' % crawl.id)
        
        image_urls = json.loads(result_response.content)['image_urls']
        
        self.assertEqual(len(image_urls), expected_image_urls)
        

    
class TestCrawl(object):
    """Contains utility methods that hide the Django ORM so that it will be
    easier to swap in a different data layer later, if desired.
     
    """
    
    def __init__(self):
        self.crawl_model = Crawl.objects.create()
        
        
    @property
    def id(self):
        return self.crawl_model.id


    def add_url(self, url, depth):
        return Url.objects.create(crawl_id=self.crawl_model.id, url=url, depth=depth)
        
        
    def num_total_urls(self):
        return len(Url.objects.filter(crawl_id=self.crawl_model.id))
        
        
    def url_not_visited(self, url_object):
        return (url_object.content_type is None) and (url_object.visited is None)
            
            
    def url_visited_recently(self, url_object):
        return \
            (url_object.content_type is not None) and \
            (url_object.visited is not None) and \
            ((datetime.datetime.now() - url_object.visited).total_seconds() < 30)
            