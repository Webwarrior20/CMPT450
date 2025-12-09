import pandas as pd
from app.store import get_uploaded_data

# Get Cleaned Uploaded DataFrame
def get_uploaded_dataframe() -> pd.DataFrame:
    df = get_uploaded_data()
    if df is None or not isinstance(df, pd.DataFrame):
        return pd.DataFrame()
    return df

# ---------------------------------------------------------
# Get Cleaned Uploaded DataFrame Filtered to Songs the user Played
# Linked by track_uri
# ---------------------------------------------------------
def get_combined_listened_dataframe() -> pd.DataFrame:
    df = get_uploaded_dataframe()
    if df is None or df.empty:
        return pd.DataFrame()

    duration_col = _first(df, ["duration_ms", "ms_played"])
    if not duration_col:
        return pd.DataFrame()

    listened_df = df[df[duration_col] > 0].copy()
    return listened_df

# Overview Page Statistics
def compute_overview_stats(df: pd.DataFrame):
    if df is None or df.empty:
        return _empty_stats()

    track_col = _first(df, ["track", "track_name", "master_metadata_track_name"])
    artist_col = _first(df, ["artist", "artist_name", "master_metadata_album_artist_name"])
    duration_col = _first(df, ["duration_ms", "ms_played"])
    genre_col = _first(df, ["artist_genres", "genres", "genre"])

    # Top genre
    top_genre = "N/A"
    if genre_col:
        series = (
            df[genre_col]
            .dropna()
            .astype(str)
            .str.split(",")
            .explode()
            .str.strip()
        )
        if not series.empty:
            top_genre = series.value_counts().idxmax()

    # Top artist
    if artist_col:
        top_artist = df[artist_col].dropna().astype(str).value_counts().idxmax()
    else:
        top_artist = "Unknown"

    # Discoveries
    discoveries = df[track_col].nunique() if track_col else 0

    # Average length
    if duration_col:
        avg_ms = df[duration_col].mean()
        avg_sec = int(avg_ms / 1000)
        avg_length = f"{avg_sec // 60}:{avg_sec % 60:02d}"
    else:
        avg_length = "0:00"

    # Total hours
    listening_time_hours = round(df[duration_col].sum() / 3_600_000, 2) if duration_col else 0

    # Streak
    streak = compute_listening_streak(df)

    return {
        "top_genre": top_genre,
        "top_artist": top_artist,
        "discoveries": discoveries,
        "avg_length": avg_length,
        "listening_time_hours": listening_time_hours,
        "streak": streak,
    }


# Listen Streak
def compute_listening_streak(df: pd.DataFrame):
    ts_col = _first(df, ["played_at", "ts", "timestamp"])
    if not ts_col:
        return 0

    try:
        temp = df.dropna(subset=[ts_col]).copy()
        temp[ts_col] = pd.to_datetime(temp[ts_col], errors="coerce")
        temp["date_only"] = temp[ts_col].dt.date

        unique_days = sorted(temp["date_only"].dropna().unique())
        if not unique_days:
            return 0

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


# Helpers
def _first(df: pd.DataFrame, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _empty_stats():
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

def get_first_listen_date(df: pd.DataFrame):
    ts_col = _first(df, ["played_at", "ts", "timestamp"])
    if not ts_col:
        return "N/A"
    try:
        df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
        first_date = df[ts_col].min()
        if pd.isna(first_date):
            return "N/A"
        return first_date.strftime("%B %d, %Y")
    except Exception:
        return "N/A"

def get_total_listening_time(df: pd.DataFrame):
    duration_col = _first(df, ["duration_ms", "ms_played"])
    return round(df[duration_col].sum() / 3_600_000, 2) if duration_col else 0

def get_most_listened_day(df: pd.DataFrame):
    """
    Find out which day of the week the user listens to music the most.
    """
    ts_col = _first(df, ["played_at", "ts", "timestamp"])
    if not ts_col:
        return "N/A"
    try:
        df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
        df["weekday"] = df[ts_col].dt.day_name()
        most_listened_day = df["weekday"].value_counts().idxmax()
        return most_listened_day
    except Exception:
        return "N/A"

def get_most_listened_hour(df: pd.DataFrame):
    """
    Returns an array of hours (0-23) during which the user listens to music the most sorted from most to least.
    """
    ts_col = _first(df, ["played_at", "ts", "timestamp"])
    if not ts_col:
        return []
    try:
        df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
        df["hour"] = df[ts_col].dt.hour
        hour_counts = df["hour"].value_counts().sort_values(ascending=False)
        return hour_counts.index.tolist()
    except Exception:
        return []

def get_most_listened_overall_day(df: pd.DataFrame):
    """
    Find out which specific date the user listened to the most music.
    Returns value a tuple of (date string, total duration in ms).
    """
    ts_col = _first(df, ["played_at", "ts", "timestamp"])
    duration_col = _first(df, ["duration_ms", "ms_played"])
    if not ts_col or not duration_col:
        return ("N/A", 0)
    try:
        df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
        df["date_only"] = df[ts_col].dt.date
        daily_listening = df.groupby("date_only", observed=False)[duration_col].sum()
        if daily_listening.empty:
            return ("N/A", 0)
        most_listened_date = daily_listening.idxmax()
        total_duration = daily_listening.max()
        return (most_listened_date.strftime("%B %d, %Y"), total_duration)
    except Exception:
        return ("N/A", 0)