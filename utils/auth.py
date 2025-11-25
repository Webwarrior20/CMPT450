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
            scope="user-read-private user-top-read",
            open_browser=False,          # ⬅ prevents launching a browser
            cache_path=".spotify_cache", # ⬅ avoid re-auth every call
            requests_timeout=10,         # ⬅ avoid hanging
        )
    )

    print("Connected to Spotify Client" if spotify_client else "Unable to connect to Spotify Client")
    set_spotify_client(spotify_client)
