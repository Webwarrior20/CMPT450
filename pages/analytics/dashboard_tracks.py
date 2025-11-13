import dash
from dash import html, dcc, callback, Output, Input
from layout.analytics_layout import analytics_layout
from components.time_select_period import time_select_period

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
