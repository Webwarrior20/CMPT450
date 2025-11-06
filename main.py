import os
import io
import json
import base64
import uuid
from urllib.parse import urlparse, parse_qs

import dash
from dash import html, dcc, dash_table, Input, Output, State
import pandas as pd

from flask import request, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# -----------------------------
# Config
# -----------------------------
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "727613cea28546bd8165ffdf1e2bff2e")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "02e1a105f45e4a75b274f0a24e18e458")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8050/callback")
SPOTIFY_SCOPE = "user-read-recently-played"

# global server-side cache for passing data from Flask routes to Dash callbacks
DATA_CACHE = {}

# -----------------------------
# Dash app
# -----------------------------
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# ---- Shared styles (Spotify landing) ----
HERO_STYLE = {
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": "#1DB954",
    "height": "100vh",
    "display": "flex",
    "justifyContent": "center",
    "alignItems": "center",
    "textAlign": "center",
    "color": "black",
}

# -----------------------------
# Pages
# -----------------------------
def landing_page():
    return html.Div(
        style=HERO_STYLE,
        children=[
            dcc.Store(id="session-data", storage_type="session"),  # holds parsed tracks + source
            html.Div(
                style={"maxWidth": "760px"},
                children=[
                    # Logo + Title
                    html.Div(
                        style={"display": "flex", "justifyContent": "center", "alignItems": "center", "gap": "12px"},
                        children=[
                            html.Img(
                                src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
                                style={"width": "55px", "height": "55px"},
                            ),
                            html.H1("RhythmGraph", style={"fontSize": "42px", "fontWeight": "700", "margin": "0"}),
                        ],
                    ),
                    html.H2("Turn Your Music Into a Story", style={"marginTop": "40px", "fontSize": "30px", "fontWeight": "700"}),
                    html.P(
                        "Upload your listening data and discover what your sound says about you.",
                        style={"fontSize": "16px", "marginTop": "10px"},
                    ),

                    # Upload + Spotify buttons
                    html.Div(
                        style={"marginTop": "50px", "display": "flex", "gap": "16px", "justifyContent": "center", "flexWrap": "wrap"},
                        children=[
                            # Upload
                            dcc.Upload(
                                id="upload",
                                children=html.Div(
                                    [
                                        html.Span("⬆️", style={"marginRight": "8px"}),
                                        "Upload Listening History",
                                    ],
                                    style={
                                        "backgroundColor": "black",
                                        "color": "white",
                                        "padding": "14px 28px",
                                        "borderRadius": "30px",
                                        "cursor": "pointer",
                                        "display": "inline-block",
                                        "fontSize": "16px",
                                    },
                                ),
                                multiple=False,
                                accept=".json,.csv",
                                style={"border": "none"},
                            ),
                            # Spotify login
                            html.A(
                                id="spotify-login",
                                children=html.Div(
                                    ["🎧", html.Span("  Connect with Spotify")],
                                    style={
                                        "backgroundColor": "#191414",
                                        "color": "white",
                                        "padding": "14px 28px",
                                        "borderRadius": "30px",
                                        "cursor": "pointer",
                                        "display": "inline-block",
                                        "fontSize": "16px",
                                    },
                                ),
                                href="/login",
                                style={"textDecoration": "none"},
                            ),
                        ],
                    ),
                    html.P(
                        "Upload your Spotify listening history (.JSON or .CSV). Your data stays private and will never leave your device.",
                        style={"fontSize": "12px", "marginTop": "15px", "opacity": "0.8"},
                    ),
                ],
            ),
        ],
    )


def dashboard_page():
    return html.Div(
        style={"fontFamily": "Arial, sans-serif", "padding": "24px"},
        children=[
            dcc.Location(id="dash-url", refresh=False),
            dcc.Store(id="session-data", storage_type="session"),
            html.H1("Dashboard", style={"marginBottom": "10px"}),
            html.Div(id="summary"),
            html.Div(id="table-wrap", style={"marginTop": "18px"}),
            html.Br(),
            html.A("⬅️ Back to Home", href="/", style={"textDecoration": "none", "color": "#1DB954", "fontWeight": "bold"}),
        ],
    )


# -----------------------------
# App Layout (Router)
# -----------------------------
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),  # Enables routing
    html.Div(id="page-content")
])


# -----------------------------
# Page Routing Callback
# -----------------------------
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(_pathname):
    pathname = _pathname or "/"
    if pathname == "/dashboard":
        return dashboard_page()
    return landing_page()


