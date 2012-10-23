from django.contrib import admin
from crawlapp.models import Crawl, Url

class CrawlAdmin(admin.ModelAdmin):
    list_display = ['id', 'created', 'finished']
    
class UrlAdmin(admin.ModelAdmin):
    list_display = ['url', 'crawl_id', 'created', 'visited', 'content_type']
    
    def crawl_id(self, obj):
        return obj.crawl.id

admin.site.register(Crawl, CrawlAdmin)
admin.site.register(Url, UrlAdmin)
