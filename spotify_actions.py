# spotify_moods.py

import base64
import datetime
import json
import os
import random
import string
import time
from collections import Counter
from urllib.parse import quote

import requests
import spotipy
import spotipy.util as util

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
redirect_uri = os.environ.get('REDIRECT_URI')

scope = 'user-top-read playlist-modify-public playlist-modify-private'


def req_auth():

    show_dialog = "false"

    AUTH_FIRST_URL = f'https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={quote(redirect_uri)}&show_dialog={show_dialog}&scope={scope}'
    return AUTH_FIRST_URL


def req_token(code):

    # B64 encode variables
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())

    # Token data
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }

    # Token header
    token_header = {
        "Authorization": f"Basic {client_creds_b64.decode()}"
    }

    # Make request post for token info
    token_json = requests.post(
        'https://accounts.spotify.com/api/token', data=token_data, headers=token_header)

    # Checking if token is still valid, otherwise, refresh

    if "expires_in" in token_json.json():

        now = datetime.datetime.now()
        expires_in = token_json.json()['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)

        if now > expires:

            refresh_token_data = {
                "grant_type": "refresh_token",
                "refresh_token": token_json.json()['refresh_token']
            }

            refresh_token_json = requests.post(
                'https://accounts.spotify.com/api/token', data=refresh_token_data, headers=token_header)
            token = refresh_token_json.json()['access_token']

            return token
        else:
            token = token_json.json()['access_token']
            return token
    else:

        token = token_json.json()['access_token']

        return token

class Track:
     def __init__(self, id, name, artists, imageURL, audio_features=None):
         self.id = id
         self.name = name
         self.artists = artists
         self.imageURL = imageURL
         self.audio_features = []

def getVibes(user_token, tryAgain=False):
    spotifyObject = spotipy.Spotify(auth=user_token)

    start = time.time()

    short_term_favorite_artist_items = spotifyObject.current_user_top_artists(limit=50, time_range="short_term")['items']
    medium_term_favorite_artist_items = spotifyObject.current_user_top_artists(limit=50, time_range="medium_term")['items']
    long_term_favorite_artist_items = spotifyObject.current_user_top_artists(limit=50, time_range="long_term")['items']

    artistIDSet = set()
    artistImageList = []
    
    print(user_token)
    print(len(short_term_favorite_artist_items))
    for i in range(20):
        if i < len(short_term_favorite_artist_items):
            if short_term_favorite_artist_items[i]['id'] not in artistIDSet:
                if short_term_favorite_artist_items[i]['images']:
                    artistImageList.append(short_term_favorite_artist_items[i]['images'][0]['url'])
                    artistIDSet.add(short_term_favorite_artist_items[i]['id'])
        if i < len(medium_term_favorite_artist_items):
            if medium_term_favorite_artist_items[i]['id'] not in artistIDSet:
                if medium_term_favorite_artist_items[i]['images']:
                    artistImageList.append(medium_term_favorite_artist_items[i]['images'][0]['url'])
                    artistIDSet.add(medium_term_favorite_artist_items[i]['id'])
        if i < len(long_term_favorite_artist_items):
            if long_term_favorite_artist_items[i]['id'] not in artistIDSet:
                if long_term_favorite_artist_items[i]['images']:
                    artistImageList.append(long_term_favorite_artist_items[i]['images'][0]['url'])
                    artistIDSet.add(long_term_favorite_artist_items[i]['id'])


    danceableSet = set()
    angrySet = set()
    happySet = set()
    chillSet = set()
    hypeSet = set()
    sadSet = set()

    artistIDList = list(artistIDSet)

    dance = [0.0]
    angry = [0.0]
    happy = [0.0]
    chill = [0.0]
    hype = [0.0]
    sad = [0.0]

    def getAudioFeatures(spotify_ids):
            audio_features_resp = spotifyObject.audio_features(spotify_ids)
            audio_features_list = []

            for features in audio_features_resp:
                audio_features = {}
                
                audio_features['energy'] = features['energy']
                audio_features['danceability'] = features['danceability']
                audio_features['sadness'] = 1.05 * (1 - features['energy']) * (1 - features['valence'])
                audio_features['happiness'] = 1.05 * features['energy'] * features['valence']
                audio_features['anger'] = 1.05 * features['energy'] * (1 - features['valence'])

                dance[0] += audio_features['danceability']
                angry[0] += audio_features['anger']
                happy[0] += audio_features['happiness']
                chill[0] += 1 - audio_features['energy']
                hype[0] += audio_features['energy']
                sad[0] += audio_features['sadness']

                if audio_features['energy'] <= 0.3:
                    chillSet.add(features['id'])
                if audio_features['energy'] >= 0.7:
                    hypeSet.add(features['id'])
                if audio_features['happiness'] >= 0.7:
                    happySet.add(features['id'])
                if audio_features['sadness'] >= 0.5:
                    sadSet.add(features['id'])
                if audio_features['anger'] >= 0.55:
                    angrySet.add(features['id'])
                if audio_features['danceability'] >= 0.75:
                    danceableSet.add(features['id'])
                    
                audio_features_list.append(audio_features)

            return audio_features_list

    short_term_favorite_items = spotifyObject.current_user_top_tracks(limit=50, time_range="short_term")['items']
    medium_term_favorite_items = spotifyObject.current_user_top_tracks(limit=50, time_range="medium_term")['items']
    long_term_favorite_items = spotifyObject.current_user_top_tracks(limit=50, time_range="long_term")['items']

    favorite_tracks = []
    idSet = set()
    for i in range(len(short_term_favorite_items)):
        if short_term_favorite_items[i]['id'] not in idSet:
            favorite_tracks.append(Track(short_term_favorite_items[i]['id'], short_term_favorite_items[i]['name'], short_term_favorite_items[i]['artists'], short_term_favorite_items[i]['album']['images'][0]['url']))
            idSet.add(short_term_favorite_items[i]['id'])
        if medium_term_favorite_items[i]['id'] not in idSet:
            favorite_tracks.append(Track(medium_term_favorite_items[i]['id'], medium_term_favorite_items[i]['name'], medium_term_favorite_items[i]['artists'], medium_term_favorite_items[i]['album']['images'][0]['url']))
            idSet.add(medium_term_favorite_items[i]['id'])
        if long_term_favorite_items[i]['id'] not in idSet:
            favorite_tracks.append(Track(long_term_favorite_items[i]['id'], long_term_favorite_items[i]['name'], long_term_favorite_items[i]['artists'], long_term_favorite_items[i]['album']['images'][0]['url']))
            idSet.add(long_term_favorite_items[i]['id'])

    for i in range(0, len(favorite_tracks), 100):
        hundred = favorite_tracks[i:i+100]
        spotify_ids = [track.id for track in hundred]
#        print(spotify_ids)
        audio_features = getAudioFeatures(spotify_ids)
        for k in range(len(favorite_tracks[i:i+100])):
            favorite_tracks[i + k].audio_features = audio_features[k]

    favorite_chill_track = None
    favorite_hype_track = None
    favorite_sad_track = None
    favorite_happy_track = None
    favorite_angry_track = None
    favorite_dance_track = None

    i = 1
    
    for track in favorite_tracks:
        if track.audio_features['energy'] < 0.3 and not favorite_chill_track:
            favorite_chill_track = track
        if track.audio_features['sadness'] >= 0.7 and not favorite_sad_track:
            favorite_sad_track = track
        if track.audio_features['energy'] >= 0.8 and not favorite_hype_track:
            favorite_hype_track = track
        if track.audio_features['happiness'] >= 0.75 and not favorite_happy_track:
            favorite_happy_track = track
        if track.audio_features['anger'] >= 0.56 and not favorite_angry_track:
            favorite_angry_track = track
        if track.audio_features['danceability'] >= 0.70 and not favorite_dance_track:
            favorite_dance_track = track
        
        i += 1
    
    scores = {}
    if len(idSet) > 0:
        scores['hypeScore'] = hype[0]/len(idSet)
        scores['chillScore'] = chill[0]/len(idSet)
        scores['danceScore'] = dance[0]/len(idSet)
        scores['sadScore'] = sad[0]/len(idSet)
        scores['happyScore'] = happy[0]/len(idSet)
        scores['angryScore'] = angry[0]/len(idSet)
    else:
        scores['hypeScore'] = 0.45
        scores['chillScore'] = 0.30
        scores['danceScore'] = 0.51
        scores['sadScore'] = 0.2
        scores['happyScore'] = 0.21
        scores['angryScore'] = 0.23

    user = spotifyObject.me()
    profile_image = "https://lh3.googleusercontent.com/eN0IexSzxpUDMfFtm-OyM-nNs44Y74Q3k51bxAMhTvrTnuA4OGnTi_fodN4cl-XxDQc" # default
    if user['images']:
        profile_image = user['images'][0]['url']

    fav_mood_tracks = {}

    max_key = max(scores, key=scores.get)

    if max_key == "danceScore":
        if favorite_dance_track:
            fav_mood_tracks['dance'] = (favorite_dance_track.name, favorite_dance_track.artists[0]['name'], favorite_dance_track.imageURL)
        if favorite_hype_track:
            fav_mood_tracks['hype'] = (favorite_hype_track.name, favorite_hype_track.artists[0]['name'], favorite_hype_track.imageURL)
        if favorite_chill_track:
            fav_mood_tracks['chill'] = (favorite_chill_track.name, favorite_chill_track.artists[0]['name'], favorite_chill_track.imageURL)
        if favorite_happy_track:
            fav_mood_tracks['happy'] = (favorite_happy_track.name, favorite_happy_track.artists[0]['name'], favorite_happy_track.imageURL)
        if favorite_sad_track:
            fav_mood_tracks['sad'] = (favorite_sad_track.name, favorite_sad_track.artists[0]['name'], favorite_sad_track.imageURL)
        if favorite_angry_track:
            fav_mood_tracks['angry'] = (favorite_angry_track.name, favorite_angry_track.artists[0]['name'], favorite_angry_track.imageURL)
    elif max_key == "hypeScore":
        if favorite_hype_track:
            fav_mood_tracks['hype'] = (favorite_hype_track.name, favorite_hype_track.artists[0]['name'], favorite_hype_track.imageURL)
        if favorite_dance_track:
            fav_mood_tracks['dance'] = (favorite_dance_track.name, favorite_dance_track.artists[0]['name'], favorite_dance_track.imageURL)
        if favorite_happy_track:
            fav_mood_tracks['happy'] = (favorite_happy_track.name, favorite_happy_track.artists[0]['name'], favorite_happy_track.imageURL)
        if favorite_sad_track:
            fav_mood_tracks['sad'] = (favorite_sad_track.name, favorite_sad_track.artists[0]['name'], favorite_sad_track.imageURL)
        if favorite_angry_track:
            fav_mood_tracks['angry'] = (favorite_angry_track.name, favorite_angry_track.artists[0]['name'], favorite_angry_track.imageURL)
        if favorite_chill_track:
            fav_mood_tracks['chill'] = (favorite_chill_track.name, favorite_chill_track.artists[0]['name'], favorite_chill_track.imageURL)
    else:
        if favorite_chill_track:
            fav_mood_tracks['chill'] = (favorite_chill_track.name, favorite_chill_track.artists[0]['name'], favorite_chill_track.imageURL)
        if favorite_hype_track:
            fav_mood_tracks['hype'] = (favorite_hype_track.name, favorite_hype_track.artists[0]['name'], favorite_hype_track.imageURL)
        if favorite_happy_track:
            fav_mood_tracks['happy'] = (favorite_happy_track.name, favorite_happy_track.artists[0]['name'], favorite_happy_track.imageURL)
        if favorite_sad_track:
            fav_mood_tracks['sad'] = (favorite_sad_track.name, favorite_sad_track.artists[0]['name'], favorite_sad_track.imageURL)
        if favorite_angry_track:
            fav_mood_tracks['angry'] = (favorite_angry_track.name, favorite_angry_track.artists[0]['name'], favorite_angry_track.imageURL)
        if favorite_dance_track:
            fav_mood_tracks['dance'] = (favorite_dance_track.name, favorite_dance_track.artists[0]['name'], favorite_dance_track.imageURL)

    songSets = [happySet, sadSet, hypeSet, chillSet, danceableSet, angrySet]

    end = time.time()
    print(end - start)     
    return [scores, fav_mood_tracks, profile_image, songSets, artistImageList[:10], artistIDList]

def getTracks(user_token, songSets):
    spotifyObject = spotipy.Spotify(auth=user_token)

    track_ids = []
    if songSets[0]:
        track_ids.append(random.sample(songSets[0], 1)[0])
    else:
        track_ids.append('2d8JP84HNLKhmd6IYOoupQ')
    if songSets[1]:
        track_ids.append(random.sample(songSets[1], 1)[0])
    else:
        track_ids.append('6K4t31amVTZDgR3sKmwUJJ')
    if songSets[2]:
        track_ids.append(random.sample(songSets[2], 1)[0])
    else:
        track_ids.append('2xLMifQCjDGFmkHkpNLD9h')
    if songSets[3]:
        track_ids.append(random.sample(songSets[3], 1)[0])
    else:
        track_ids.append('4S7YHmlWwfwArgd8LfSPud')
    if songSets[4]:
        track_ids.append(random.sample(songSets[4], 1)[0])
    else:
        track_ids.append('0wwPcA6wtMf6HUMpIRdeP7')
    if songSets[5]:
        track_ids.append(random.sample(songSets[5], 1)[0])
    else:
        track_ids.append('2gZUPNdnz5Y45eiGxpHGSc')
    tracks = {}

    api_resp = spotifyObject.tracks(track_ids)['tracks']

    tracks['happy'] = (api_resp[0]['name'], api_resp[0]['artists'][0]['name'], api_resp[0]['album']['images'][0]["url"])
    tracks['sad'] = (api_resp[1]['name'], api_resp[1]['artists'][0]['name'], api_resp[1]['album']['images'][0]["url"])
    tracks['hype'] = (api_resp[2]['name'], api_resp[2]['artists'][0]['name'], api_resp[2]['album']['images'][0]["url"])
    tracks['chill'] = (api_resp[3]['name'], api_resp[3]['artists'][0]['name'], api_resp[3]['album']['images'][0]["url"])
    tracks['dance'] = (api_resp[4]['name'], api_resp[4]['artists'][0]['name'], api_resp[4]['album']['images'][0]["url"])
    tracks['angry'] = (api_resp[5]['name'], api_resp[5]['artists'][0]['name'], api_resp[5]['album']['images'][0]["url"])
    

    return tracks

def getRecommendations(user_token, topArtistIDs, vibe, songList=[]):
    spotifyObject = spotipy.Spotify(auth=user_token)
    songSet = set(songList)
    if vibe == "happy":
        happy_recommendations = spotifyObject.recommendations(seed_artists=list(topArtistIDs[:4]), seed_genres=['happy'], min_valence=0.75, min_energy=0.75, limit=20)['tracks']
        happy_recommendations2 = spotifyObject.recommendations(seed_artists=list(topArtistIDs[4:8]), seed_genres=['happy'], min_valence=0.75, min_energy=0.75, limit=20)['tracks']

        for i in range(10):
            if i < len(happy_recommendations): songSet.add(happy_recommendations[i]['id'])
            if i < len(happy_recommendations2): songSet.add(happy_recommendations2[i]['id'])
    
    elif vibe == "sad":
        sad_recommendations = spotifyObject.recommendations(seed_artists=list(topArtistIDs[:4]), seed_genres=['sad'], max_valence=0.25, max_energy=0.4, limit=20)['tracks']
        sad_recommendations2 = spotifyObject.recommendations(seed_artists=list(topArtistIDs[4:8]), seed_genres=['sad'], max_valence=0.25, max_energy=0.4, limit=20)['tracks']

        for i in range(10):
            if i < len(sad_recommendations): songSet.add(sad_recommendations[i]['id'])
            if i < len(sad_recommendations2): songSet.add(sad_recommendations2[i]['id'])

    elif vibe == "hype":
        sad_recommendations = spotifyObject.recommendations(seed_artists=list(topArtistIDs[:5]), min_energy=0.75, limit=10)['tracks']
        sad_recommendations2 = spotifyObject.recommendations(seed_artists=list(topArtistIDs[5:10]), min_energy=0.75, limit=10)['tracks']

        for i in range(10):
            if i < len(sad_recommendations): songSet.add(sad_recommendations[i]['id'])
            if i < len(sad_recommendations2): songSet.add(sad_recommendations2[i]['id'])

    elif vibe == "chill":
        chill_recommendations = spotifyObject.recommendations(seed_artists=list(topArtistIDs[:4]), seed_genres=['chill'], max_energy=0.25, limit=20)['tracks']
        chill_recommendations2 = spotifyObject.recommendations(seed_artists=list(topArtistIDs[4:8]), seed_genres=['chill'], max_energy=0.25, limit=20)['tracks']

        for i in range(10):
            if i < len(chill_recommendations): songSet.add(chill_recommendations[i]['id'])
            if i < len(chill_recommendations2): songSet.add(chill_recommendations2[i]['id'])

    elif vibe == "groovy":
        dance_recommendations = spotifyObject.recommendations(seed_artists=list(topArtistIDs[:5]), min_danceability=0.8, limit=20)['tracks']
        dance_recommendations2 = spotifyObject.recommendations(seed_artists=list(topArtistIDs[5:10]), min_danceability=0.8, limit=20)['tracks']

        for i in range(10):
            if i < len(dance_recommendations): songSet.add(dance_recommendations[i]['id'])
            if i < len(dance_recommendations2): songSet.add(dance_recommendations2[i]['id'])

    elif vibe == "angry":
        angry_recommendations = spotifyObject.recommendations(seed_artists=list(topArtistIDs[:5]), max_valence=0.25, min_energy=0.75, limit=20)['tracks']
        angry_recommendations2 = spotifyObject.recommendations(seed_artists=list(topArtistIDs[5:10]), max_valence=0.25, min_energy=0.75, limit=20)['tracks']

        for i in range(10):
            if i < len(angry_recommendations): songSet.add(angry_recommendations[i]['id'])
            if i < len(angry_recommendations2): songSet.add(angry_recommendations2[i]['id'])
    
    elif vibe == "study":
        songSet = set()
        study_recommendations = spotifyObject.recommendations(seed_artists=list(topArtistIDs[:4]), seed_genres=['study'], limit=20)['tracks']
        study_recommendations2 = spotifyObject.recommendations(seed_artists=list(topArtistIDs[4:8]), seed_genres=['study'], limit=20)['tracks']
    
        for i in range(20):
            if i < len(study_recommendations): songSet.add(study_recommendations[i]['id'])
            if i < len(study_recommendations2): songSet.add(study_recommendations2[i]['id'])

    elif vibe == "workout":
#        songSet = set()
        workout_recommendations = spotifyObject.recommendations(seed_tracks=songList[:4], seed_genres=['work-out'], min_energy=0.8, limit=20)['tracks']
        workout_recommendations2 = spotifyObject.recommendations(seed_tracks=songList[4:8], seed_genres=['work-out'], min_energy=0.8, limit=20)['tracks']
    
        for i in range(20):
            if i < len(workout_recommendations): songSet.add(workout_recommendations[i]['id'])
            if i < len(workout_recommendations2): songSet.add(workout_recommendations2[i]['id'])


    api_resp = spotifyObject.tracks(list(songSet)[:50])['tracks']

    playlistSongs = []
    for track in api_resp:
        playlistSongs.append((track['name'], track['artists'][0]['name'], track['album']['images'][0]['url'], track['id']))
    return playlistSongs


def createPlaylist(user_token, song_ids, vibe):
    spotifyObject = spotipy.Spotify(auth=user_token)
    user_id = str(spotifyObject.current_user()['id'])
    description = vibe.capitalize() + " vibes by Vibeify."

    mydate = datetime.datetime.now()
    month = mydate.strftime("%B")

    titles = {}
    titles['happy'] = 'Happy ' + month + ' 😁'
    titles['sad'] = 'Sad ' + month + ' 😔'
    titles['chill'] = 'Chill ' + month + ' 😎'
    titles['hype'] = 'Hype ' + month + ' 😤'
    titles['groovy'] = 'Groovy ' + month + ' 😏'
    titles['angry'] = 'Angry ' + month + ' 😡'
    titles['study'] = 'Study ' + month + ' 📚'
    titles['workout'] = 'Workout ' + month + ' 💪'
    playlist_name = titles[vibe]
    playlist = spotifyObject.user_playlist_create(user_id, playlist_name, public=False, description=description)
    spotifyObject.user_playlist_add_tracks(user_id, playlist['id'], song_ids)

    return playlist['id']

def unfollow_playlist(user_token, playlist_id):
    spotifyObject = spotipy.Spotify(auth=user_token)
    user_id = str(spotifyObject.current_user()['id'])

    return spotifyObject.user_playlist_unfollow(user_id, playlist_id)
