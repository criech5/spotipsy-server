import json
import SpotiPsy
import datetime


def create_payload(access_token, tracks):
    artists = SpotiPsy.get_artists(tracks)
    payload = {
        'top_songs': build_songs(tracks),
        'top_artists': build_artists(artists),
        'top_genres': build_genres(artists),
        'recommended': build_recommendations(artists, access_token),
        'range': build_listen_range(tracks),
        'length': build_average_length(tracks),
        'age': build_age(tracks),
        'location': build_location(tracks),
        'popularity': build_popularity(tracks)
    }
    return payload


def build_recommendations(artists, access_token):
    rec_artists = SpotiPsy.recommend_artists(artists, access_token)
    return rec_artists


def build_songs(tracks):
    # list of songs fmt: [[obj, count]]
    songs_freq = SpotiPsy.song_frequency(tracks)
    songs = []
    blurb = ''
    for item in songs_freq:
        song = {}
        song['count'] = item["count"]
        if 5 <= item["count"] < 10:
            blurb = f'{item["object"].name} made up for {item["count"]*2}% of your plays. Guess it must be a good song?'
        elif 10 <= item["count"] < 25:
            blurb = f'Uh, wow. {item["object"].name} accounted for {item["count"]*2}% of your plays. Do you, uh, need new' \
                    f' music recs? All you have to do is ask.'
        elif item["count"] >= 25:
            blurb = f'{item["object"].name} is {item["count"]*2}% of your listens. {item["count"]*2}%! What am I supposed to' \
                    f' gain from that? What do YOU gain from it??'
        song['name'] = item["object"].name
        song['artists'] = []
        for artist in item["object"].artists:
            song['artists'].append({'name': artist.name, 'url': artist.url})
        song['album'] = item["object"].album
        song['url'] = item["object"].url
        song['images'] = item["object"].art_urls
        songs.append(song)
    return {'songs': songs, 'blurb': blurb}


def build_artists(artists):
    # list of artist objects, frequency
    artists_list, artists_freq = SpotiPsy.artist_frequency(artists)
    top_artists = []
    for artist in artists_list:
        artist_dict = {'name': artist.name, 'url': artist.url, 'images': artist.images}
        top_artists.append(artist_dict)
    blurb = ''
    if len(artists_list) > 1:
        if 5 <= artists_freq < 10:
            blurb = f'These artists made up for {artists_freq * len(artists_list) * 2}% of your plays.' \
                    f' Guess you must just be a pretty huge fan.'
        elif 10 <= artists_freq < 25:
            blurb = f'Uh, wow. These artists accounted for {artists_freq * len(artists_list) * 2}% ' \
                    f'of your plays. Do you, uh, need new music recs? All you have to do is ask.'
        elif artists_freq >= 25:
            blurb = f'These artists are {artists_freq * len(artists_list) * 2}% of your listens. ' \
                    f'{artists_freq * len(artists_list) * 2}%! What am I supposed to' \
                    f' gain from that? What do YOU gain from it??'
    else:
        if 5 <= artists_freq < 10:
            blurb = f'{artists_list[0].name} made up for {artists_freq * 2}% of your plays.' \
                    f' Guess you must just be a pretty huge fan.'
        elif 10 <= artists_freq < 25:
            blurb = f'Uh, wow. {artists_list[0].name} accounted for {artists_freq * 2}% ' \
                    f'of your plays. Do you, uh, need new music recs? All you have to do is ask.'
        elif artists_freq >= 25:
            blurb = f'{artists_list[0].name} is {artists_freq * 2}% of your listens. ' \
                    f'{artists_freq * 2}%! What am I supposed to' \
                    f' gain from that? What do YOU gain from it??'
    return {'artists': top_artists, 'count': artists_freq, 'blurb': blurb}


def build_genres(artists):
    # list of genres, frequency
    genres, genre_freq = SpotiPsy.genre_frequency(artists)
    return genres


def build_listen_range(tracks):
    # timedelta - time btwn 1st/last plays
    listen_delta = SpotiPsy.listen_range(tracks)
    dhms = {}
    dhms['days'] = listen_delta.days
    dhms['hours'] = listen_delta.seconds // 3600
    rem_sec = listen_delta.seconds - dhms['hours']*3600
    dhms['minutes'] = rem_sec // 60
    dhms['seconds'] = listen_delta.seconds - dhms['hours']*3600 - dhms['minutes']*60
    blurb = ''
    if dhms['days'] < 1:
        if dhms['hours'] < 1:
            blurb = 'Do you listen to everything on 2x speed or something?'
        elif 1 <= dhms['hours'] < 5:
            blurb = 'You\'re probably working hard at something important! Keep those tunes going.'
        elif dhms['hours'] > 5:
            blurb = 'How was your lunch break? Have something tasty today?'
    elif 1 <= dhms['days'] < 7:
        blurb = 'Slow and steady wins the race, I guess. Seems like you haven\'t been in much of a ' \
                'musical mood lately.'
    elif 7 <= dhms['days'] < 14:
        blurb = 'Did you just get back to civilization or something? I hope you at least had a radio ' \
                'to keep you company.'
    elif dhms['days'] > 14:
        blurb = 'Do you ever listen to music? What is this, one song a month? Well, maybe that makes each' \
                ' one more special to you. Or whatever.'
    return {'range': dhms, 'blurb': blurb}


