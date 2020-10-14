import datetime
import random
import string
from collections import Counter

import spotipy
import spotipy.util as util


def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

def create_party_playlist(token, playlist_name, playlist_desc):
    spotifyObject = spotipy.Spotify(auth=token)
    user_id = str(spotifyObject.current_user()['id'])
    first_name = spotifyObject.current_user()['display_name'].split()[0]

    if playlist_name is None:
        playlist_name = first_name + '\'s Party'
        playlist_desc = "A party on " + custom_strftime('%B {S}, %Y', datetime.datetime.now()) + ". From Vibeify."

    party_playlist = spotifyObject.user_playlist_create(user_id, playlist_name, public=False, description=playlist_desc)
    
    user = spotifyObject.me()
    profile_image = "https://lh3.googleusercontent.com/eN0IexSzxpUDMfFtm-OyM-nNs44Y74Q3k51bxAMhTvrTnuA4OGnTi_fodN4cl-XxDQc" # default
    if user['images']:
        profile_image = user['images'][0]['url']

    return [first_name, user_id, party_playlist['id'], profile_image]

def generate(host_token, guest_tokens, playlist_id):
    spotifyObject = spotipy.Spotify(auth=host_token)
    host_id = str(spotifyObject.current_user()['id'])

#    host_country = spotifyObject.me()['country']

    # Collect collective top tracks and artists

    top_artists_list = [] # list of dictionaries of guests' top artists
    top_tracks_list = [] # list of dictionaries of guests' top tracks

    for guest_token in guest_tokens:
#        print(guest_token) # debugging
        guest_object = spotipy.Spotify(auth=guest_token)

        # Guest follows the playlist
