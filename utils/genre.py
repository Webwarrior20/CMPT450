from app.store import get_uploaded_data, get_main_database
import pandas as pd


def clean_genres(genre_value):
    if pd.isna(genre_value):
        return []
    if isinstance(genre_value, list):
        return genre_value
    if isinstance(genre_value, str):
        try:
            import ast
            parsed = ast.literal_eval(genre_value)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return [genre_value]
    return []


def get_genre_data(time_period):
    lh = get_uploaded_data()
    if lh is None or len(lh) == 0:
        return pd.DataFrame()

    if "ts" not in lh.columns:
        return pd.DataFrame()

    # Convert timestamp and sort
    lh = lh.dropna(subset=["ts"]).copy()
    lh["ts"] = pd.to_datetime(lh["ts"], errors="coerce")
    lh = lh.dropna(subset=["ts"]).sort_values("ts")

    if lh.empty:
        return pd.DataFrame()

    last_ts = lh["ts"].max()

    # Apply time period filtering
    if time_period == "4 weeks":
        lh = lh[lh["ts"] >= last_ts - pd.Timedelta(weeks=4)]
    elif time_period == "6 months":
        lh = lh[lh["ts"] >= last_ts - pd.Timedelta(days=180)]
    elif time_period == "12 months":
        lh = lh[lh["ts"] >= last_ts - pd.Timedelta(days=365)]

    db = get_main_database()
    if db is None or len(db) == 0:
        return pd.DataFrame()

    # Merge metadata
    merged = lh.merge(
        db,
        left_on="spotify_track_uri",
        right_on="track_uri",
        how="left"
    )

    # Parse genres
    merged["parsed_genres"] = merged["artist_genres"].apply(clean_genres)

    exploded = merged.explode("parsed_genres")

    # If comma-separated string, take only the first value
    exploded["parsed_genres"] = exploded["parsed_genres"].apply(
        lambda g: g.split(",")[0].strip() if isinstance(g, str) else g
    )

    # Remove invalid genres
    exploded = exploded.dropna(subset=["parsed_genres"])
    exploded = exploded[exploded["parsed_genres"] != ""]
    exploded = exploded[exploded["parsed_genres"] != "[]"]

    return exploded


def get_genre_counts(exploded):
    if exploded.empty:
        return pd.DataFrame()

    genre_counts = (
        exploded["parsed_genres"]
        .value_counts()
        .reset_index()
    )
    genre_counts.columns = ["genre", "genre_count"]

    return genre_counts


def get_top5_breakdown(genre_counts):
    if genre_counts.empty:
        return []

    total = genre_counts["genre_count"].sum()

    top5 = genre_counts.head(5).copy()
    top5["pct"] = (top5["genre_count"] / total * 100).round(1)

    other_count = genre_counts["genre_count"].iloc[5:].sum()
    other_pct = round(other_count / total * 100, 1)

    breakdown = top5.to_dict("records")

    if other_count > 0:
        breakdown.append({
            "genre": "Other",
            "genre_count": other_count,
            "pct": other_pct
        })

    return breakdown


def get_genre_stats(genre_counts):
    if genre_counts.empty:
        return None, None, None, None

    total = genre_counts["genre_count"].sum()

    most_played_genre = genre_counts.iloc[0]["genre"]
    most_played_pct = round(
        genre_counts.iloc[0]["genre_count"] / total * 100, 1
    )

    genre_diversity = len(genre_counts)
    avg_per_genre = round(total / genre_diversity, 1)

    return most_played_genre, most_played_pct, genre_diversity, avg_per_genre
