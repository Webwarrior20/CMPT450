from utils.database import load_from_db, db_has_data

UPLOADED_DATA = None


def set_uploaded_data(df):
    global UPLOADED_DATA
    UPLOADED_DATA = df


def get_uploaded_data():
    global UPLOADED_DATA

    # 1. If uploaded in-session → use it
    if UPLOADED_DATA is not None:
        return UPLOADED_DATA

    # 2. If DB has saved history → load from DB automatically
    if db_has_data():
        print("📦 Loading data from SQLite DB…")
        return load_from_db()

    # 3. Otherwise empty state
    return None



# Spotify Client
def set_spotify_client(client):
    global SPOTIFY_CLIENT
    SPOTIFY_CLIENT = client


def get_spotify_client():
    return SPOTIFY_CLIENT
