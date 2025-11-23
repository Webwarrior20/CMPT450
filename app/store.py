UPLOADED_DATA = None
SPOTIFY_CLIENT = None


# Uploaded Data
def set_uploaded_data(data):
    global UPLOADED_DATA
    UPLOADED_DATA = data


def get_uploaded_data():
    return UPLOADED_DATA


# Spotify Client
def set_spotify_client(client):
    global SPOTIFY_CLIENT
    SPOTIFY_CLIENT = client


def get_spotify_client():
    return SPOTIFY_CLIENT
