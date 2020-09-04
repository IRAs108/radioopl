from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from scrobbell.models import Station, HistLast, Song, Artist, History, Genre, Style, Label, Country
from ._get_rds import get_meta_service, get_meta_stream, replacer
from ._yt2mp3_util import get_video_url
from ._discogs import get_disc
from ._spotify import sp_data, add_track_to_playlist
from redis import StrictRedis


class Command(BaseCommand):
    help = 'Pobieranie informacji o utworach'

    def add_arguments(self, parser):
        parser.add_argument('--test', action='store_true', help='Testowa komenda', )
        parser.add_argument('--get', action='store_true', help='Get last song from stations', )
        parser.add_argument('--add', action='store_true', help='Add song to database from last scrobble', )
        parser.add_argument('--duplicate', action='store_true', help='Testowa komenda', )
        parser.add_argument('--get2', action='store_true', help='Get last song from stations', )
        parser.add_argument('--add2', action='store_true', help='Get last song from stations', )
        parser.add_argument('--updatedate', action='store_true', help='Songs update date publish, created', )


    def handle(self, *args, **options):

        if options['get']:
            stations = Station.objects.all()

            for st in stations:
                if st.service_ndj_url != "None":
                    metadata = get_meta_service(st.service_ndj_url, st.service_ndj_id)

                else:
                    metadata = get_meta_stream(st.stream_url)
                metadata_r = replacer(metadata[0])
                if metadata_r is None:
                    continue
                else:
                    metadata_r = metadata_r

                # print(metadata[0])
                last_song = HistLast.objects.filter(station=st).last()
                if last_song is None:
                    last_song = "None"
                    try:
                        last_song = History.objects.filter(station=st).last().rds
                    except:
                        last_song = "ERR"
                    # last_song = replacer(last_song.rds)['rds']

                else:
                    last_song = last_song.rds

                dtm = timezone.now()
                last_song = replacer(last_song)
                # print(metadata_r)
                # print(last_song)
                if metadata_r != last_song:
                    lh = HistLast(rds=metadata[0], station=st, listeners=metadata[1], date=dtm)
                    lh.save()

                """""
                # postproces
                for hist in HistLast.objects.all():
                    # print(hist.rds)
                    rds = replacer(hist.rds)
                    if rds is None:
                        hist.delete()
                        continue
                    if rds['rds'] == History.objects.filter(station=hist.station).last().rds:
                        hist.delete()
                        continue
                    song = Song.objects.filter(name=rds["rds"]).last()
                    if song:
                        total = int(History.objects.filter(song=song).count()) + 1
                        # print(total)
                        song.stations.add(hist.station)
                        song.total_plays = total
                        song.save()

                        lhs = History.objects.filter(station=hist.station).last()
                        if lhs != hist:
                            move = History(rds=rds['rds'], listeners=hist.listeners, station=hist.station,
                                           date=hist.date
                                           , song=song)
                            move.save()
                            hist.delete()
                            
                            """

        if options['add']:
            for hist in HistLast.objects.all():
                # print(hist.rds)
                rds = replacer(hist.rds)
                if rds is None:
                    hist.delete()
                    continue
                try:
                    if rds['rds'] == History.objects.filter(station=hist.station).last().rds:
                        hist.delete()
                        continue
                except:
                    continue
                song = Song.objects.filter(name=rds["rds"]).last()
                if song is None:

                    # GET METADATA FROM SPOTIFY DISCOGS YOUTUBE
                    name = rds['rds']
                    artist = name.split(' - ')[0]
                    title = name.split(' - ')[1]
                    clip = ""
                    clip = get_video_url({"artist_name": artist, "track_name": title})
                    if clip is None:
                        clip = "None"
                    else:
                        clip = clip.replace("https://www.youtube.com/watch?v=", "")

                    disc_style = ["None"]

                    disc_data = get_disc(name)
                    if disc_data is None:
                        disc_alb = "None"
                        disc_label = "None"
                        disc_genre = ["None"]
                        disc_style = ["None"]
                        disc_country = "None"
                        disc_image = "None"
                        disc_thumb = "None"
                        disc_year = 0
                    else:
                        """
                        print("Album: {name}".format(name=disc_data[0]))
                        print("Label: {name}".format(name=disc_data[1]))
                        print("Genre: {name}".format(name=disc_data[2]))
                        print("Style: {name}".format(name=disc_data[3]))
                        print("Country: {name}".format(name=disc_data[4]))
                        print("Image: {name}".format(name=disc_data[5]))
                        print("Thumb: {name}".format(name=disc_data[6]))
                        """
                        disc_alb = disc_data[0]
                        disc_label = disc_data[1]
                        disc_genre = disc_data[2]
                        disc_style = disc_data[3]
                        disc_country = disc_data[4]
                        disc_image = disc_data[5]
                        disc_thumb = disc_data[6]
                        disc_year = disc_data[7]

                    spd = sp_data(name)

                    spd_uri = "None"
                    spd_preview = "None"
                    spd_popularity = 0

                    for i, t in enumerate(spd['tracks']['items']):
                        spd_popularity = int(t['popularity'])
                        spd_preview = t['preview_url']
                        spd_uri = t['uri']

                    if spd_preview is None:
                        spd_preview = "None"

                    # END

                    if spd_uri != "None":
                        add_track_to_playlist(hist.station.playlist_sp_url, spd_uri)
                    # print("Dodano do playlisty Spotify")

                    song = Song(title=rds["title"], name=rds["rds"], clip=clip, sp_uri=spd_uri, sp_prev=spd_preview,
                                sp_pop=spd_popularity, ds_album=disc_alb, ds_img=disc_image, ds_thm=disc_thumb,
                                ds_year=disc_year, total_plays=1)

                    song.save()
                    for art in rds['artist']:
                        s_art = Artist.objects.filter(name=art).last()
                        if s_art is None:
                            s_art = Artist(name=art)
                            s_art.save()
                        song.artist.add(s_art)
                        song.save()

                    sfe = Artist.objects.filter(name=rds["feat"]).last()
                    if sfe is None:
                        sfe = Artist(name=rds["feat"])
                        sfe.save()
                    song.feat.add(sfe)
                    song.save()

                    country = Country.objects.filter(name=disc_country).last()
                    if country is None:
                        country = Country(name=disc_country)
                        country.save()
                    song.ds_country.add(country)
                    song.save()

                    for gnr in disc_genre:
                        genre = Genre.objects.filter(name=gnr).last()
                        if genre is None:
                            genre = Genre(name=gnr)
                            genre.save()
                        song.ds_genre.add(genre)
                        song.save()
                    try:
                        for gnr in disc_style:
                            style = Style.objects.filter(name=gnr).last()
                            if style is None:
                                style = Style(name=gnr)
                                style.save()
                            song.ds_style.add(style)
                            song.save()
                    except:
                        print("Error")
                    label = Label.objects.filter(name=disc_label).last()
                    if label is None:
                        label = Label(name=disc_label)
                        label.save()
                    song.ds_label.add(label)
                    song.save()

                # print(song)
                total = int(History.objects.filter(song=song).count()) + 1
                # print(total)
                song.stations.add(hist.station)
                song.total_plays = total
                song.save()

                lhs = History.objects.filter(station=hist.station).last()
                if lhs != hist:
                    move = History(rds=rds['rds'], listeners=hist.listeners, station=hist.station, date=hist.date
                                   , song=song)
                    move.save()
                    hist.delete()

        if options['test']:
            print("test")
            nr = 0
            file = open("historia.csv", 'r')
            for line in file:
                nr = nr + 1
                if nr < 66945:
                    continue
                if nr > 66838:
                    break
                line = line.split('","')
                # add some custom validation\parsing for some of the fields
                radio = line[2]
                data = line[1]
                try:
                    rds = line[3]
                except:
                    continue
                try:
                    listeners = line[5]
                except:
                    continue
                radio = radio.replace("\"", "")
                data = data.replace("\"", "")
                rds = rds.replace("\"", "")
                listeners = int(listeners.replace("\"", ""))

                data = timezone.template_localtime(data, 'Europe/Warsaw')
                rd = Station.objects.filter(name=radio).last()

                if rd is None:
                    continue

                his = HistLast(date=data, rds=rds, station=rd, listeners=listeners)
                print(his)
                his.save()

        if options['duplicate']:
            print("Duplikaty")
            for t in History.objects.all():

                ost = (t.rds[:-1])
                for tt in ost:
                    if tt == "?":
                        print(t.rds)
                        p = HistLast(rds=t.rds, station=t.station, listeners=t.listeners, date=t.date)
                        p.save()
                        try:
                            t.delete()
                        except:
                            print("ERR")
            las_s = ""
            for st in Station.objects.all():

                for t in History.objects.filter(station=st).order_by('date'):
                    if t.rds == las_s:
                        print(t)
                        t.delete()
                    las_s = t.rds

        if options['get2']:
            # print('Test')
            rd = StrictRedis(host='localhost', port=6379, db=1)
            rdn = StrictRedis(host='localhost', port=6379, db=1)
            stations = Station.objects.all()

            for st in stations:
                print(st)
                if st.service_ndj_url != "None":
                    metadata = get_meta_service(st.service_ndj_url, st.service_ndj_id)

                else:
                    metadata = get_meta_stream(st.stream_url)

                # print(st)
                klucz = "station:" + str(st.id)
                czas = str(timezone.now())
                wartosc = str(czas) + "|" + metadata[0] + "|" + str(metadata[1])
                # print(wartosc)

                rd.lpush(klucz, wartosc)
                rd.close()
                try:
                    now = str(replacer(metadata[0])['rds'])
                except:
                    now = "NIC NIE GRA"
                klucz = klucz+":n"
                rdn.set(klucz, now, 200)

                """""
                mee = dat + ";" + str(metadata[0]) + ";" + str(metadata[1])
                try:
                    last = str(rd.rpop(nrs, 3).encode("utf-8"))
                    print(last)
                except:
                    last = "None"
                    rd.rpush(nrs, mee)
                    continue
                print(last)
                # rd.rpush(nrs, mee)

                if last != mee.split(";")[1]:
                    rd.rpush(nrs, mee)
                    print("Dodano!")
                print(metadata)
                """
        if options['add2']:
            # print('Test')
            rd = StrictRedis(host='localhost', port=6379, db=1)
            rdc = StrictRedis(host='localhost', port=6379, db=2)
            for st in Station.objects.all():
                klucz = "station:" + str(st.id)
                try:
                    last_song_h = History.objects.filter(station=st).last()
                    last = last_song_h.rds
                except:
                    continue

                ln = rd.llen(klucz)
                for i in range(ln):
                    try:
                        nowrds = rd.rpop(klucz).decode("utf-8")
                        nowrds = str(nowrds).split("|")
                        now = replacer(nowrds[1])
                        nrd = now['rds']
                    except:
                        continue
                    # print(last)
                    # print(nrd)
                    if last == nrd:
                        continue
                    else:
                        # print(now)
                        date_n = nowrds[0]
                        listeners_n = nowrds[2]
                        last = now['rds']
                        try:
                            song = Song.objects.filter(name=now["rds"]).last()
                        except:
                            continue
                        if song is None:

                            # GET METADATA FROM SPOTIFY DISCOGS YOUTUBE
                            name = now['rds']
                            artist = name.split(' - ')[0]
                            title = name.split(' - ')[1]
                            clip = ""
                            clip = get_video_url({"artist_name": artist, "track_name": title})
                            if clip is None:
                                clip = "None"
                            else:
                                clip = clip.replace("https://www.youtube.com/watch?v=", "")

                            disc_style = ["None"]

                            disc_data = get_disc(name)
                            if disc_data is None:
                                disc_alb = "None"
                                disc_label = "None"
                                disc_genre = ["None"]
                                disc_style = ["None"]
                                disc_country = "None"
                                disc_image = "None"
                                disc_thumb = "None"
                                disc_year = 0
                            else:
                                """
                                print("Album: {name}".format(name=disc_data[0]))
                                print("Label: {name}".format(name=disc_data[1]))
                                print("Genre: {name}".format(name=disc_data[2]))
                                print("Style: {name}".format(name=disc_data[3]))
                                print("Country: {name}".format(name=disc_data[4]))
                                print("Image: {name}".format(name=disc_data[5]))
                                print("Thumb: {name}".format(name=disc_data[6]))
                                """
                                disc_alb = disc_data[0]
                                disc_label = disc_data[1]
                                disc_genre = disc_data[2]
                                disc_style = disc_data[3]
                                disc_country = disc_data[4]
                                disc_image = disc_data[5]
                                disc_thumb = disc_data[6]
                                disc_year = disc_data[7]

                            spd = sp_data(name)

                            spd_uri = "None"
                            spd_preview = "None"
                            spd_popularity = 0

                            for i, t in enumerate(spd['tracks']['items']):
                                spd_popularity = int(t['popularity'])
                                spd_preview = t['preview_url']
                                spd_uri = t['uri']

                            if spd_preview is None:
                                spd_preview = "None"

                            # END

                            if spd_uri != "None":
                                add_track_to_playlist(st.playlist_sp_url, spd_uri)
                            # print("Dodano do playlisty Spotify")

                            song = Song(title=now["title"], name=now["rds"], clip=clip, sp_uri=spd_uri,
                                        sp_prev=spd_preview,
                                        sp_pop=spd_popularity, ds_album=disc_alb, ds_img=disc_image, ds_thm=disc_thumb,
                                        ds_year=disc_year, total_plays=1)

                            song.save()
                            for art in now['artist']:
                                s_art = Artist.objects.filter(name=art).last()
                                if s_art is None:
                                    s_art = Artist(name=art)
                                    s_art.save()
                                song.artist.add(s_art)
                                song.save()

                            sfe = Artist.objects.filter(name=now["feat"]).last()
                            if sfe is None:
                                sfe = Artist(name=now["feat"])
                                sfe.save()
                            song.feat.add(sfe)
                            song.save()

                            country = Country.objects.filter(name=disc_country).last()
                            if country is None:
                                country = Country(name=disc_country)
                                country.save()
                            song.ds_country.add(country)
                            song.save()

                            for gnr in disc_genre:
                                genre = Genre.objects.filter(name=gnr).last()
                                if genre is None:
                                    genre = Genre(name=gnr)
                                    genre.save()
                                song.ds_genre.add(genre)
                                song.save()
                            try:
                                for gnr in disc_style:
                                    style = Style.objects.filter(name=gnr).last()
                                    if style is None:
                                        style = Style(name=gnr)
                                        style.save()
                                    song.ds_style.add(style)
                                    song.save()
                            except:
                                print("Error")
                            label = Label.objects.filter(name=disc_label).last()
                            if label is None:
                                label = Label(name=disc_label)
                                label.save()
                            song.ds_label.add(label)
                            song.save()

                        # print(song)
                        total = int(History.objects.filter(song=song).count()) + 1
                        # print(total)
                        song.stations.add(st)
                        song.total_plays = total
                        song.save()

                        # lhs = History.objects.filter(station=hist.station).last()
                        # if lhs != hist:
                        move = History(rds=now['rds'], listeners=listeners_n, station=st,
                                       date=date_n
                                       , song=song)
                        move.save()

                        songm = "m;" + str(st.id) + ";" + str(song.id)
                        songt = "w;" + str(st.id) + ";" + str(song.id)
                        # print(songm)
                        rdc.incr(songm)
                        rdc.incr(songt)

        if options['updatedate']:
            historia = Song.objects.all().order_by('-pk')
            for hist in historia:
                print(hist.pk)
                lst = History.objects.filter(song=hist).last()
                frst = History.objects.filter(song=hist).first()
                try:
                    hist.created = frst.date
                    hist.updated = lst.date
                    hist.save()
                except:
                    hist.delete()
