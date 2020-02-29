"""radioszpieg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.decorators.http import require_POST
from scrobbell.views import RadioListView, RadioDetailView, SongDetailView, GenreListView, StyleListView, StyleDetailView, GenreDetailView, LastHist, SimpleEditSongForm, RadioDetailRedirect, SongDetailRedirect
from scrobbell.views import radionow, last_history
from django.conf.urls.static import static
from django.conf import settings

from scrobbell.views import MuxRb, MuxRbAjax, SearchResultsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RadioListView.as_view(), name='station_list'),
    # path('station/<pk>/', RadioDetailView.as_view(), name='station_detail'),
    path('station/<pk>/', RadioDetailRedirect.as_view(), name='station_redirect'),
    path('stacja/<slug>/', RadioDetailView.as_view(), name='station_detail'),
    # path('song/<pk>/', SongDetailView.as_view(), name='song_detail'),
    path('utwor/<slug>', SongDetailView.as_view(), name='song_detail'),
    path('song/<pk>/', SongDetailRedirect.as_view(), name='song_redirect'),
    path('muxrb/', MuxRb, name='muxrb'),
    path('genre/', GenreListView.as_view(), name='genres'),
    path('style/', StyleListView.as_view(), name='styles'),
    path('style/<pk>/', StyleDetailView.as_view(), name='style_detail'),
    path('genre/<pk>/', GenreDetailView.as_view(), name='genre_detail'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('last/', LastHist.as_view(), name='lastsong'),
    path('edit', require_POST(SimpleEditSongForm.as_view()), name='editsong'),
    path('ajax/now/', radionow, name="now"),
    # path('radio/ajax/last/', last_history, name="last"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
