import dash
from dash import html, dcc, callback, Output, Input
from layout.analytics_layout import analytics_layout
from components.time_select_period import time_select_period
from app.store import get_uploaded_data

dash.register_page(__name__, path="/analytics/tracks", name="Your Top Tracks - Analytics")


def layout():
    return analytics_layout(
        [
            time_select_period(),
            html.Div(id="track-listing"),   # will render dynamically
            dcc.Store(id="selected-time-period"),
        ],
        "Top Tracks",

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
def on_time_period_change_tracks(time_period):
    if time_period is None:
        time_period = "4 weeks"

    # Placeholder data:
    track_list = [
        {
            "song": "Juna",
            "artist": "Clairo",
            "album": "Charm",
            "link": "https://open.spotify.com/track/2mWfVxEo4xZYDaz0v7hYrN",
            "album-art-link": "https://i.scdn.co/image/ab67616d0000b273193c2fafdce8f116b5ca0a78"
        },
        {
            "song": "Juna",
            "artist": "Clairo",
            "album": "Charm",
            "link": "https://open.spotify.com/track/2mWfVxEo4xZYDaz0v7hYrN",
            "album-art-link": "https://i.scdn.co/image/ab67616d0000b273193c2fafdce8f116b5ca0a78"
        },
        {
            "song": "Juna",
            "artist": "Clairo",
            "album": "Charm",
            "link": "https://open.spotify.com/track/2mWfVxEo4xZYDaz0v7hYrN",
            "album-art-link": "https://i.scdn.co/image/ab67616d0000b273193c2fafdce8f116b5ca0a78"
        },
        {
            "song": "Juna",
            "artist": "Clairo",
            "album": "Charm",
            "link": "https://open.spotify.com/track/2mWfVxEo4xZYDaz0v7hYrN",
            "album-art-link": "https://i.scdn.co/image/ab67616d0000b273193c2fafdce8f116b5ca0a78"
        },
        {
            "song": "Juna",
            "artist": "Clairo",
            "album": "Charm",
            "link": "https://open.spotify.com/track/2mWfVxEo4xZYDaz0v7hYrN",
            "album-art-link": "https://i.scdn.co/image/ab67616d0000b273193c2fafdce8f116b5ca0a78"
        },
        {
            "song": "Juna",
            "artist": "Clairo",
            "album": "Charm",
            "link": "https://open.spotify.com/track/2mWfVxEo4xZYDaz0v7hYrN",
            "album-art-link": "https://i.scdn.co/image/ab67616d0000b273193c2fafdce8f116b5ca0a78"
        },
        {
            "song": "Juna",
            "artist": "Clairo",
            "album": "Charm",
            "link": "https://open.spotify.com/track/2mWfVxEo4xZYDaz0v7hYrN",
            "album-art-link": "https://i.scdn.co/image/ab67616d0000b273193c2fafdce8f116b5ca0a78"
        },
        {
            "song": "Juna",
            "artist": "Clairo",
            "album": "Charm",
            "link": "https://open.spotify.com/track/2mWfVxEo4xZYDaz0v7hYrN",
            "album-art-link": "https://i.scdn.co/image/ab67616d0000b273193c2fafdce8f116b5ca0a78"
        },
        {
            "song": "Juna",
            "artist": "Clairo",
            "album": "Charm",
            "link": "https://open.spotify.com/track/2mWfVxEo4xZYDaz0v7hYrN",
            "album-art-link": "https://i.scdn.co/image/ab67616d0000b273193c2fafdce8f116b5ca0a78"
        },        {
            "song": "Juna",
            "artist": "Clairo",
            "album": "Charm",
            "link": "https://open.spotify.com/track/2mWfVxEo4xZYDaz0v7hYrN",
            "album-art-link": "https://i.scdn.co/image/ab67616d0000b273193c2fafdce8f116b5ca0a78"
        }
    ]

    return html.Div(
        className="track-list",
        children=[
            html.Div(
                className="track-item",
                children=[
                    html.Div(
                        children=[
                            html.Div(str(rank), className="track-rank heading-3"),
                            html.Img(
                                src=track["album-art-link"],
                                className="track-album-art",
                            ),
                            html.Div(track["song"], className="track-title heading-4")
                        ],
                        className="track-main-info",
                    ),
                    html.Div(track["artist"], className="track-artist body"),
                    html.Div(track["album"], className="track-album body"),
                    html.Div(
                        className="link",
                        children=html.A(
                            html.Img(
                                src="/assets/images/icon-spotify-white.png",
                                className="spotify-track-link-icon",
                            ),
                            href=track["link"],
                            target="_blank",
                        ),
                    ),
                ],
            )
            for rank, track in enumerate(track_list, start=1)
        ],
    )


# ---------- CALLBACK: RENDER TRACK LIST ----------
@callback(
    Output("track-listing", "children"),
    Input("selected-time-period", "data"),
)
def render_tracks(time_period):

    df = get_uploaded_data()

    # No upload yet
    if df is None or df.empty:
        return html.Div(
            "No data uploaded yet. Upload a CSV or JSON first.",
            className="body",
            style={"padding": "2rem"}
        )

    # Identify possible column names
    track_col = next((c for c in df.columns if c.lower() in ["track", "track_name", "master_metadata_track_name"]), None)
    artist_col = next((c for c in df.columns if "artist" in c.lower()), None)
    album_col = next((c for c in df.columns if "album" in c.lower()), None)

    # If no track column → can't render
    if not track_col:
        return html.Div("Track data missing from uploaded file.", style={"padding": "2rem"})

    # Group by track for ranking
    track_counts = df.groupby(track_col).size().reset_index(name="plays")
    track_counts = track_counts.sort_values(by="plays", ascending=False).head(50)

    track_items = []

    for rank, row in enumerate(track_counts.itertuples(), start=1):
        track_name = getattr(row, track_col)
        plays = row.plays
        artist = ""
        album = ""

        # Get a matching sample row for artist/album if those columns exist
        sample_row = df[df[track_col] == track_name].iloc[0]

        if artist_col:
            artist = sample_row[artist_col]
        if album_col:
            album = sample_row[album_col]

        track_items.append(
            html.Div(
                className="track-item",
                children=[
                    html.Div(
                        children=[
                            html.Div(str(rank), className="track-rank heading-3"),
                            html.Div(track_name, className="track-title heading-4"),
                        ],
                        className="track-main-info",
                    ),
                    html.Div(artist, className="track-artist body"),
                    html.Div(album, className="track-album body"),
                ],
            )
        )

    return html.Div(track_items, className="track-list")
