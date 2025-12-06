from app.store import get_uploaded_data, get_main_database
import pandas as pd

AUDIO_FEATURES = [
    "danceability",
    "energy",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "valence"
]


def compute_audio_profile(df):
    if df.empty:
        return None

    feature_df = df[AUDIO_FEATURES].apply(pd.to_numeric, errors="coerce").dropna()

    if feature_df.empty:
        return None

    return (feature_df.mean() * 100).round(1)


def get_feature_data(time_period):
    lh = get_uploaded_data()
    if lh is None or len(lh) == 0:
        return pd.DataFrame()

    if "ts" not in lh.columns:
        return pd.DataFrame()

    lh = lh.dropna(subset=["ts"]).copy()
    lh["ts"] = pd.to_datetime(lh["ts"], errors="coerce")
    lh = lh.dropna(subset=["ts"]).sort_values("ts")

    if lh.empty:
        return pd.DataFrame()

    last_ts = lh["ts"].max()

    # Apply time filtering
    if time_period == "4 weeks":
        lh = lh[lh["ts"] >= last_ts - pd.Timedelta(weeks=4)]
    elif time_period == "6 months":
        lh = lh[lh["ts"] >= last_ts - pd.Timedelta(days=180)]
    elif time_period == "12 months":
        lh = lh[lh["ts"] >= last_ts - pd.Timedelta(days=365)]

    db = get_main_database()
    if db is None or len(db) == 0:
        return pd.DataFrame()

    # Merge with metadata (audio features live here)
    merged = lh.merge(
        db,
        left_on="spotify_track_uri",
        right_on="track_uri",
        how="left"
    )

    for col in AUDIO_FEATURES:
        merged[col] = pd.to_numeric(merged[col], errors="coerce")

    return merged
