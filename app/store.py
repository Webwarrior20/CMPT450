UPLOADED_DATA = None
MAIN_DATABASE = None
SPOTIFY_CLIENT = None


# -----------------------------
# UPLOADED DATA
# -----------------------------
def set_uploaded_data(df):
    global UPLOADED_DATA
    UPLOADED_DATA = df


def get_uploaded_data():
    return UPLOADED_DATA


# -----------------------------
# DATABASE (SAFE + LAZY LOAD)
# -----------------------------
def get_main_database():
    global MAIN_DATABASE

    if MAIN_DATABASE is not None:
        return MAIN_DATABASE

    try:
        from utils.database import load_recent_data
        import pandas as pd

        print("⚡ Loading SMALL database subset (lazy)...")

        db = load_recent_data(6)

        if db is None or db.empty:
            print("⚠️ DB empty, using empty DataFrame")
            MAIN_DATABASE = pd.DataFrame()
            return MAIN_DATABASE

        # -----------------------------
        # 🔥 CRITICAL FIX: ensure track_uri
        # -----------------------------
        if "track_uri" not in db.columns:

            if "spotify_track_uri" in db.columns:
                db["track_uri"] = db["spotify_track_uri"]

            elif "uri" in db.columns:
                db["track_uri"] = db["uri"]

            elif "track_id" in db.columns:
                db["track_uri"] = "spotify:track:" + db["track_id"].astype(str)

            elif "id" in db.columns:
                db["track_uri"] = "spotify:track:" + db["id"].astype(str)

            else:
                print("⚠️ No track column found → creating dummy track_uri")
                db["track_uri"] = "unknown"

        MAIN_DATABASE = db

    except Exception as e:
        print(f"❌ DB load failed: {e}")
        import pandas as pd
        MAIN_DATABASE = pd.DataFrame()

    return MAIN_DATABASE


def set_main_database(df):
    global MAIN_DATABASE
    MAIN_DATABASE = df


# -----------------------------
# SPOTIFY CLIENT
# -----------------------------
def set_spotify_client(client):
    global SPOTIFY_CLIENT
    SPOTIFY_CLIENT = client


def get_spotify_client():
    return SPOTIFY_CLIENT