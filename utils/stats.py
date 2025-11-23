import pandas as pd
from app.store import get_uploaded_data

# ---------------------------------------------------------
# Get Cleaned Uploaded DataFrame
# ---------------------------------------------------------
def get_uploaded_dataframe() -> pd.DataFrame:
    """
    Central function used by ALL analytics pages.
    Ensures the app always receives a valid DataFrame.
    """
    df = get_uploaded_data()
    if df is None or not isinstance(df, pd.DataFrame):
        return pd.DataFrame()

    return df


# ---------------------------------------------------------
# Overview Page Statistics
# ---------------------------------------------------------
def compute_overview_stats(df: pd.DataFrame):
    """
    Computes summary statistics for Overview page.
    Fully tolerant of missing or differently named columns.
    """

    if df is None or df.empty:
        return _empty_stats()

    # --- Track column handling ---
    track_col = _first(df, ["track", "track_name", "master_metadata_track_name"])
    artist_col = _first(df, ["artist", "artist_name", "master_metadata_album_artist_name"])
    duration_col = _first(df, ["duration_ms", "ms_played"])
    genre_col = _first(df, ["artist_genres", "genres", "genre"])

    # ---------- Top Genre ----------
    top_genre = "N/A"
    if genre_col:
        genre_series = (
            df[genre_col]
            .dropna()
            .astype(str)
            .str.split(",")
            .explode()
            .str.strip()
        )
        if not genre_series.empty:
            top_genre = genre_series.value_counts().idxmax()

    # ---------- Top Artist ----------
    if artist_col:
        top_artist = df[artist_col].dropna().astype(str).value_counts().idxmax()
    else:
        top_artist = "Unknown"

    # ---------- Unique Tracks ----------
    discoveries = df[track_col].nunique() if track_col else 0

    # ---------- Average Song Duration ----------
    if duration_col:
        avg_ms = df[duration_col].mean()
        avg_sec = int(avg_ms / 1000)
        avg_length = f"{avg_sec//60}:{avg_sec%60:02d}"
    else:
        avg_length = "0:00"

    # ---------- Total Listening Hours ----------
    listening_time_hours = (
        round(df[duration_col].sum() / 3_600_000, 2)
        if duration_col else 0
    )

    # ---------- Listening Streak ----------
    streak = compute_listening_streak(df)

    return {
        "top_genre": top_genre,
        "top_artist": top_artist,
        "discoveries": discoveries,
        "avg_length": avg_length,
        "listening_time_hours": listening_time_hours,
        "streak": streak,
    }


# ---------------------------------------------------------
# Listen Streak
# ---------------------------------------------------------
def compute_listening_streak(df: pd.DataFrame):
    """
    Computes consecutive-day listening streak using ts or played_at.
    Works even when timestamps are missing or stored differently.
    """

    # Find timestamp column
    ts_col = _first(df, ["played_at", "ts", "timestamp"])

    if not ts_col:
        return 0

    try:
        temp = df.dropna(subset=[ts_col]).copy()

        # Convert to datetime if not already
        temp[ts_col] = pd.to_datetime(temp[ts_col], errors="coerce")
        temp["date_only"] = temp[ts_col].dt.date

        unique_days = sorted(temp["date_only"].dropna().unique())
        if not unique_days:
            return 0

        # Calculate consecutive streak
        streak = 1
        longest = 1
        for i in range(1, len(unique_days)):
            if (unique_days[i] - unique_days[i - 1]).days == 1:
                streak += 1
                longest = max(longest, streak)
            else:
                streak = 1

        return longest

    except Exception:
        return 0


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def _first(df: pd.DataFrame, candidates: list):
    """Returns the first existing column from a list of possible names."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _empty_stats():
    """Fallback empty stats dictionary."""
    return {
        "top_genre": "N/A",
        "top_artist": "N/A",
        "discoveries": 0,
        "avg_length": "0:00",
        "listening_time_hours": 0,
        "streak": 0,
    }



def get_mock_stats():
    return {
        "top_genre": "Pop",
        "top_artist": "The Weeknd",
        "listening_streak": 45,
        "new_discoveries": 342,
        "avg_song_length": "3:24",
        "listening_hours": 847,
    }
