import dash
from dash import html, dcc, callback, Output, Input
from layout.analytics_layout import analytics_layout
from components.time_select_period import time_select_period

dash.register_page(__name__, path="/analytics/artists", name="Your Top Artists - Analytics")

layout = analytics_layout(
        [
            time_select_period(),
            dcc.Store(id="selected-time-period"),
            html.Div(id="artist-listing"),
        ],
    "Top Artists"
    )

@callback(
    Output("artist-listing", "children"),
    Input("selected-time-period", "data"),
)
def on_time_period_change_tracks(time_period):
    if time_period is None:
        time_period = "4 weeks"

    # Placeholder data:
    artist_list = [
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"},
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"},
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"},
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"},
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"},
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"},
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"},
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"},
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"},
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"},
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"},
        {"artist": "Clario", "link": "https://open.spotify.com/artist/3l0CmX0FuQjFxr8SK7Vqag", "artist-photo-link": "https://i.scdn.co/image/ab6772690000dd22677b28d7b8018ee22436ee0b"}
    ]

    return html.Div(
        className="artist-list",
        children=[
            html.Div(
                className="artist-item",
                children=[
                    html.Div(
                        className="artist-art-wrapper",
                        children=html.Img(
                            src=artist["artist-photo-link"],
                            className="artist-art",
                        ),
                    ),
                    html.Div(f"#{str(rank)}", className="artist-rank heading-3"),
                    html.Div(artist["artist"], className="artist-name heading-2"),
                    html.Div(
                        className="link-artist",
                        children=html.A(
                            html.Img(
                                src="/assets/images/icon-spotify-white.png",
                                className="spotify-track-link-icon-artist",
                            ),
                            href=artist["link"],
                            target="_blank",
                        ),
                    ),
                ],
            )
            for rank, artist in enumerate(artist_list, start=1)
        ],
    )
