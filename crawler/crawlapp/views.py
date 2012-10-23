import json

from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from crawlapp.models import Crawl, Url


@csrf_exempt
@require_http_methods(["POST"])
def crawl(request):
    crawl = Crawl.objects.create()
    
    print('crawl: request.body = %r' % request.body)
    
    for url in request.body.splitlines():
        url_object = Url.objects.create(url=url, depth=0, crawl=crawl)
    
    json_response = json.dumps({
        'crawl_id': crawl.id})
        
    return HttpResponse(json_response + '\n', content_type='application/json')


def status(request, crawl_id):
    in_progress_url_objects = Url.objects.filter(
        crawl_id=crawl_id)
    completed_url_objects = Url.objects.filter(
        crawl_id=crawl_id,
        visited__isnull=False)
        
    json_response = json.dumps({
        'crawl_id': crawl_id,
        'in_progress': len(in_progress_url_objects),
        'completed': len(completed_url_objects)})
    
    return HttpResponse(json_response + '\n', content_type='application/json')
    
    
def result(request, crawl_id):
    image_objects = Url.objects.filter(
        crawl_id=crawl_id,
        content_type__in=('image/png', 'image/gif', 'image/jpeg'))
    image_urls = [image_object.url for image_object in image_objects]
        
    json_response = json.dumps({'crawl_id': crawl_id, 'image_urls': image_urls})
    
    return HttpResponse(json_response + '\n', content_type='application/json')