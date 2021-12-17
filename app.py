from flask import Flask,render_template,redirect,request,make_response,url_for,jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from decouple import config
import json
import random

app = Flask(__name__)
app.sp = None


perpage = 15

@app.route('/')
def red():
    return redirect(url_for('index',page=0))

@app.route('/<int:page>')
def index(page:int):
    if app.sp is None:
        return redirect(url_for('login'))
    else:
        user = app.sp.current_user()
        tracks = app.sp.current_user_top_tracks(limit=perpage, offset=page*perpage)
        return render_template('index.html',user=user,top_tracks=tracks['items'],duration=0,p=page,end=tracks['total']%perpage)





@app.route('/startgame')
def startgame():
    #If No SP object is created , redirect to login
    if app.sp is None:
        return redirect(url_for('login'))
    user = app.sp.current_user()
    retdb = {}
    retdb['quiz'] = create_questions()
    retdb['user'] = user
    return render_template('gameTemplate.html',ret=retdb)



#### Question Creation Sub-definitions ####
def getAudioQuestion(track):
    retDict = {}
    retDict['question'] = 'What is the name of this song?'
    retDict['answer'] = track[0]['name']
    retDict['images'] = [t['album']['images'][0]['url'] for t in track]
    retDict['audio'] = track[0]['preview_url']
    retDict['options'] = [t['name'] for t in track]
    return retDict


def getCoverQuestion(track):
    pass

def getAlbumQuestion(track):
    pass

def getPopularityQuestion(track):
    retDict = {}
    retDict['question'] = 'What is the name of this song?'
    pops = sorted({(t['popularity'],t['name']) for t in track})
    retDict['answer'] = pops[-1][1]
    retDict['options'] = [{'name':t['name'],'artist':t['artists'][0]['name'],'image':t['album']['images'][0]['url']} for t in track]
    return retDict


def create_questions():
    alltracks = app.sp.current_user_top_tracks(limit=100)
    tracks = alltracks['items']
    questions = [getAudioQuestion,getPopularityQuestion]
    q = random.choices(questions,k=10)([random.choices(tracks,k=3)])
    return q





### Login CallBack Functions to connect wih spotify
@app.route('/login',methods=['GET'])
def login():
    print("here tooooo")
    auth = SpotifyOAuth(
        scope=config("SCOPE"),
        client_id=config("SPOTIPY_CLIENT_ID"),
        client_secret=config("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=config("REDIRECT_URI")
    )
    auth_url = auth.get_authorize_url()
    return redirect(auth_url)


@app.route('/auth/callback',methods=['GET','POST'])
def auth_callback():
    auth = SpotifyOAuth(
        scope=config("SCOPE"),
        client_id=config("SPOTIPY_CLIENT_ID"),
        client_secret=config("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=config("REDIRECT_URI")
    )
    token = auth.get_access_token(request.args.get('code'))
    print(token)
    app.sp = spotipy.Spotify(auth=token['access_token'])
    res = make_response(redirect(url_for('index',page=0)))
    res.set_cookie('session',token['access_token'])
    return res


if __name__ == '__main__':
    app.run(debug=True)