# -----------------------------
# Upload parsing (A + B)
# -----------------------------
def parse_uploaded_file(contents: str, filename: str) -> pd.DataFrame:
    content_type, content_string = contents.split(",", 1)
    decoded = base64.b64decode(content_string)

    # Try JSON first
    if filename.lower().endswith(".json"):
        try:
            data = json.loads(decoded.decode("utf-8"))
        except json.JSONDecodeError:
            data = [json.loads(line) for line in decoded.decode("utf-8").splitlines() if line.strip()]

        rows = []
        for item in data:
            name = item.get("trackName") or item.get("track") or item.get("master_metadata_track_name")
            artist = item.get("artistName") or item.get("artist") or item.get("master_metadata_album_artist_name")
            played_at = item.get("endTime") or item.get("ts") or item.get("played_at")
            ms_played = item.get("msPlayed") or item.get("ms_played") or item.get("duration_ms") or None
            rows.append({"track": name, "artist": artist, "played_at": played_at, "duration_ms": ms_played})
        df = pd.DataFrame(rows)

    else:
        df = pd.read_csv(io.BytesIO(decoded))
        df = df.rename(
            columns={
                "trackName": "track",
                "Track Name": "track",
                "track_name": "track",
                "artistName": "artist",
                "Artist Name": "artist",
                "artist_name": "artist",
                "endTime": "played_at",
                "ts": "played_at",
                "played_at": "played_at",
                "msPlayed": "duration_ms",
                "ms_played": "duration_ms",
                "duration_ms": "duration_ms",
            }
        )
        keep = [c for c in ["track", "artist", "played_at", "duration_ms"] if c in df.columns]
        df = df[keep]

    # Clean up
    if "played_at" in df.columns:
        df["played_at"] = pd.to_datetime(df["played_at"], errors="coerce")
    if "duration_ms" in df.columns:
        df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    return df


@app.callback(
    Output("session-data", "data"),
    Output("url", "href"),
    Input("upload", "contents"),
    State("upload", "filename"),
    State("session-data", "data"),
    prevent_initial_call=True,
)
def on_upload(contents, filename, cur_data):
    if contents and filename:
        df = parse_uploaded_file(contents, filename)
        tracks = df.to_dict("records")
        return {"source": "upload", "tracks": tracks}, "/dashboard"
    raise dash.exceptions.PreventUpdate


# -----------------------------
# Spotify OAuth (D)
# -----------------------------
def make_oauth(state=None):
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_path=None,
        show_dialog=True,
        state=state,
    )


@server.route("/login")
def login_route():
    key = str(uuid.uuid4())
    oauth = make_oauth(state=key)
    auth_url = oauth.get_authorize_url()
    return redirect(auth_url)


@server.route("/callback")
def callback_route():
    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return redirect("/")

    oauth = make_oauth(state=state)
    token_info = oauth.get_access_token(code)
    access_token = token_info["access_token"]

    sp = spotipy.Spotify(auth=access_token)
    recent = sp.current_user_recently_played(limit=50)

    rows = []
    for item in recent.get("items", []):
        track = item["track"]
        rows.append(
            {
                "track": track.get("name"),
                "artist": ", ".join([a["name"] for a in track.get("artists", [])]),
                "played_at": item.get("played_at"),
                "duration_ms": track.get("duration_ms"),
            }
        )

    DATA_CACHE[state] = {"source": "spotify", "tracks": rows}

    return redirect(f"/dashboard?source=spotify&key={state}")


# -----------------------------
# Dashboard Rendering
# -----------------------------
@app.callback(
    Output("summary", "children"),
    Output("table-wrap", "children"),
    Input("dash-url", "href"),
    State("session-data", "data"),
    prevent_initial_call=False,
)
def render_dashboard(href, store_data):
    data = store_data or {}

    if href:
        q = parse_qs(urlparse(href).query or "")
        if (not data) and q.get("source") == ["spotify"] and "key" in q:
            key = q["key"][0]
            cached = DATA_CACHE.pop(key, None)
            if cached:
                data = cached

    if not data or "tracks" not in data or len(data["tracks"]) == 0:
        return html.P("No data loaded yet."), html.Div()

    df = pd.DataFrame(data["tracks"])
    total_tracks = len(df)
    unique_tracks = df["track"].nunique() if "track" in df else total_tracks
    unique_artists = df["artist"].nunique() if "artist" in df else 0

    summary = html.Div([
        html.P(f"Source: {data.get('source', 'unknown')}", style={"opacity": 0.7}),
        html.H3(f"{total_tracks} plays · {unique_tracks} unique tracks · {unique_artists} artists"),
    ])

    shown = df.head(200)
    table = dash_table.DataTable(
        data=shown.to_dict("records"),
        columns=[{"name": c, "id": c} for c in shown.columns],
        page_size=10,
        style_table={"overflowX": "auto", "border": "1px solid #eee"},
        style_cell={"textAlign": "left", "padding": "8px"},
        style_header={"textTransform": "uppercase", "fontWeight": "bold"},
    )

    return summary, table


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("\n⚠️  Warning: Spotify login will not work until you set your Spotify environment variables.\n")
    app.run(debug=True)
