import json
import sys

import requests
from flask import Flask, request, Response, jsonify, redirect
from flask_cors import CORS
import SpotiPsy
import SpotiPayload

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
                   'redirect_uri': 'http://ec2-3-19-57-186.us-east-2.compute.amazonaws.com:5000/auth',
                   'client_id': '136c245c7f744cf1844b2bb64aadbcb1',
                   'client_secret': 'a954bbaf3e7f444e9d3bee48c10e7656'}
    access_response = requests.post('https://accounts.spotify.com/api/token', data=access_body).json()
    expires_in = access_response['expires_in']
    global access_token
    access_token = access_response['access_token']
    refresh_token = access_response['refresh_token']
    return redirect('http://criech5.github.io/#/signedin', code=302)


@api.route('/psy')
def get_data():
    global access_token
    tracks = SpotiPsy.get_play_data(access_token, False)
    data_json = SpotiPayload.create_payload(access_token, tracks)
    return data_json


if __name__ =='__main__':
    api.run(host="0.0.0.0", port=5000)