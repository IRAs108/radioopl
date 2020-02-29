from __future__ import print_function

import json
import re
import struct
import urllib
import time
import sys
import urllib.request as urllib2
import requests

def get_meta_stream(url):
    encoding = 'latin1'
    request = urllib2.Request(url, headers={'Icy-MetaData': 1})
    response = urllib2.urlopen(request)
    time.sleep(1)
    meta_il = int(response.headers['icy-metaint'])
    rds = ""
    ll = 0
    while rds == "":
        ll = ll + 1
        if ll > 10:
            break
        for _ in range(10):
            response.read(meta_il)
            metadata_length = struct.unpack('B', response.read(1))[0] * 16
            metadata = response.read(metadata_length).rstrip(b'\0')
            m = re.search(br"StreamTitle='([^']*)';", metadata)
            if m:
                title = m.group(1)
                title_dec = title.decode(encoding, errors='replace')
                if title_dec == "STOP_AD_BREAK":
                    time.sleep(5)
                    continue
                if title:
                    break
        else:
            rds = 'no title found'
        try:
            rds = title.decode(encoding, errors='replace')
            rds = rds.replace("; ", " & ")
        except:
            rds = "ERROR"

    return rds, 0


def get_meta_service(url, service_id):
    #print(url, service_id)
    try:
        #fp = urllib.request.urlopen(url)
        #dane = fp.read()
        #dane = dane.decode('utf8')
        #fp.close()
        headers = {
    'User-Agent': 'radioo.pl v. 0.1',
    'From': 'ireneusz@pocza.fm'  # This is another valid field
}
        r = requests.get(url, headers=headers)
        dane = r.text
        r.close
        # print(dane)
        if service_id == -1:
            #dane = dane.replace("\\/", "&")
            # dane = dane.replace("\\u0", "&#x")
            # dane.replace("\\\\", "\\")
            # dane = dane.encode('latin1').decode('utf8')
            #dane = dane.split('"status":-1')[1]
            artist = ""
            title = ""
            json_data = json.loads(re.sub(r'([a-zA-Z_0-9\.]*\()|(\);?$)','',dane))
            if json_data[1]['status'] == -1:
                idx = 0
            else:
                idx = 1
            if json_data[idx]['status'] == 0:
                for art in json_data[idx]['artists']:
                    artist = artist + " & " + art['name']
            #artist = dane.split('"name":"')[2].split('"')[0]
            #title = dane.split('"name":"')[1].split('",')[0]
                title = json_data[idx]['name'] 
            if title == "":
                return "None", 0
            artist = artist[3:]
            rds = artist + " - " + title
            listeners = 0
        elif service_id == -2:
            artist = dane.split('"artist":"')[1].split('","')[0]
            title = dane.split('"title":"')[1].split('","')[0]
            artist = artist.replace('\\/', '&')
            if title.lower == 'meloradio' or title.lower == 'radiozet':
                rds = 'None'
            else:
                rds = artist + " - " + title
            listeners = 0

        elif service_id == -3:
            dane = dane[1:-1]
            dane_json = json.loads(dane)
            artist = dane_json['artist_name']
            title = dane_json['song_title']
            rds = dane_json['artist_name'] + " - " + dane_json['song_title']
            listeners = 0
        elif service_id == -4:
            dane_json = json.loads(dane)
            rds = dane_json['artist'] + " - " + dane_json['song']
            listeners = 0
        elif service_id == -5: #muzo
            dane_json = json.loads(dane)
            print(dane_json)
            rds = dane_json['emisja'][0]['wykonawca'] + " - " + dane_json['emisja'][0]['tytul']
            # print(rds)
            rds = rds.replace(' - Muzo.Fm', 'None')
            listeners = 0
        else:
            dane_json = json.loads(dane)
            rds = dane_json[service_id]['metadata']
            listeners = int(dane_json[service_id]['recipients_count'])
    except:
        rds = "Error"
        listeners = 0

    return rds, listeners


