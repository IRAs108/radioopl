from django.contrib import admin
from .models import Country, Station, HistLast, Artist, Song, History, Genre


# Register your models here.

class CountryAdmin(admin.ModelAdmin):
    search_fields = ['name', 'short']
    ordering = ['name']
    list_display = ['name', 'short']


class StationAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'country', 'website_url']


class HistoryAdmin(admin.ModelAdmin):
    search_fields = ['station__name', 'rds']
    list_display = ['date', 'station', 'rds', 'listeners']
    list_filter = ['station__name', 'date']
    date_hierarchy = 'date'


class SongAdmin(admin.ModelAdmin):
    search_fields = ['name', 'ds_genre__name', 'ds_country__name', 'ds_style__name', 'ds_year']
    list_display = ['name', 'ds_album', 'ds_year', 'ds_genre_f', 'ds_style_f', 'ds_country_f', 'sp_pop', 'sp_b', 'yt_b',
                    'total_plays', 'stations_f']
    list_filter = ['stations__name', 'ds_year', 'ds_genre__name', 'ds_style__name', 'ds_country__name']
    list_editable = ['ds_year']


class LastHistAdmin(admin.ModelAdmin):
    search_fields = ['rds']
    list_display = ['date', 'station', 'rds', 'listeners']
    list_filter = ['station']


admin.site.register(Country, CountryAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(HistLast, LastHistAdmin)
admin.site.register(Artist)
admin.site.register(Song, SongAdmin)
admin.site.register(History, HistoryAdmin)
