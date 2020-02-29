from django.db import models
from datetime import datetime
from django.utils import timezone


# Create your models here.
from django.utils.text import slugify


class Station(models.Model):
    name = models.CharField(max_length=50)
    website_url = models.CharField(max_length=150, default="None")
    stream_url = models.CharField(max_length=150, default="None")
    service_ndj_url = models.CharField(max_length=150, default="None")
    service_ndj_id = models.IntegerField(default=0)
    playlist_sp_url = models.CharField(max_length=100, default="None")
    playlist_yt_url = models.CharField(max_length=100, default="None")
    country = models.ForeignKey('Country', on_delete=models.PROTECT)
    img = models.ImageField(upload_to='stations/', width_field='width', height_field='height', blank=True)
    width = models.IntegerField(editable=False, null=True)
    height = models.IntegerField(editable=False, null=True)
    info = models.TextField(null=True)
    slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

    def _generate_unique_slug(self):
        unique_slug = slugify(self.name)
        num = 1
        while Station.objects.filter(slug=unique_slug).exists():
            slug = '{}-{}'.format(unique_slug, num)
            num += 1
            return slug
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)


class Country(models.Model):
    name = models.CharField(max_length=50)
    short = models.CharField(max_length=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class HistLast(models.Model):
    rds = models.CharField(max_length=150)
    station = models.ForeignKey('Station', on_delete=models.CASCADE)
    listeners = models.IntegerField(default=0)
    date = models.DateTimeField()

    def __str__(self):
        return "{date} - {station} - {text}".format(date=self.date, station=self.station, text=self.rds)


class Artist(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Style(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Label(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Song(models.Model):
    artist = models.ManyToManyField(Artist)
    title = models.CharField(max_length=100)
    name = models.CharField(max_length=150)
    feat = models.ManyToManyField(Artist, related_name="feat")

    clip = models.CharField(max_length=20, default="None")

    sp_uri = models.CharField(max_length=50, default="None")
    sp_prev = models.CharField(max_length=200, default="None")
    sp_pop = models.IntegerField(default=0)

    ds_album = models.CharField(max_length=300, default="None")
    ds_img = models.CharField(max_length=400, default="None")
    ds_thm = models.CharField(max_length=400, default="None")
    ds_country = models.ManyToManyField(Country, verbose_name='countries')
    ds_label = models.ManyToManyField(Label, verbose_name='labels')
    ds_genre = models.ManyToManyField(Genre, verbose_name='genres')
    ds_style = models.ManyToManyField(Style, verbose_name='styles')
    ds_year = models.IntegerField(default=0)

    total_plays = models.IntegerField()
    stations = models.ManyToManyField(Station)
    slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.name

    def ds_genre_f(self):
        return "|".join([p.name for p in self.ds_genre.all()])

    def ds_style_f(self):
        return "|".join([p.name for p in self.ds_style.all()])

    def ds_country_f(self):
        return "|".join([p.name for p in self.ds_country.all()])

    def stations_f(self):
        return "|".join([p.name for p in self.stations.all()])

    def sp_b(self):
        if self.sp_uri != "None":
            return True
        else:
            return False

    def yt_b(self):
        if self.clip != "None":
            return True
        else:
            return False

    def spo(self):
        pio = self.sp_uri.replace("spotify:track:", "")
        return pio

    sp_b.boolean = True
    yt_b.boolean = True

    def emisje(self):
        em = History.objects.filter(song=self).order_by('-date')[:10]
        return em

    def _generate_unique_slug(self):
        unique_slug = slugify(self.name)
        num = 1
        while Song.objects.filter(slug=unique_slug).count() > 0:
            slug = '{}-{}'.format(unique_slug, num)
            num += 1
            unique_slug = slug
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)


class History(models.Model):
    rds = models.CharField(max_length=150)
    station = models.ForeignKey('Station', on_delete=models.CASCADE)
    listeners = models.IntegerField(default=0)
    date = models.DateTimeField()
    song = models.ForeignKey('Song', on_delete=models.CASCADE)

    def __str__(self):
        return "{date} - {station} - {text}".format(date=self.date, station=self.station, text=self.rds)

    def spo(self):
        pio = self.song.sp_uri.replace("spotify:track:", "")
        return pio

    def last(self):
        now = self.date
        return now
