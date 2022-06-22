import json

import Artist
import datetime


class Track:
    def __init__(self, track):
        track_outside = track
        track = track['track']
        self.name = track['name']
        self.id = track['id']
        self.url = track['external_urls']['spotify']
        self.artists = []
        for artist in track['artists']:
            self.artists.append(Artist.Artist(artist))
        self.popularity = track['popularity']
        self.length = track['duration_ms']
        self.album = track['album']['name']
        self.art_urls = track['album']['images']
        self.release = release_to_date(track['album']['release_date'], track['album']['release_date_precision'])
        self.listen_time = text_to_time(track_outside['played_at'])
        self.markets = track['available_markets']

    def update_artists(self, data, access_token):
        for artist in self.artists:
            data = artist.update_artist_object(data, access_token)
        return data

    def jsonify_artists(self):
        for i in range(len(self.artists)):
            self.artists[i] = json.dumps(self.artists[i].__dict__)


def release_to_date(release, precision):
    if precision == 'day':
        return datetime.datetime.strptime(release, '%Y-%m-%d')
    elif precision == 'month':
        return datetime.datetime.strptime(release, '%Y-%m')
    elif precision == 'year':
        return datetime.datetime.strptime(release, '%Y')


def text_to_time(text):
    return datetime.datetime.strptime(text, '%Y-%m-%dT%H:%M:%S:%fZ')