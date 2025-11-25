import dash
from dash import html, dcc, callback, Output, Input
from layout.analytics_layout import analytics_layout
from components.time_select_period import time_select_period
from app.store import get_uploaded_data
import pandas as pd

dash.register_page(__name__, path="/analytics/artists", name="Your Top Artists - Analytics")

# ------------------------------------------------------
# Page Layout
# ------------------------------------------------------
layout = analytics_layout(
    [
        time_select_period(),
        dcc.Store(id="selected-time-period"),
        html.Div(id="artist-listing"),
    ],
    "Top Artists",
)

# ------------------------------------------------------
# CALLBACK (only one!)
# ------------------------------------------------------
@callback(
    Output("artist-listing", "children"),
    Input("selected-time-period", "data"),
)
def render_top_artists(time_period):

    df = get_uploaded_data()

    # No data
    if df is None or df.empty:
        return html.Div(
            "No data uploaded yet — upload CSV/JSON first.",
            className="warning"
        )

    # Ensure timestamp is datetime
    if "ts" in df.columns:
        df = df.dropna(subset=["ts"]).copy()
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("ts")

        last = df["ts"].max()

        # Time filtering
        if time_period == "4 weeks":
            df = df[df["ts"] >= last - pd.Timedelta(weeks=4)]
        elif time_period == "6 months":
            df = df[df["ts"] >= last - pd.Timedelta(days=180)]
        # lifetime = no filter

    # Must have "artist" + "minutes"
    if "artist" not in df.columns:
        return html.Div("No 'artist' column found in uploaded data.", className="error")

    if "minutes" not in df.columns:
        df["minutes"] = df.get("ms_played", 0) / 60000  # fallback

    # Aggregate top 15 artists
    artist_totals = (
        df.groupby("artist")["minutes"]
        .sum()
        .sort_values(ascending=False)
        .head(15)
    )

    artists = [
        {
            "rank": i + 1,
            "artist": name,
            "minutes": round(minutes, 1),
            "link": f"https://open.spotify.com/search/{name.replace(' ', '%20')}",
        }
        for i, (name, minutes) in enumerate(artist_totals.items())
    ]

    # ------------------------------------------------------
    # Build UI
    # ------------------------------------------------------
    return html.Div(
        className="artist-list",
        children=[
            html.Div(
                className="artist-item",
                children=[
                    html.Div(f"#{artist['rank']}", className="artist-rank heading-3"),

                    html.Div(
                        className="artist-main",
                        children=[
                            html.Div(artist["artist"], className="artist-name heading-2"),
                            html.Div(
                                f"{artist['minutes']} min",
                                className="artist-minutes body",
                            ),
                        ],
                    ),

                    html.A(
                        html.Img(
                            src="/assets/images/icon-spotify-white.png",
                            className="artist-link-icon",
                        ),
                        href=artist["link"],
                        target="_blank",
                        className="artist-link",
                    ),
                ],
            )
            for artist in artists
        ],
    )
