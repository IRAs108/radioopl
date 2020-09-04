from django.contrib import admin
from .models import Country, Station, HistLast, Artist, Song, History, Genre, Style, Label
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Register your models here.


class HistoryResource(resources.ModelResource):
    class Meta:
        model = History


class CountryAdmin(admin.ModelAdmin):
    search_fields = ['name', 'short']
    ordering = ['name']
    list_display = ['name', 'short']


class StationAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'country', 'website_url']


class HistoryAdmin(ImportExportModelAdmin):
    search_fields = ['station__name', 'rds']
    list_display = ['date', 'station', 'rds', 'listeners']
    list_filter = ['station__name', 'date']
    date_hierarchy = 'date'
    resource_class = HistoryResource


class StationResource(resources.ModelResource):
    class Meta:
        model = Station


class SongResource(resources.ModelResource):
    class Meta:
        model = Song


class CountryResource(resources.ModelResource):
    class Meta:
        model = Country


class CountryResource(resources.ModelResource):
    class Meta:
        model = Country


class ArtistResource(resources.ModelResource):
    class Meta:
        model = Artist


class GenreResource(resources.ModelResource):
    class Meta:
        model = Genre


class StyleResource(resources.ModelResource):
    class Meta:
        model = Style


class LabelResource(resources.ModelResource):
    class Meta:
        model = Label


class CountryAdmin(ImportExportModelAdmin):
    resource_class = CountryResource


class GenreAdmin(ImportExportModelAdmin):
    resource_class = GenreResource


class StyleAdmin(ImportExportModelAdmin):
    resource_class = StyleResource


class LabelAdmin(ImportExportModelAdmin):
    resource_class = LabelResource


class ArtistAdmin(ImportExportModelAdmin):
    resource_class = ArtistResource


class StationAdmin(ImportExportModelAdmin):
    resource_class = StationResource


class SongAdmin(admin.ModelAdmin):
    search_fields = ['name', 'ds_genre__name', 'ds_country__name', 'ds_style__name', 'ds_year']
    list_display = ['name', 'ds_album', 'ds_year', 'ds_genre_f', 'ds_style_f', 'ds_country_f', 'sp_pop', 'sp_b', 'yt_b',
                    'total_plays', 'stations_f']
    list_filter = ['stations__name', 'ds_year', 'ds_genre__name', 'ds_style__name', 'ds_country__name']
    list_editable = ['ds_year']


class SongAdmin(ImportExportModelAdmin):
    resource_class = SongResource


class LastHistAdmin(admin.ModelAdmin):
    search_fields = ['rds']
    list_display = ['date', 'station', 'rds', 'listeners']
    list_filter = ['station']


admin.site.register(Country, CountryAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(HistLast, LastHistAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Style, StyleAdmin)
admin.site.register(Label, LabelAdmin)
admin.site.register(History, HistoryAdmin)
