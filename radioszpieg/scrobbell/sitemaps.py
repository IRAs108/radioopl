from django.contrib.sitemaps import Sitemap
from .models import Song


class SongSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9
    limit = 1000

    def items(self):
        return Song.objects.all().order_by('-total_plays')

    def lastmod(self, obj):
        return obj.updated