#        print(host_id, playlist_id)
#        guest_object.user_playlist_follow_playlist(host_id, playlist_id)
        
        ranges = {'short_term': 8, 'medium_term': 9, 'long_term': 10}

        guest_top_tracks = {} # guest dictionary {(name, spotifyURI): likeScore, ...} like,  {('The Less I Know the Better, '349rh3498r'): 27, ...}
        guest_top_artists = {} # guest dictionary  {(name, spotifyURI): likeScore, ...} like,  {('Kendrick Lamar, '349rh3498r'): 27, ...}

        for range in ranges.keys():   

            guest_top_tracks_range = guest_object.current_user_top_tracks(limit=50, time_range=range)['items']
            
            for track in guest_top_tracks_range:
                if (track['name'], track['id']) in guest_top_tracks:
                    guest_top_tracks[(track['name'], track['id'])] += ranges[range]
                else:
                    guest_top_tracks[(track['name'], track['id'])] = ranges[range]
            
            guest_top_artists_range = guest_object.current_user_top_artists(limit=50, time_range=range)['items']
            
            for artist in guest_top_artists_range:
                if (artist['name'], artist['id']) in guest_top_artists:
                    guest_top_artists[(artist['name'], artist['id'])] += ranges[range]
                else:
                    guest_top_artists[(artist['name'], artist['id'])] = ranges[range]

        top_tracks_list.append(guest_top_tracks)
        top_artists_list.append(guest_top_artists)

    group_favorite_tracks = [list(ttdict.keys()) for ttdict in top_tracks_list]
    group_favorite_artists = [list(tadict.keys()) for tadict in top_artists_list]

    from itertools import chain
    group_favorite_tracks_counter = Counter(chain(*group_favorite_tracks)) # a frequency count of everyone's collective top tracks
    group_favorite_artists_counter = Counter(chain(*group_favorite_artists)) # a frequency count of everyone's collective top artists

    favorite_track_candidates = set()
    common_tracks = set()

    for track in group_favorite_tracks_counter:
        if group_favorite_tracks_counter[track] >= 2 and len(guest_tokens) in [2,3]:
            common_tracks.add(track)
        else:
            if group_favorite_tracks_counter[track] >= (len(guest_tokens) // 2):
                common_tracks.add(track)

#    print(len(favorite_track_candidates))
    if len(common_tracks) < 20:
        diff = 20 - len(common_tracks)
        num_tracks_to_get_from_guest = diff // len(guest_tokens)

        for guest_tracks_dict in top_tracks_list:
            sorted_tracks = {k: v for k, v in sorted(guest_tracks_dict.items(), key=lambda item: item[1], reverse=True)}
            top_20_tracks_for_guest = [k for k in list(sorted_tracks)[:20]]
            favorite_track_candidates.update(random.sample(top_20_tracks_for_guest, num_tracks_to_get_from_guest))
        
        favorite_track_candidates.update(common_tracks)

        counter = 0
        # guarantee 20 tracks are in favorite_track_candidates
        while len(favorite_track_candidates) < 10:
            track_to_add = random.choice(group_favorite_tracks_counter.most_common()) # should be a tuple like (('Money Trees', '921310892SKJAS'), 1)
            favorite_track_candidates.add(track_to_add[0])
            counter += 1

            if counter == 50: # fail safe, in theory the random.choice could keep pulling the same track or already be in favorite_track_candidates
                break

    else:
        favorite_track_candidates = set(random.sample(common_tracks, 20))
    
    # favorite_track_candidates should have 20 tracks at this point, either all common tracks, 
    # a mix of common tracks and individual favorites, or all individual favorites

    print(favorite_track_candidates)
    track_ids = []
    favorite_artist_candidates = set()
    common_artists = set()

    for artist in group_favorite_artists_counter:
        if group_favorite_artists_counter[artist] >= 2 and len(guest_tokens) in [2,3]:
            common_artists.add(artist)
        else:
            if group_favorite_artists_counter[artist] >= (len(guest_tokens) // 2):
                common_artists.add(artist)

#    print(len(common_artists))
    if len(common_artists) < 10:
        diff = 10 - len(common_artists)
        num_artists_to_get_from_guest = diff // len(guest_tokens)

        for guest_artists_dict in top_artists_list:
            sorted_artists = {k: v for k, v in sorted(guest_artists_dict.items(), key=lambda item: item[1], reverse=True)}
            top_20_artists_for_guest = [k for k in list(sorted_artists)[:20]]
            favorite_artist_candidates.update(random.sample(top_20_artists_for_guest, num_artists_to_get_from_guest))
        
        favorite_artist_candidates.update(common_artists)

        counter = 0
        # guarantee 10 artists are in favorite_artist_candidates
        while len(favorite_artist_candidates) < 10:
            artist_to_add = random.choice(group_favorite_artists_counter.most_common()) # should be a tuple like (('Kanye West', '921310892SKJAS'), 1)
            favorite_artist_candidates.add(artist_to_add[0])
            counter += 1

            if counter == 50: # fail safe, in theory the random.choice could keep pulling the same artists or already be in favorite_artist_candidates
                break

    else:
        favorite_artist_candidates = set(random.sample(common_artists, 10))
    
    seed_artists_ids = [i[1] for i in favorite_artist_candidates]

    # collect recommendations
    recommended_tracks = spotifyObject.recommendations(country='US', seed_artists=seed_artists_ids[:5], limit=15)
    for track in recommended_tracks['tracks']:
        track_ids.append(track['id'])
    
    recommended_tracks = spotifyObject.recommendations(country='US', seed_artists=seed_artists_ids[5:], limit=15)
    for track in recommended_tracks['tracks']:
        track_ids.append(track['id'])

    # add in favorite_track_candidates
    track_ids.extend([i[1] for i in favorite_track_candidates])

#    print(track_ids)

    # shuffle tracks around
    random.shuffle(track_ids)

    # add to playlist
    spotifyObject.user_playlist_add_tracks(
        host_id, playlist_id, track_ids)


def get_user(token):
    spotifyObject = spotipy.Spotify(auth=token)

    user = spotifyObject.me()
    profile_image = "https://lh3.googleusercontent.com/eN0IexSzxpUDMfFtm-OyM-nNs44Y74Q3k51bxAMhTvrTnuA4OGnTi_fodN4cl-XxDQc" # default
    if user['images']:
        profile_image = user['images'][0]['url']
    return [user['display_name'].split()[0], user['id'], profile_image]

def get_playlist_length(token, playlist_id):
    spotifyObject = spotipy.Spotify(auth=token)
    playlist = spotifyObject.playlist_tracks(playlist_id)
    return playlist['total']

def follow_playlist(token, playlist_id):
    spotifyObject = spotipy.Spotify(auth=token)
    owner_id = spotifyObject.playlist(playlist_id)['owner']['id']
    return spotifyObject.user_playlist_follow_playlist(owner_id, playlist_id)