import dash
import pandas as pd
from dash import html, dcc, callback, Output, Input
from layout.analytics_layout import analytics_layout
from components.time_select_period import time_select_period
from app.store import get_uploaded_data, get_spotify_client

dash.register_page(__name__, path="/analytics/tracks", name="Your Top Tracks - Analytics")

layout = analytics_layout(
    [
        time_select_period(),
        html.Div(
            className="track-list",
            children=[
                html.Div(
                    className="track-item",
                    children=[
                        html.Div(
                            children=[
                                html.Div("#", className="track-rank body bold"),
                                html.Div(),
                                html.Div("Title", className="track-title body bold")
                            ],
                            className="track-main-info",
                        ),
                        html.Div("Artist", className="track-artist body bold"),
                        html.Div("Album", className="track-album body bold"),
                        html.Div(
                            className="link",
                        ),
                    ],
                )
            ],
        ),
        dcc.Store(id="selected-time-period"),
        html.Div(id="track-listing"),
    ],
    "Top Tracks",
)


@callback(
    Output("track-listing", "children"),
    Input("selected-time-period", "data"),
)
def render_tracks(time_period):
    spotipy_client = get_spotify_client()
    df = get_uploaded_data()

    if df is None or df.empty:
        return html.Div("Upload your Spotify data first.", style={"padding": "2rem"})

    uri_col = next((c for c in df.columns if "uri" in c.lower()), None)

    # Time filtering
    if "ts" in df.columns:
        df = df.dropna(subset=["ts"])
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("ts")

        last = df["ts"].max()

        if time_period == "4 weeks":
            df = df[df["ts"] >= last - pd.Timedelta(weeks=4)]
        elif time_period == "6 months":
            df = df[df["ts"] >= last - pd.Timedelta(days=180)]

    # Count plays per track
    ranked = (
        df.groupby(uri_col)
        .size()
        .reset_index(name="plays")
        .sort_values("plays", ascending=False)
        .head(50)
    )

    track_uris = ranked[uri_col].tolist()
    track_ids = [uri.split(":")[-1] for uri in track_uris]

    track_infos = spotipy_client.tracks(track_ids)["tracks"]
    id_to_info = {info["id"]: info for info in track_infos}

    items = []

    # Build UI rows
    for rank, row in enumerate(ranked.itertuples(), start=1):
        uri = getattr(row, uri_col)
        plays = row.plays

        track_id = uri.split(":")[-1]
        info = id_to_info.get(track_id)

        if not info:
            continue

        track_name = info["name"]
        track_link = info["external_urls"]["spotify"]
        artist = ", ".join(a["name"] for a in info["artists"])
        album = info["album"]["name"]
        album_art_url = info["album"]["images"][-2]["url"]

        items.append(
            html.Div(
                className="track-list",
                children=[
                    html.Div(
                        className="track-item",
                        children=[
                            html.Div(
                                children=[
                                    html.Div(str(rank), className="track-rank heading-3"),
                                    html.Img(
                                        src=album_art_url,
                                        className="track-album-art",
                                    ),
                                    html.Div(track_name, className="track-title heading-4")
                                ],
                                className="track-main-info",
                            ),
                            html.Div(artist, className="track-artist body"),
                            html.Div(album, className="track-album body"),
                            html.Div(
                                className="link",
                                children=html.A(
                                    html.Img(
                                        src="/assets/images/icon-spotify-white.png",
                                        className="spotify-track-link-icon",
                                    ),
                                    href=track_link,
                                    target="_blank",
                                ),
                            ),
                        ],
                    )
                ],
            )
        )

    return html.Div(items, className="track-list")
