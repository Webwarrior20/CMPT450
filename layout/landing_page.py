from dash import html, dcc

def LandingPage():
    return html.Div(
        style={
            "height": "100vh",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "alignItems": "center",
            "backgroundColor": "#1DB954",
            "color": "black",
            "fontFamily": "Arial, sans-serif",
            "textAlign": "center",
        },
        children=[
            html.Div(
                [
                    html.Img(
                        src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
                        style={"width": "60px", "marginBottom": "15px"},
                    ),
                    html.H1("RhythmGraph", style={"fontSize": "38px", "fontWeight": "700", "marginBottom": "40px"}),
                ]
            ),
            html.H2(
                "Turn Your Music Into a Story",
                style={"fontWeight": "700", "fontSize": "28px", "marginBottom": "10px"},
            ),
            html.P(
                "Upload your listening data and discover what your sound says about you.",
                style={"fontSize": "16px", "marginBottom": "50px"},
            ),
            dcc.Upload(
                id="upload-data",
                children=html.Div(
                    [
                        html.Span("⬆️ Upload Listening History", style={"fontWeight": "600"}),
                    ],
                    style={
                        "backgroundColor": "black",
                        "color": "white",
                        "padding": "16px 28px",
                        "borderRadius": "40px",
                        "cursor": "pointer",
                        "fontSize": "16px",
                        "display": "inline-block",
                    },
                ),
                multiple=True,
                accept=".json,.csv",
                style={"border": "none"},
            ),
            html.P(
                "Upload your Spotify listening history (.JSON or .CSV). Your data stays private and never leaves your device.",
                style={"fontSize": "12px", "marginTop": "20px", "opacity": "0.8"},
            ),
            dcc.Location(id="redirect", refresh=True),
        ],
    )
