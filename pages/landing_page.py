import dash
from dash import html, dcc

dash.register_page(__name__, path="/", name="Welcome to RhythmGraph")

layout = html.Div(
    className="landing-page",
    children=[
        # ---------------------- HEADER ----------------------
        html.Section(
            className="landing-header",
            children=[
                html.Img(
                    src="/assets/images/icon-spotify-black.png",
                    className="landing-logo",
                ),
                html.H1("RhythmGraph", className="display"),
            ],
        ),

        # ---------------------- BODY TEXT ----------------------
        html.Div(
            className="landing-body",
            children=[
                html.H2("Turn Your Music Into a Story", className="heading-1"),
                html.P(
                    "Upload your listening data and discover what your sound says about you.",
                    className="body",
                ),
            ],
        ),

        # ---------------------- UPLOAD SECTION ----------------------
        html.Div(
            className="landing-upload-section",
            children=[
                dcc.Upload(
                    id="upload-data",
                    className="landing-upload-area body bold",
                    children=html.Div(
                        [
                            html.Img(src="/assets/images/icon-upload.svg"),
                            html.Span(
                                "Upload Listening History",
                                className="landing-upload-text",
                            ),
                        ],
                        className="landing-upload-button",
                    ),
                    multiple=True,
                    accept=".json,.csv",
                ),

                # NEW: Upload Progress Output Container
                html.Div(
                    id="upload-progress",
                    className="upload-progress-wrapper"
                ),

                html.P(
                    [
                        "Upload your Spotify listening history (.JSON or .CSV).",
                        html.Br(),
                        "Your data stays private and never leaves your device.",
                    ],
                    className="subtitle",
                ),

                # Hidden location for redirect after upload
                dcc.Location(id="redirect", refresh=True),
            ],
        ),
    ],
)
