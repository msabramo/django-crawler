"""
Management command for starting crawler worker processes
"""

from __future__ import with_statement
import logging
import urllib

from django.core.management.base import BaseCommand
from crawlapp.models import Crawl, Url
from crawlapp.worker import Worker


logging.basicConfig(level=logging.DEBUG)


class Command(BaseCommand):
    help = """Launch crawler worker process"""

    def handle(self, *args, **options):
        print("This is a worker process.")
        worker = Worker()
        worker.process()
        """
        args = args or [CLASSIFIERS_URL]

        cnt = 0
        for location in args:
            print "Loading %s" % location
            lines = self._get_lines(location)
            for name in lines:
                c, created = Classifier.objects.get_or_create(name=name)
                if created:
                    c.save()
                    cnt += 1

        print "Added %s new classifiers from %s source(s)" % (cnt, len(args))
        """

    def _get_lines(self, location):
        """Return a list of lines for a lication that can be a file or
        a url. If path/url doesn't exist, returns an empty list"""
        try: # This is dirty, but OK I think. both net and file ops raise IOE
            if location.startswith(("http://", "https://")):
                fp = urllib.urlopen(location)
                return [e.strip() for e in fp.read().split('\n')
                        if e and not e.isspace()]
            else:
                fp = open(location)
                return [e.strip() for e in fp.readlines()
                        if e and not e.isspace()]
        except IOError:
            print "Couldn't load %s" % location
            return []
