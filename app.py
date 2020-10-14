import json
import os
import os.path
import time
from os import path

from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from whitenoise import WhiteNoise

from party_actions import (create_party_playlist, generate,
                           get_playlist_length, get_user, follow_playlist)
from spotify_actions import (createPlaylist, getRecommendations, getTracks,
                             getVibes, req_auth, req_token, unfollow_playlist)

'''
App Config
'''

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

'''
Database Config
'''

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_REDIRECT_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# database
db = SQLAlchemy(app)
db.app = app

class User(db.Model):
    spotify_id = db.Column(db.String(50), primary_key=True)
    playlist_id = db.Column(db.String(40), unique=False, nullable=True)
    first_name = db.Column(db.String(20), unique=False, nullable=True)
    image = db.Column(db.String(150), unique=False, nullable=True)
    auth_token = db.Column(db.String(20), unique=False, nullable=True)
    party_id = db.Column(db.Integer, unique=False, nullable=True)
    party_on = db.Column(db.BOOLEAN, unique=False, nullable=True)


    def __init__(self, user_id, playlist_id, first_name, image, token, party_id):
        self.spotify_id = user_id
        self.playlist_id = playlist_id
        self.first_name = first_name
        self.image = image
        self.auth_token = token
        self.party_id = party_id
        self.party_on = False
#        self.host = host\

    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'spotify_id': self.spotify_id,
           'playlist_id': self.playlist_id,
           'first_name': self.first_name,
           'image': self.image,
           'party_id': self.party_id,
           'party_on': self.party_on
       }

    def __repr__(self):
        return '<User %r>' % self.spotify_id

engine = create_engine(os.environ.get('DB_REDIRECT_URI'))
db.drop_all()
if not engine.dialect.has_table(engine, 'user'):
    db.create_all()

'''
DB helper functions
'''

def get_members(party_id):
    return User.query.filter_by(party_id=party_id)


def get_parties():
    users = User.query.filter_by()
    return {user.party_id for user in users}

# Home view
@app.route('/')
@app.route('/home')
def home():
    '''
    # If authenticated, redirect to options page
    if 'token' in session:
        found_user = User.query.filter_by(auth_token=session['token']).first()
        if found_user:
            return redirect(url_for('options'))
        else:
            return render_template('home.html', title='Home')

    '''
    # Home page
    session.clear()
    return render_template('home.html', title='Home')


# Login view


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    # Redirect user to Spotify login page
    AUTH_FIRST = req_auth()
    return redirect(AUTH_FIRST)


# Callback view for Spotify API


@app.route('/callback')
def callback():
    if request.args.get('error') or not request.args.get('code'):

        # Prevents user from accessing page without going through authorization
        # steps properly
        return redirect(url_for('home'))
    else:
        # Get 'code' from Spotify request
        code = request.args.get('code')

        # Using 'code' provided by Spotify, request a user token from Spotify
        token = req_token(code)
        session['token'] = token
        session['loginTime'] = time.time()

        return redirect(url_for('options'))

@app.route('/vibes')
def vibes():
    if session.get('loginTime') and time.time() < session['loginTime'] + 1800 and session.get('token'):
        vibeData = getVibes(session['token'])
        
        songLists = [list(songSet) for songSet in vibeData[3]]
        session['songSets'] = songLists
        '''
        session['profileImage'] = vibeData[2]
        session['artistImages'] = vibeData[4]
        '''
        session['artistIDs'] = vibeData[5]
        sortedScores = {k: v for k, v in sorted(vibeData[0].items(), key=lambda item: item[1], reverse=True)}

        return render_template('vibes.html', vibeMoodList=json.dumps(sortedScores), favorite_tracks=json.dumps(vibeData[1]), profileImage=vibeData[2], artistImages=vibeData[4])
    else:
        return redirect(url_for('login'))

@app.route('/tryAgain')
def tryAgain():
    if session.get('loginTime') and time.time() < session['loginTime'] + 1800 and session.get('token'):
        vibeData = getVibes(session['token'])
        randomSongs = getTracks(session['token'], [list(songSet) for songSet in vibeData[3]])
        sortedScores = {k: v for k, v in sorted(vibeData[0].items(), key=lambda item: item[1], reverse=True)}

        return render_template('vibes.html', vibeMoodList=json.dumps(sortedScores), favorite_tracks=json.dumps(randomSongs), profileImage=vibeData[2], artistImages=vibeData[4])
    else:
        return redirect(url_for('home'))