def replacer(rds):
    replacing = [("  ", " - "), ("  ", " "), ("&#x142;", "ł"), ("&#x15B;", "ś"), ("&#x119;", "ę"), ("&#xF3;", "ó"),
                 ("\\u0142", "ł"), ("\\u015b", "ś"), ("\\u0119", "ę"), ("\\u00f3", "ó"), ("\\u0141", "Ł"),
                 ("\\u0107", "ć"), ("\\u0104", "Ą"), ("\\u0d3", "Ó"), ("\\u015a", "Ś"), ("\\u017c", "ż"),
                 ("\\u0105", "ą"), ("\\u0144", "ń"), ("\\u017b", "Ż"), ("\\u017a", "ź"), ("\\u0118", "Ę"),
                 ("\\u0104", "Ą"), ("\\u0106", "Ć"), ("\\u015a", "Ś"),
                 ("&#x141;", "Ł"), ("&#x107;", "ć"), ('H&#xE4;', 'ä'), ('&#x104', 'Ą'), ('&#xD3;', 'Ó'),
                 ("&#x15A;", "Ś"), ("&#x17C;", "ż"), ("&#x105;", "ą"), ("&#x144;", "ń"), ("&#x17B;", "Ż"),
                 ("&#x17A;", "ź"), ("&#x118;", "Ę"), ("&#x104;", "Ą"),
                 ("&#x141;", "Ł"), ("&#x106;", "Ć"), ("  ", " - "), ("\r", ""), ("\\n", ""), ("&#xD;", ""),
                 ("Off Radio Kraków - ", ""), ("DOBRA MUZYKA I WSZYSTKO GRA - Meloradio", ""),
                 ("TERAZ: ", ""), ("TERAZ GRAMY ", ""), ("Radio Zachod - ", ""), ("TERAZ NA ANTENIE ", ""),
                 ("RADIO - RADIO", "NIEMA"), ("RADIOZET - ", ""), ("VOX FM - ", ""),
                 ("H?Nni", "Hänni"), ("Mi?D", "Miód"), ("h?nni", "Hänni"), ("mi?d", "Miód"),
                 ("G?Nther", "Günther"), ("St?L", "Stół"), ("Canci?N", "Canción"), ("G?Raleczko", "Góraleczko"),
                 ("P?Lnocy", "Północy"), ("Kt?Rych", "Których"), ("Cl?Udia", "Cláudia"), ("R?Zowe", "Różowe"),
                 ("Um?W", "UmóW"), ("Kr?L", "Król"), ("Tw?J", "Twój"), ("D?Ja", "Déjà"), ("R?Że", "Róże"),
                 ("Canci?N", "Cancion"), ("Zr?Bmy", "Zróbmy"), ("Aserej?", "Aserejé"),
                 ("M?W", "Mów"), ("Studni?Wka", "Studniówka"), ("M?Wi", "Mówi"), ("Perd?N", "Perdón"),
                 ("Kr?Tka", "Krótka"), ("G?ry", "Góry"), ("Pszcz?Lka", "Pszczółka"),
                 ("Tr?J", "Trój"), ("M?J", "Mój"), ("G?Re", "Górę"), ("R?Ża", "Róża"), ("R?Że", "Róże"),
                 ("P?Jde", "Pójde"),
                 ("&#x2019;", "’"), ("&#xe9;", "é"), ("&#X2019;", "’"), ("&#Xe9;", "é"),
                 ("G?RNIAK", "GÓRNIAK"), ("G?rniak", "Górniak"), ("Mon?E", "Monáe"), ("Zawr?", "Zawró"), ("Zr?", "Zró"),
                 ("Kr?L", "Król"), ("P?Lnocy", "Północy"), ("St?L", "Stół"), ("Tw?J", "Twój"), ("R?Za", "Róża"),
                 ("RADIOZET - RADIO ZET I JUZ", "None"), (" - MELORADIO", "None"), ("VOX FM - ", "None")
                 ]
    rds2 = ""
    for s in replacing:
        rds = rds.replace(s[0], s[1])

    splitting = " - "
    pattern = re.compile("[Ff][Ee][Aa][Tt]?.")

    if len(rds.split(splitting)) != 2:
        return None

    rds2 = rds

    if pattern.search(rds):
        artist_feat_s = str(pattern.search(rds).group(0))
        artist_feat = rds.split(artist_feat_s)[1]
        artist_feat = artist_feat.split(" - ")[0]
        replace = " " + artist_feat_s + artist_feat
        rds = rds.replace(replace, "")
    else:
        artist_feat = "None"

    if artist_feat[0] == " ":
        artist_feat = artist_feat[1:]

    rds_s = rds.split(splitting)
    # print(rds_s)
    if len(rds_s) == 2:
        artist = rds_s[0].upper()
        title = rds_s[1].title()
    else:
        return None

    if artist.count(" & ") > 0:
        artists = artist.split(" & ")

    else:
        if artist.count("; ") > 0:
            artists = artist.split("; ")
        else:
            artists = [artist]
    if title[-1:] == " ":
        title = title[:-1]

    rds = artist + " - " + title

    ret_data = {"artist": artists, "title": title, "feat": artist_feat, "rds": rds, "old": rds2}

    return ret_data