def build_average_length(tracks):
    # int - avg song length in ms
    avg_length = SpotiPsy.average_length(tracks)
    min_sec = [avg_length // 1000 // 60, avg_length // 1000 % 60]
    return min_sec


def build_location(tracks):
    locations = SpotiPsy.location(tracks)
    file_in = open('ISO3166.json', 'r', encoding='utf-8')
    country_codes = json.load(file_in)
    file_in.close()
    blurb = ''
    if len(locations) == 1:
        blurb = f'You\'re listening from {country_codes[locations[0]]}, I\'m 100% sure! Don\'t worry,' \
                f' that\'s as specific as I can get.'
    elif len(locations) == 2:
        blurb = f'You\'re listening from the sunny shores of {country_codes[locations[0]]}! Or wait, ' \
                f'sorry, it looks like you might be hanging out in the snowy mountains of ' \
                f'{country_codes[locations[1]]}? I think I might need to dust off this crystal ball.'
    elif len(locations) > 2:
        blurb = f'Hmm... uhhh, hold on... I got it! You\'re from, uh, {country_codes[locations[0]]}!' \
                f' No, wait, scratch that, you\'re either from '
        for i in range(len(locations)):
            if i == len(locations) - 1:
                blurb += f'{country_codes[locations[i]]}.'
            else:
                blurb += f'{country_codes[locations[i]]} or '
    else:
        blurb = 'You\'re not in the house, Questlove.\nYou\'re nowhere.'
    return {'locations': locations, 'blurb': blurb}


def build_age(tracks):
    # avg song age fmt: [years, months, days]
    age_ymd = SpotiPsy.age(tracks)
    age_blurb = ''
    if age_ymd[0] < 5:
        age_blurb = 'You only listen to the new stuff! Either you were just born yesterday, or you just ' \
                    'REALLY like to commit to the whole \"being with the times\" thing.'
    elif 5 <= age_ymd[0] < 12:
        age_blurb = 'You\'re still pretty young, but not in diapers or anything - I mean, probably not.'
    elif 12 <= age_ymd[0] < 20:
        age_blurb = 'You\'re easy to card at the bar, but not because you look old - your birth year just' \
                    ' starts with a 1.'
    elif 20 < age_ymd[0] < 25:
        age_blurb = 'What are you doing listening to this much music? Don\'t you have a mortgage to pay ' \
                    'off or something?'
    elif 25 <= age_ymd[0] < 40:
        age_blurb = 'I\'ve heard that nursing homes often play music that was popular when their ' \
                    'residents were early teens. Something to think about.'
    elif 40 <= age_ymd[0]:
        age_blurb = 'Did you know computers consider someone this old to be prehistoric? It\'s true!'
    return {'ymd': age_ymd, 'blurb': age_blurb}


def build_popularity(tracks):
    popularity = SpotiPsy.popularity(tracks)
    blurb = ''
    if 90 <= popularity < 100:
        blurb = 'You have basically all the music of the last 100 years at your fingertips, and you still ' \
                'play the Top 40 charts on repeat! Honestly, I\'ve got to respect that.'
    elif 80 <= popularity < 90:
        blurb = 'I can tell you\'re way too refined to just listen to the Top 40 on repeat. Yes, you\'re ' \
                'someone who needs the breadth of sound only the Top 100 can provide.'
    elif 60 <= popularity < 80:
        blurb = 'No one\'s going to argue with what you put on - you\'re not too poppy and you\'re not ' \
                'too obscure either.'
    elif 50 <= popularity < 60:
        blurb = 'You\'re cutting edge, but probably not annoyingly so.'
    elif 35 <= popularity < 50:
        blurb = 'Big fan of the Discover Weekly playlist, I see.'
    elif 14 <= popularity < 35:
        blurb = 'What are you listening to, muzak? How did you find this stuff?'
    elif popularity < 14:
        blurb = 'I really have to commend you for listening to your best friend\'s new mixtape so much.' \
                'I\'m sure they really appreciate your support.'

    # ADD MOST/LEAST POPULAR SONGS
    songs = []
    mostleast = SpotiPsy.most_least_popular(tracks)
    for item in mostleast:
        song = {}
        song['name'] = item.name
        song['artists'] = []
        for artist in item.artists:
            song['artists'].append({'name': artist.name, 'url': artist.url})
        song['album'] = item.album
        song['url'] = item.url
        song['images'] = item.art_urls
        songs.append(song)
    return {'score': popularity, 'blurb': blurb, 'most': songs[1], 'least': songs[0]}