@app.route('/vibePlaylist')
def vibePlaylist():
    vibe = request.args.get('vibe')
    if session.get('loginTime') and time.time() < session['loginTime'] + 1800 and session.get('token'):
        vibeSetMap = {'happy': 0, 'sad': 1, 'hype': 2, 'chill': 3, 'groovy': 4, 'angry': 5, 'study': 0, 'workout': 2}
        song_ids = []
        song_ids = getRecommendations(session['token'], session['artistIDs'], vibe, session['songSets'][vibeSetMap[vibe]])

        ids = [track[3] for track in song_ids]
        playlist_id = createPlaylist(session['token'], ids, vibe)
        return redirect(url_for('showPlaylist', vibe=vibe, playlist_id=playlist_id))
    else:
        return redirect(url_for('home'))   

@app.route('/showPlaylist')
def showPlaylist():
    vibe = request.args.get('vibe')
    playlist_id = request.args.get('playlist_id')

    if session.get('loginTime') and time.time() < session['loginTime'] + 1800 and session.get('token'):
        return render_template('vibePlaylist.html', vibe=vibe, playlist_id=playlist_id)
    else:
        return redirect(url_for('home'))

@app.route('/deletePlaylist')
def deletePlaylist():
    vibe = request.args.get('vibe')
    playlist_id = request.args.get('playlist_id')
    unfollow_playlist(session['token'], playlist_id)

    if vibe:
        return redirect(url_for('vibePlaylist', vibe=vibe))
    else:       
        return redirect(url_for('vibes'))

@app.route('/get_party_members')
def get_party_members():

    if session.get('spotify_id'):

#        party_id = request.args.get('party_id', 0, type=int)
        party_id = session['party_id']
        return jsonify([i.serialize for i in get_members(party_id)])

    return jsonify({'result': 'failure'})

@app.route('/get_party_ids')
def get_party_ids():

    if session.get('loginTime') and time.time() < session['loginTime'] + 1800 and session.get('token'):
        reg_ex = ""

        for id in get_parties():
            reg_ex += str(id)
            reg_ex += '|'
        
        reg_ex = reg_ex[:-1]
        return jsonify(reg_ex)

    return jsonify({'result': 'failure'})

@app.route('/options')
def options():
    return render_template('options.html')


@app.route('/create_party', methods=['GET', 'POST'])
def create_party():
    if session.get('songSets'):
        del session['songSets']
    if session.get('sortedScores'):
        del session['sortedScores']
    if session.get('artistImages'):
        del session['artistImages']
    if session.get('artistIDs'):
        del session['artistIDs']

    
    if request.method == 'POST':
        return redirect(url_for('success')) 
    else:
        
        # TO DO: get custom playlist name and description from jquery post request
        pl_name = session.get('pl_name')
        pl_desc = session.get('pl_desc')

        # Generate random 4-digit party ID
        # TO DO: check that it's unique in the database
        import random
        active_party_ids = get_parties()
        party_id = random.randint(1000,9999)
        while party_id in active_party_ids:
            party_id = random.randint(1000,9999)

        # Store party ID in session
        session['party_id'] = party_id

        session['host_status'] = True

        party_info = create_party_playlist(session.get('token'), pl_name, pl_desc)

        host_first_name = str(party_info[0])
        host_spotify_id = str(party_info[1])
        party_playlist_id = str(party_info[2])
        host_image = str(party_info[3])

        # Store playlist ID in session
        session['spotify_id'] = host_spotify_id
        session['party_playlist_id'] = party_playlist_id

        found_user = User.query.filter_by(spotify_id=host_spotify_id).first()

        if found_user:
            found_user.auth_token = session.get('token')
            found_user.party_id = party_id
            found_user.playlist_id = party_playlist_id
            found_user.party_on = False
