from datetime import datetime
from datetime import timedelta

import redis
from django.core.management.base import BaseCommand
from redis import StrictRedis
from scrobbell.models import History, Station, Song


class Command(BaseCommand):
    help = 'Pobieranie informacji o utworach'

    def add_arguments(self, parser):
        parser.add_argument('--test', action='store_true', help='Testowa komenda', )
        parser.add_argument('--get', action='store_true', help='Get last song from stations', )
        parser.add_argument('--add', action='store_true', help='Add song to database from last scrobble', )
        parser.add_argument('--duplicate', action='store_true', help='Testowa komenda', )

    def handle(self, *args, **options):
        rd = redis.Redis(host='localhost', port=6379, db=2)

        if options['test']:
            def ssc(val):
                return val[1]

            rd.flushdb()

            for st in Station.objects.all():
                print(st)
                # qs = History.objects.filter(date__range=["2019-12-09 00:00", "2019-12-15 23:59"], station=st)
                delt = datetime.now() - timedelta(days=30)
                qs = History.objects.filter(date__gte=delt, station=st)
                list1 = []
                for s in qs:
                    song = "m;" + str(st.id) + ";" + str(s.song.id)
                    # print(song)
                    rd.incr(song)

                delt = datetime.now() - timedelta(days=7)
                qs = History.objects.filter(date__gte=delt, station=st)
                for s in qs:
                    song = "w;" + str(st.id) + ";" + str(s.song.id)
                    rd.incr(song)

                # cnt = qs.filter(song=s.song).count()
                # if cnt > 4:
                #    list1 = list1 + [(s.song, cnt)]
                # print(s)
                # print(cnt)
            # list2 = list(set(list1))
            # list2.sort(key=ssc, reverse=True)
            # for ll in list2:
            #     print(ll)

        if options['get']:
            rdt = StrictRedis(host='localhost', port=6379, db=2)

            def ssc(val):
                return val[1]

            # il = Song.objects.count
            list1 = []

            for l in Song.objects.all():
                sng = "m;2;" + str(l.id)
                if rd.get(sng):
                    count = int(rd.get(sng))
                    if count > 10:
                        list1 = list1 + [(l.name, count)]
            list1.sort(key=ssc, reverse=True)
            for ll in list1:
                print(ll)
            rdt.set("top;m;2", list1)
