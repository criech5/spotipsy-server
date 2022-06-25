import os

import requests
from flask import Flask, request, Response, jsonify, redirect
from flask_cors import CORS
from time import sleep
import SpotiPsy
import SpotiPayload
import UserTracker

global access_token

api = Flask(__name__)
CORS(api)


# @api.route('/')
# def get_code():
#     code = request.query_string.decode(encoding='utf-8')[5:]
#     if code is not None and code != '':
#         with open('auth.txt', 'w') as auth_file:
#             auth_file.write(code)
#     return redirect('https://coleriechert.com', code=302)


@api.route('/auth')
def get_auth():
    auth_code = request.query_string.decode(encoding='utf-8')[5:]

    if auth_code is None:
        auth_code = ''
        ret = jsonify(code=auth_code, status=400)
    else:
        ret = jsonify(code=auth_code, status=200)

    access_body = {'grant_type': 'authorization_code',
                   'code': auth_code,
                   # 'redirect_uri': 'http://127.0.0.1:5000/auth',
                   'redirect_uri': 'https://spotipsy.herokuapp.com/auth',
                   # 'client_id': '136c245c7f744cf1844b2bb64aadbcb1',
                   # 'client_secret': 'a954bbaf3e7f444e9d3bee48c10e7656'}
                   'client_id': os.environ.get('CLIENT_ID'),
                   'client_secret': os.environ.get('CLIENT_SECRET')}
    access_response = requests.post('https://accounts.spotify.com/api/token', data=access_body).json()
    expires_in = access_response['expires_in']
    global access_token
    access_token = access_response['access_token']
    refresh_token = access_response['refresh_token']
    # return redirect('http://localhost:3000/project-site/#/spotipsy/signedin', code=302)
    return redirect('http://criech5.github.io/project-site/#/spotipsy/signedin', code=302)


@api.route('/psy')
def get_data():
    global access_token
    sleep(2)
    tracks = SpotiPsy.get_play_data(access_token, False)
    data_json = SpotiPayload.create_payload(access_token, tracks)
    return data_json


@api.route('/automate/<email>')
def do_automate(email):
    UserTracker.edit_users(os.environ.get('USERNAME'), os.environ.get('PASSWORD'), email)
    return email


@api.route('/helloworld')
def hello_world():
    # I can't get my deploys to work correctly, and this is a lot easier to test lol
    print('Hello, world!')
    return 'Hello, world!'


if __name__ =='__main__':
    api.run(debug=True)
