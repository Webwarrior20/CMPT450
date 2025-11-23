import dash
from dash import html, dcc, callback, Output, Input
from layout.analytics_layout import analytics_layout
from components.time_select_period import time_select_period
from app.store import get_uploaded_data
import pandas as pd

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
def render_top_artists(time_period):

    df = get_uploaded_data()

    # No Data → Show message
    if df is None or df.empty:
        return html.Div(
            "No data uploaded yet — upload CSV/JSON on the homepage.",
            className="warning"
        )

    # 🔥 Filter by time period (default 4 weeks)
    if "ts" in df.columns:
        df = df.dropna(subset=["ts"])
        df = df.sort_values("ts")

        last_date = df["ts"].max()

        if time_period == "4 weeks":
            df = df[df["ts"] >= last_date - pd.Timedelta(weeks=4)]
        elif time_period == "6 months":
            df = df[df["ts"] >= last_date - pd.Timedelta(days=180)]
        elif time_period == "lifetime":
            pass  # use all data

    # 🔥 Aggregate listening time per artist
    if "artist" not in df.columns:
        return html.Div("No 'artist' column found in uploaded data.", className="error")

    artist_totals = (
        df.groupby("artist")["minutes"].sum().sort_values(ascending=False).head(15)
    )

    # Convert to displayable structure
    artists = [
        {
            "rank": i + 1,
            "artist": name,
            "minutes": round(minutes, 1),
            "link": f"https://open.spotify.com/search/{name.replace(' ', '%20')}",
            "img": "/assets/images/icon-spotify-green.png",   # placeholder
        }
        for i, (name, minutes) in enumerate(artist_totals.items())
    ]

    # Build UI Components
    return html.Div(
        className="artist-list",
        children=[
            html.Div(
                className="artist-item",
                children=[
                    html.Div(
                        className="artist-art-wrapper",
                        children=html.Img(
                            src=artist["img"],
                            className="artist-art",
                        ),
                    ),
                    html.Div(f"#{artist['rank']}", className="artist-rank heading-3"),
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
            for artist in artists
        ],
    )
