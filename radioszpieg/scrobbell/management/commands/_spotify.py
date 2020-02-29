#!/usr/bin/env python

# coding: utf-8

import spotipy
from spotipy import util
from .apikey import client_id, client_secret

from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id=client_id,
                                                      client_secret=client_secret)


def sp_data(song):
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    results = sp.search(q=song, type='artist,track', limit=1)
    return results


def add_track_to_playlist(playlist_id, track):
    # print(track)
    username = '1167712682'
    # playlist_id = '5pRCGZzmsPT5adjfuW39SZ'
    # track = 'spotify:track:18lq8FwQ94jlSk95PTM7Mr'
    if playlist_id != 'None' and track != "NULL":

        track_ids = [track]
        # print (playlist_id)
        # print (track_ids)
        scope = 'playlist-modify-public'
        token = util.prompt_for_user_token(username, scope)
        xa = 0
        xb = 0

        #client_credentials_manager=client_credentials_managersp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        if token:
            sp = spotipy.Spotify(auth=token)
            sp.trace = False

            # playlist = sp.user_playlist_tracks(username, playlist_id, fields='items(track(uri))')

            # results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
            # for l in playlist['items']:
                # print(l['track']['uri'])
            #     xa = xa + 1

            #     if l['track']['uri'] == track_ids[0]:
            #       xb = 1

            # if xb == 1:
            results = sp.user_playlist_add_tracks(username, playlist_id, track_ids)
            # print(results)


        else:
            print("Can't get token for", username)
        return
