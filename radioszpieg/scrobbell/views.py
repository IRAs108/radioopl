import pytz
from django.core import serializers
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, View, FormView, RedirectView
from .models import Station, History, Song, Genre, Style
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import redis
from random import shuffle
from .forms import SimpleEditSong
from datetime import datetime
from django.utils import timezone
from datetime import timedelta

rd = redis.Redis(host='localhost', port=6379, db=2)
nw = redis.Redis(host='localhost', port=6379, db=1)


class GenreListView(ListView):
    model = Genre
    ordering = ['name']


class StyleListView(ListView):
    model = Style
    ordering = ['name']


class StyleDetailView(DetailView):
    model = Style

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        songs = Song.objects.all().filter(ds_style__in=[kwargs['object']]).order_by('-total_plays')[:300]
        context['songs'] = songs
        return context


class GenreDetailView(DetailView):
    model = Genre

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        songs = Song.objects.all().filter(ds_genre__in=[kwargs['object']]).order_by('-total_plays')[:300]
        context['songs'] = songs
        return context


class RadioListView(ListView):
    model = Station


class RadioDetailRedirect(RedirectView):
    def get_redirect_url(self, pk):
        station = Station.objects.get(pk=pk)
        slug = station.slug
        return reverse('station_detail', args=[slug])


class RadioDetailView(DetailView):
    model = Station
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        krr = []
        krrt = []
        # query = self.request.GET.get('st')
        # st = History.objects.all().filter(station=query).order_by('-date')
        context = super().get_context_data(**kwargs)
        hist = History.objects.all().filter(station=kwargs['object']).order_by('-date')[:40]
        # page = self.GET.get('page')
        # paginator = Paginator(hist, 10)
        # page = 1
        # context_object_name = 'history'
        # paginate_by = 10
        # template_name = 'scrobbel/station_detail.html'
        # context['last_hist'] = hist

        for hh in hist:
            try:
                cnt = int(rd.get("m;" + str(kwargs['object'].id) + ";" + str(hh.song.id)))
            except:
                cnt = 0
            krr.append(cnt)
        for hh in hist:
            try:
                cnt = int(rd.get("w;" + str(kwargs['object'].id) + ";" + str(hh.song.id)))
            except:
                cnt = 0
            krrt.append(cnt)
        zipped = zip(hist, krr, krrt)
        context['last_hist'] = zipped
        context['historia'] = hist
        context['now'] = str(nw.get("station:" + str(kwargs['object'].id) + ":n").decode("utf-8"))

        toplist = Song.objects.filter(stations=kwargs['object']).order_by('-total_plays')[:20]
        newsong = Song.objects.filter(stations=kwargs['object']).order_by('-pk')[:20]
        uniquesong = Song.objects.annotate(stn=Count('stations')).filter(stations=kwargs['object']).filter(stn=1).order_by('-total_plays')[:20]
        context['toplist'] = toplist
        context['newsong'] = newsong
        context['unique'] = uniquesong

        return context


def MuxRb(request):
    stations = Station.objects.all()[:3]
    return render(request, 'scrobbell/muxrb.html', {'stations': stations})


def MuxRbAjax(request):
    stations = Station.objects.all()[:3]
    return render(request, 'scrobbell/test.html', {'stations': stations})


class SongDetailView(DetailView):
    model = Song
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        style = kwargs['object'].ds_style.all()
        year = kwargs['object'].ds_year
        similar = Song.objects.all().filter(ds_style__in=style, ds_year__gte=year - 3, ds_year__lte=year + 1).order_by(
            '-total_plays')[:7]
        # similar = similar.order_by('?')[:5]
        context['similar'] = similar
        context['form'] = SimpleEditSong(
            initial={'id': kwargs['object'].id, 'clip': kwargs['object'].clip, 'spo_uri': kwargs['object'].sp_uri,
                     'rok': kwargs['object'].ds_year
                     })
        # context['data'] = {'Python': 52.9, 'Jython': 1.6, 'Iron Python': 27.7}
        # context['line_data'] = list(enumerate(range(1, 20)))
        rrr = {}
        for st in Station.objects.all():
            ile = History.objects.all().filter(station=st, song=kwargs['object']).count()
            if ile > 0:
                rrr[st.name] = ile
        context['data'] = rrr
        ll = []
        for dayy in range(90, 1, -1):
            ile = History.objects.all().filter(song=kwargs['object'], date__gte=datetime.now() - timedelta(days=dayy),
                                               date__lte=datetime.now() - timedelta(days=dayy - 1)).count()
            ll.append((dayy, ile))
            # ll.reverse()
        context['line_data'] = ll

        return context