#            found_user.host = True
            db.session.commit()

        else:
            user = User(host_spotify_id, party_playlist_id, host_first_name, host_image, session.get('token'), party_id)
            user.party_on = False
            db.session.add(user)
            db.session.commit()

        return redirect(url_for('lobby'))



@app.route('/lobby', methods=['GET', 'POST'])
def lobby():

    found_user = User.query.filter_by(spotify_id=session['spotify_id']).first()
    found_user.party_on = False
    db.session.commit()

    for party_member in get_members(session['party_id']):
        if party_member.party_on or get_playlist_length(party_member.auth_token, party_member.playlist_id) > 0:
            found_user.party_on = True
            db.session.commit()
            return render_template('party.html', playlist_id=party_member.playlist_id, party_id=session['party_id'], party_members = get_members(session['party_id'])) 

    # Check if user is a host or not 
    return render_template('lobby.html', host=session['host_status'], party_id=session['party_id'], party_members = get_members(session['party_id']))

@app.route('/start_party', methods=['GET', 'POST'])
def start_party():
    if session.get('loginTime') and time.time() < session['loginTime'] + 1800 and session.get('token'):

        members = get_members(session['party_id'])

        guest_tokens = [member.auth_token for member in members]

        generate(session['token'], guest_tokens, session['party_playlist_id'])

        user = User.query.filter_by(party_id=session['party_id']).first()
        user.party_on = True
        db.session.commit()


        return render_template('party.html', playlist_id=session['party_playlist_id'], party_id=session['party_id'], party_members = get_members(session['party_id']))

    else:
        return redirect(url_for('login'))

@app.route('/save_party', methods=['GET', 'POST'])
def save_party():
    if session.get('loginTime') and time.time() < session['loginTime'] + 1800 and session.get('token'):
        party_playlist_id = request.args.get('playlist_id')
        follow_playlist(session['token'], party_playlist_id)

        return render_template('party.html', playlist_id=session['party_playlist_id'], party_id=session['party_id'], party_members = get_members(session['party_id']))

    else:
        return redirect(url_for('login'))      

@app.route('/join_party', methods=['GET', 'POST'])
def join_party():
    if session.get('loginTime') and time.time() < session['loginTime'] + 1800 and session.get('token'):

        if session.get('songSets'):
            del session['songSets']
        if session.get('sortedScores'):
            del session['sortedScores']
        if session.get('artistImages'):
            del session['artistImages']
        if session.get('artistIDs'):
            del session['artistIDs']
        

        if request.method == 'POST':

            # TO DO: get custom playlist name and description from jquery post request
            #pl_name = session.get('pl_name')
            #pl_desc = session.get('pl_desc')

            # Store party ID in session
            party_id = int(float(request.form.get('party_code')))
            session['party_id'] = party_id

            session['host_status'] = False
            token = session.get('token')

            spotify_info = get_user(token)

            user_first_name = str(spotify_info[0])
            user_spotify_id = str(spotify_info[1])
            profile_image = str(spotify_info[2]) #TO DO

            session['spotify_id'] = user_spotify_id

            found_user = User.query.filter_by(spotify_id=user_spotify_id).first()

            party_playlist_id = get_members(party_id)[0].playlist_id

            if found_user:
                found_user.party_id = party_id
                found_user.playlist_id = party_playlist_id
                found_user.image = profile_image
                db.session.commit()

            else:
                user = User(user_spotify_id, party_playlist_id, user_first_name, profile_image, session.get('token'), party_id)
                db.session.add(user)
                db.session.commit()

            return redirect(url_for('lobby'))

        else:

            reg_ex = ""

            for id in get_parties():
                reg_ex += str(id)
                reg_ex += '|'
            
            reg_ex = reg_ex[:-1]

            return render_template('join_party.html', reg_ex=reg_ex)
    else:
        return redirect(url_for('login'))        


# Update modal form (backend page)


@app.route('/update', methods=["GET", "POST"])
def update():

    if request.method == 'POST':
        #TODO
        # Get custom playlist name from jquery post
        pl_name = request.form.get('name')
        pl_desc = request.form.get('desc')

        # Store custom info into session
        session['pl_name'] = pl_name
        session['pl_desc'] = pl_desc

        return jsonify({'result': 'success'})

    if request.method == 'GET':
        return redirect(url_for('home'))
