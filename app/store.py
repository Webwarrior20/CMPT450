UPLOADED_DATA = None
MAIN_DATABASE = None


def set_uploaded_data(df):
    global UPLOADED_DATA
    UPLOADED_DATA = df


def get_uploaded_data():
    return UPLOADED_DATA


def set_main_database(db):
    global MAIN_DATABASE
    MAIN_DATABASE = db


def get_main_database():
    return MAIN_DATABASE


# Spotify Client
def set_spotify_client(client):
    global SPOTIFY_CLIENT
    SPOTIFY_CLIENT = client


def get_spotify_client():
    return SPOTIFY_CLIENT
