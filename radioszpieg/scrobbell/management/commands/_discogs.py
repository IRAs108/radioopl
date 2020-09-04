import discogs_client

from .apikey import ds_key, ds_secret, ds_token

d = discogs_client.Client('test_muxrb')
d.set_consumer_key(ds_key, ds_secret)
d = discogs_client.Client('test_muxrb', user_token=ds_token)
me = d.identity()


def get_disc(song):
    data = d.search(song.encode('utf-8'), type='relase')
    if data is None:
        return
    year = 0
    try:
        first = data[0]
    except:
        return
    try:
        if first.title:
            r_album = first.title
    except:
        return
    r_genre = first.genres
    r_style = first.styles
    try:
        r_country = first.country
    except:
        r_country = "None"
    try:
        r_image = first.images[0]['uri']
    except:
        r_image = "None"
    try:
        r_thumb = first.thumb
    except:
        r_thumb = "None"
    try:
        r_labels = first.labels
    except:
        r_labels = "None"
    for yy in data:
        try:
            rok = yy.year
        except:
            rok = 0
        if int(rok) > 1900:
            year = yy.year
            break
    return r_album, r_labels, r_genre, r_style, r_country, r_image, r_thumb, year
