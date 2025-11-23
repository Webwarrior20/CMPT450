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
