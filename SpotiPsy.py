import sys

import requests
import json
import webbrowser
from time import sleep
from operator import itemgetter
import datetime
import Track
import Artist


def authorize():
    # This GET and webbrowser thing should probably be handled client-side when that gets built
    response = requests.get('https://accounts.spotify.com/authorize?'
                 'client_id=136c245c7f744cf1844b2bb64aadbcb1&'
                 'response_type=code&'
                 'redirect_uri=http://127.0.0.1:5000/&'
                 'scope=playlist-read-private%20playlist-modify-private%20playlist-modify-public'
                 '%20user-read-recently-played%20user-top-read&'
                 'show_dialog=true', allow_redirects=True).url
    webbrowser.open(response)
    auth_code = ''
    while auth_code == '':
        auth_code = requests.get('http://127.0.0.1:5000/auth').json()['code']
        sleep(3)
    access_body = {'grant_type': 'authorization_code',
                   'code': auth_code,
                   'redirect_uri': 'http://127.0.0.1:5000/',
                   'client_id': '136c245c7f744cf1844b2bb64aadbcb1',
                   'client_secret': 'a954bbaf3e7f444e9d3bee48c10e7656'}
    access_response = requests.post('https://accounts.spotify.com/api/token', data=access_body).json()
    expires_in = access_response['expires_in']
    access_token = access_response['access_token']
    refresh_token = access_response['refresh_token']
    return access_token, refresh_token, expires_in


def get_play_data(access_token, debug):
    all_track_data = {}
    if debug:
        file_in = open('recent.json', 'r', encoding='utf-8')
        all_track_data = json.load(file_in)
        file_in.close()
    else:
        all_track_data = requests.get('https://api.spotify.com/v1/me/player/recently-played?limit=50',
                                 headers={'Authorization': f'Bearer {access_token}'}).json()
    tracks = []
    artists_dict = {}
    for track in all_track_data['items']:
        new_track = Track.Track(track)
        artists_dict = new_track.update_artists(artists_dict, access_token)
        tracks.append(new_track)
    # may want this later on:
    # artists = artists_dict.values()
    return tracks


def get_artists(plays):
    artists = {}
    for track in plays:
        for artist in track.artists:
            if artist.id not in artists:
                artists[artist.id] = {'object': artist, 'count': 1}
            else:
                artists[artist.id]['count'] += 1
    return artists


def artist_frequency(artists):
    max_freq = 0
    max_list = []
    for id in artists:
        if artists[id]['count'] > max_freq:
            max_list = [artists[id]['object']]
            max_freq = artists[id]['count']
        elif artists[id]['count'] == max_freq:
            max_list.append(artists[id]['object'])
    return max_list, max_freq


# won't work in debug mode (update doesn't make call)
def genre_frequency(artists):
    genres = {}
    max_freq = 0
    max_list = []
    for id in artists:
        for genre in artists[id]['object'].genres:
            if genre in genres:
                genres[genre] += artists[id]['count']
            else:
                genres[genre] = artists[id]['count']
    for genre in genres:
        if genres[genre] > max_freq:
            max_list = [[genre, genres[genre]]]
            max_freq = genres[genre]
        elif genres[genre] == max_freq:
            max_list.append([genre, genres[genre]])
    print(max_list, max_freq)
    return max_list, max_freq


def song_frequency(plays):
    max_freq= 0
    max_list = []
    track_dict = {}
    for track in plays:
        if track.id not in track_dict:
            track_dict[track.id] = {'count': 1, 'object': track}
        else:
            track_dict[track.id]['count'] += 1
    for id in track_dict:
        if track_dict[id]['count'] > max_freq:
            max_list = [track_dict[id]]
            max_freq = track_dict[id]['count']
        elif track_dict[id]['count'] == max_freq:
            max_list.append(track_dict[id])
    return max_list


def age(plays):
    total_timestamp = 0
    now = datetime.datetime.now()
    # thanks stackoverflow question 3617170 for the next 2 lines lol
    deltas = [now - plays[i].release for i in range(0, len(plays))]
    avg_age = sum(deltas, datetime.timedelta(0)) / len(deltas)
    age_years = avg_age.days // 365
    age_months = avg_age.days % 365 // 30
    age_days = avg_age.days % 365 % 30
    return age_years, age_months, age_days


def recommend_artists(artists, access_token):
    related_list = []
    related_dict = {}
    for id in artists:
        url = f'https://api.spotify.com/v1/artists/{id}/related-artists'
        response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
        response = response.json()['artists']
        for item in response:
            if item['id'] not in related_dict:
                related_dict[item['id']] = {
                    'name': item['name'],
                    'url': item['external_urls']['spotify'],
                    'images': item['images'],
                    'count': artists[id]['count']
                }
            else:
                related_dict[item['id']]['count'] += artists[id]['count']
    for key in related_dict:
        related_list.append(related_dict[key])
    sorted_related = sorted(related_list, key=itemgetter('count'), reverse=True)
    return sorted_related[:3]


def average_length(plays):
    total_length = 0
    for track in plays:
        total_length += track.length
    avg_length = total_length // len(plays)
    return avg_length


def listen_range(plays):
    first_time = plays[-1].listen_time
    last_time = plays[0].listen_time
    delta = last_time - first_time
    return delta


def location(plays):
    locations = plays[0].markets
    for track in plays:
        new_locations = []
        for market in track.markets:
            if market in locations:
                new_locations.append(market)
        locations = new_locations
    return locations


def popularity(plays):
    total_pop = 0
    num_tracks = len(plays)
    for track in plays:
        total_pop += track.popularity
    return total_pop / num_tracks


def most_least_popular(tracks):
    low = 101
    high = -1
    res = [-1, -1]
    for track in tracks:
        if track.popularity >= high:
            res[1] = track
            high = track.popularity
        if track.popularity <= low:
            res[0] = track
            low = track.popularity
    return res


if __name__ == '__main__':
    tracks = get_play_data('', True)
    print(listen_range(tracks))
    print(location(tracks))
    print(age(tracks))
    for artist in artist_frequency(get_artists(tracks)):
        print(f'{artist.name}, {artist.count} plays')
    for genre in genre_frequency(get_artists(tracks)):
        print(f'{genre[0]}, {genre[1]} plays')
    for track in song_frequency(tracks):
        print(f'{track[0].name} was listened to {track[1]} times')
