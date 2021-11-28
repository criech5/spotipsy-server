import requests


class Artist:

    def __init__(self, artist):
        self.name = artist['name']
        self.id = artist['id']
        self.url = artist['external_urls']['spotify']
        self.genres = []
        self.images = []
        self.popularity = 0
        self.count = 1

    def update_artist_object(self, data, access_token):
        if self.id in data.keys():
            self.genres = data[self.id].genres
            self.images = data[self.id].images
            self.popularity = data[self.id].popularity
            self.count += 1
            data[self.id].count += 1
        else:
            artist_json = requests.get(f'https://api.spotify.com/v1/artists/{self.id}',
                                 headers={'Authorization': f'Bearer {access_token}'}).json()
            # artist_json = {'genres': [], 'images': [], 'popularity': 0}
            self.genres = artist_json['genres']
            self.images = artist_json['images']
            self.popularity = artist_json['popularity']
        data[self.id] = self
        return data
