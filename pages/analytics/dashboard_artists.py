import dash
from dash import html, dcc, callback, Output, Input
from layout.analytics_layout import analytics_layout
from components.time_select_period import time_select_period
from app.store import get_uploaded_data, get_spotify_client
import pandas as pd

dash.register_page(__name__, path="/analytics/artists", name="Your Top Artists - Analytics")

layout = analytics_layout(
    [
        time_select_period(),
        dcc.Store(id="selected-time-period"),
        html.Div(id="artist-listing"),
    ],
    "Top Artists",
)

@callback(
    Output("artist-listing", "children"),
    Input("selected-time-period", "data"),
)
def render_top_artists(time_period):
    df = get_uploaded_data()
    sp = get_spotify_client()

    if df is None or df.empty:
        return html.Div("No data uploaded yet — upload CSV/JSON first.", className="warning")

    uri_col = next((c for c in df.columns if "spotify_track_uri" in c.lower() or "uri" in c.lower()), None)
    if not uri_col:
        return html.Div("No track URI column found in uploaded data.", className="error")

    # Time filtering
    if "ts" in df.columns:
        df = df.dropna(subset=["ts"]).copy()
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("ts")
        last = df["ts"].max()

        if time_period == "4 weeks":
            df = df[df["ts"] >= last - pd.Timedelta(weeks=4)]
        elif time_period == "6 months":
            df = df[df["ts"] >= last - pd.Timedelta(days=180)]

    # Ensure minutes column
    if "minutes" not in df.columns:
        df["minutes"] = df.get("ms_played", 0) / 60000

    # Aggregate minutes by track URI
    track_minutes = (
        df.groupby(uri_col)["minutes"]
        .sum()
        .reset_index()
    )

    # Limit to top 50 tracks before artist collapsing
    track_minutes = track_minutes.sort_values("minutes", ascending=False).head(50)

    # Convert URIs to track IDs
    track_uris = track_minutes[uri_col].tolist()
    track_ids = [uri.split(":")[-1] for uri in track_uris]

    # Batch fetch track metadata
    track_infos = sp.tracks(track_ids)["tracks"]

    # Allocate minutes to artists
    artist_minutes = {}

    for row, info in zip(track_minutes.itertuples(), track_infos):
        minutes = row.minutes

        primary_artist = info["artists"][0]
        artist_id = primary_artist["id"]

        artist_minutes[artist_id] = artist_minutes.get(artist_id, 0) + minutes

    # Sort top artists
    top_artists = sorted(artist_minutes.items(), key=lambda x: x[1], reverse=True)[:15]
    artist_ids = [artist_id for artist_id, _ in top_artists]

    # Batch fetch artist metadata
    artist_infos = sp.artists(artist_ids)["artists"]
    id_to_artist = {a["id"]: a for a in artist_infos}

    # UI rows
    items = []
    for rank, (artist_id, minutes) in enumerate(top_artists, start=1):
        info = id_to_artist.get(artist_id)

        if not info:
            continue

        name = info["name"]
        link = info["external_urls"]["spotify"]
        image = info["images"][1]["url"]

        items.append(
            html.Div(
                className="artist-item",
                children=[
                    html.Div(
                        className="artist-art-wrapper",
                        children=html.Img(
                            src=image,
                            className="artist-art",
                        ),
                    ),
                    html.Div(f"#{str(rank)}", className="artist-rank heading-3"),
                    html.Div(name, className="artist-name heading-2"),
                    html.Div(
                        className="link-artist",
                        children=html.A(
                            html.Img(
                                src="/assets/images/icon-spotify-white.png",
                                className="spotify-track-link-icon-artist",
                            ),
                            href=link,
                            target="_blank",
                        ),
                    ),
                ],
            )
        )

    return html.Div(items, className="artist-list")
