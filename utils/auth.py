import spotipy
from dotenv import dotenv_values
from spotipy.oauth2 import SpotifyOAuth
from app.store import set_spotify_client

config = dotenv_values(".env")

def spotify_client_connection():
    spotify_client = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=config["SPOTIFY_CLIENT_ID"],
            client_secret=config["SPOTIFY_CLIENT_SECRET"],
            redirect_uri=config["SPOTIFY_REDIRECT_URI"],
        ))

    print("Connected to Spotify Client" if spotify_client else "Unable to connect to Spotify Client")
    set_spotify_client(spotify_client)