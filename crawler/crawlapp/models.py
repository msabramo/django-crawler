from django.db import models

class Crawl(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	finished = models.DateTimeField(null=True)
	
class Url(models.Model):
	url = models.CharField(max_length=2048, null=False, blank=False)
	crawl = models.ForeignKey(Crawl, related_name='urls')
	depth = models.IntegerField()
	parent = models.ForeignKey('self', related_name='children', null=True)
	created = models.DateTimeField(auto_now_add=True)
	visited = models.DateTimeField(null=True)
	content_type = models.CharField(max_length=128, null=True)
