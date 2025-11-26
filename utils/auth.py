import spotipy
from dotenv import dotenv_values
from spotipy.oauth2 import SpotifyClientCredentials
from app.store import set_spotify_client

config = dotenv_values(".env")

def spotify_client_connection():
    spotify_client = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=config["SPOTIFY_CLIENT_ID"],
            client_secret=config["SPOTIFY_CLIENT_SECRET"],
        )
    )

    try:
        spotify_client.search("test", type="track", limit=1)
        print("Spotify client connected successfully")
        set_spotify_client(spotify_client)
    except Exception as e:
        print("Failed to connect to Spotify client")
        print(str(e))