class SongDetailRedirect(RedirectView):
    def get_redirect_url(self, pk):
        song = Song.objects.get(pk=pk)
        slug = song.slug
        return reverse('song_detail', args=[slug])


class SearchResultsView(ListView):
    model = Song
    ordering = ['-total_plays']
    template_name = 'scrobbell/search_results.html'
    paginate_by = 20

    def get_queryset(self):  # new
        query = self.request.GET.get('q')
        if query == "":
            object_list = Song.objects.all().order_by('-total_plays')[:500]
        elif query == "nowosci":
            object_list = Song.objects.all().order_by('-id')[:500]
        else:
            object_list = Song.objects.filter(name__icontains=query).order_by('-total_plays')
        return object_list


class LastHist(ListView):
    queryset = History.objects.all().filter(station=1).order_by('-date')
    context_object_name = 'lastsong'
    paginate_by = 20
    template_name = 'scrobbel/lastsong.html'

    def get_queryset(self):  # new
        query = self.request.GET.get('st')
        st = History.objects.all().filter(station=query).order_by('-date')
        return st

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('st')
        context = super().get_context_data(**kwargs)
        context['station'] = Station.objects.get(pk=query)
        return context


def history_list(request):
    station = request.GET.get('st')
    history = History.objects.all().filter(station=station).order_by('-date')
    paginator = Paginator(history, 20)
    page = request.GET.get('page')
    try:
        history = paginator.page(page)
    except PageNotAnInteger:

        history = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        history = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'scrobbell/last_ajax.html',
                      {'section': 'rds', 'rds': history})
    return render(request,
                  'scrobbell/last.html',
                  {'section': 'rds', 'rds': history, 'station': station})


def station_detail(request):
    station = request.GET.get('st')
    history = History.objects.all().filter(station=station).order_by('-date')
    paginator = Paginator(history, 20)
    page = request.GET.get('page')
    try:
        history = paginator.page(page)
    except PageNotAnInteger:

        history = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        history = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'scrobbell/station_detail_ajax.html',
                      {'section': 'rds', 'rds': history})


class SimpleEditSongForm(FormView):
    form_class = SimpleEditSong
    success_url = 'search/?q=nowosci'
    template_name = 'scrobbell/editsong.html'

    def form_valid(self, form):
        id = form.cleaned_data['id']
        yt = form.cleaned_data['clip']
        yt = yt.replace('https://www.youtube.com/watch?v=', '')
        sp = form.cleaned_data['spo_uri']
        year = form.cleaned_data['rok']
        remove_spotify = form.cleaned_data['us_sp']
        song = Song.objects.filter(pk=id).last()
        if remove_spotify:
            sp = "None"
            song.sp_prev = "None"
            song.sp_pop = 0
        song.sp_uri = sp
        song.clip = yt
        song.ds_year = year
        song.save()
        print(remove_spotify)
        return super(SimpleEditSongForm, self).form_valid(form)


def radionow(request):
    station = request.GET.get('st')
    position = request.GET.get('p')
    if position:
        h = History.objects.all().filter(station=station).order_by('-date')[int(position)]
        rds = h.rds
        song = h.song
        # d = h.date.tz('Europe/Warsaw')
        d = timezone.localtime(h.date, pytz.timezone('Europe/Warsaw'))
    else:
        rds = str(nw.get("station:" + station + ":n").decode('utf8'))
        song = Song.objects.all().filter(name=rds).first()
        d = datetime.now()

    if song:
        sp = song.sp_uri
        youtube = song.clip
        prev = song.sp_prev
        year = song.ds_year
        img = song.ds_img
    else:
        sp = "None"
        youtube = "None"
        prev = "None"
        year = 0
        d = datetime.now()
        img = "None"
    artit = rds.split(" - ")
    try:
        title = artit[1]
    except:
        title = "None"
    name = Station.objects.filter(pk=station).last().name
    if d.minute < 10:
        minuty = "0" + str(d.minute)
    else:
        minuty = str(d.minute)

    time = str(d.hour) + ":" + minuty
    now = {"date": d, "time": time, "rds": rds, "name": name, "spotify": sp.replace("spotify:track:", ""),
           "youtube": youtube, "preview": prev,
           "year": year, "img": img, "artist": artit[0], "title": title}
    return JsonResponse(now)


def last_history(request):
    station = request.GET.get('st')
    history = History.objects.all().filter(station=station).order_by('-date')[:100]
    qs_json = serializers.serialize('json', history)
    jsonr = {"date": 1, "rds": "test"}
    return HttpResponse(qs_json, content_type='application/json')
