import dash
from dash import html, dcc, callback, Output, Input
from layout.analytics_layout import analytics_layout
from components.time_select_period import time_select_period
from app.store import get_uploaded_data
import pandas as pd

dash.register_page(__name__, path="/analytics/tracks", name="Your Top Tracks - Analytics")

# ------------------------------------------------------
# Page Layout
# ------------------------------------------------------
layout = analytics_layout(
    [
        time_select_period(),
        dcc.Store(id="selected-time-period"),
        html.Div(id="track-listing"),
    ],
    "Top Tracks",
)

# ------------------------------------------------------
# Single Valid Callback
# ------------------------------------------------------
@callback(
    Output("track-listing", "children"),
    Input("selected-time-period", "data"),
)
def render_tracks(time_period):

    df = get_uploaded_data()

    if df is None or df.empty:
        return html.Div("Upload your Spotify data first.", style={"padding": "2rem"})

    # -------------------------------
    # Detect columns
    # -------------------------------
    track_col = next((c for c in df.columns if "track" in c.lower()), None)
    artist_col = next((c for c in df.columns if "artist" in c.lower()), None)
    album_col = next((c for c in df.columns if "album" in c.lower()), None)
    uri_col = next((c for c in df.columns if "uri" in c.lower()), None)

    # -------------------------------
    # Time filtering
    # -------------------------------
    if "ts" in df.columns:
        df = df.dropna(subset=["ts"])
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("ts")

        last = df["ts"].max()

        if time_period == "4 weeks":
            df = df[df["ts"] >= last - pd.Timedelta(weeks=4)]
        elif time_period == "6 months":
            df = df[df["ts"] >= last - pd.Timedelta(days=180)]

    # -------------------------------
    # Count plays per track
    # -------------------------------
    ranked = (
        df.groupby(track_col)
        .size()
        .reset_index(name="plays")
        .sort_values("plays", ascending=False)
        .head(50)
    )

    items = []

    # -------------------------------
    # Build UI rows
    # -------------------------------
    for rank, row in enumerate(ranked.itertuples(), start=1):
        track_name = getattr(row, track_col)
        plays = row.plays
        sample = df[df[track_col] == track_name].iloc[0]

        artist = sample.get(artist_col, "")
        album = sample.get(album_col, "")

        # Default square placeholder art
        album_art_url = "https://i.scdn.co/image/ab67616d00001e02111111111111111111111111"

        items.append(
            html.Div(
                className="track-item",
                children=[
                    html.Div(str(rank), className="track-rank"),

                    html.Div(
                        className="album-art-wrapper",
                        children=[
                            html.Img(src=album_art_url, className="album-art-image")
                        ],
                    ),

                    html.Div(
                        className="track-title-artist",
                        children=[
                            html.Div(track_name, className="track-title"),
                            html.Div(artist, className="track-artist"),
                        ],
                    ),

                    html.Div(album, className="track-album"),

                    html.Div(f"{plays} plays", className="track-plays"),
                ],
            )
        )

    return html.Div(items, className="track-list")
