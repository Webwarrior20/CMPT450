from dash import Dash, html, dcc, Input, Output, State
from layout.landing_page import LandingPage
from layout.sidebar import Sidebar
from layout.dashboard_overview import OverviewPage
from layout.dashboard_tracks import TopTracksPage
from layout.dashboard_artists import TopArtistsPage
from layout.dashboard_genres import GenresPage
from layout.dashboard_features import TrackFeaturesPage
from layout.dashboard_journey import ListeningJourneyPage
from layout.dashboard_analytics import AnalyticsPage
from utils.parser import parse_uploaded_files
from utils.stats import get_mock_stats

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server
UPLOADED_DATA = None

# Global fade-in style
FADE_STYLE = {
    "animation": "fadeIn 0.5s ease-in-out",
    "opacity": "1",
}

# Inject CSS keyframes for animation
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>RhythmGraph</title>
        {%favicon%}
        {%css%}
        <style>
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(10px);}
            to {opacity: 1; transform: translateY(0);}
        }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")
])

# -----------------------------
# Page Routing
# -----------------------------
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def route_page(pathname):
    global UPLOADED_DATA
    stats = get_mock_stats()

    # Landing
    if pathname in ["/", None]:
        return LandingPage()

    # Dashboard wrapper pages
    if pathname.startswith("/dashboard") and UPLOADED_DATA is not None:
        return html.Div(
            style={"display": "flex", "backgroundColor": "#121212", "minHeight": "100vh"},
            children=[
                Sidebar(active=pathname),
                html.Div(
                    style={"flex": 1, "padding": "30px", "color": "white", **FADE_STYLE},
                    children=render_dashboard_page(pathname, stats),
                ),
            ],
        )

    return LandingPage()

# -----------------------------
# Upload Redirect
# -----------------------------
@app.callback(
    Output("redirect", "pathname"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def handle_upload(contents, filenames):
    global UPLOADED_DATA
    if contents and filenames:
        files = [{"name": n, "content": c} for n, c in zip(filenames, contents)]
        UPLOADED_DATA = parse_uploaded_files(files)
        return "/dashboard/overview"
    raise Exception("No file uploaded.")

# -----------------------------
# Helper — Dashboard Router
# -----------------------------
def render_dashboard_page(pathname, stats):
    if pathname.endswith("overview"):
        return OverviewPage(stats)
    elif pathname.endswith("tracks"):
        return TopTracksPage()
    elif pathname.endswith("artists"):
        return TopArtistsPage()
    elif pathname.endswith("genres"):
        return GenresPage()
    elif pathname.endswith("features"):
        return TrackFeaturesPage()
    elif pathname.endswith("journey"):
        return ListeningJourneyPage()
    elif pathname.endswith("analytics"):
        return AnalyticsPage()
    else:
        return OverviewPage(stats)

if __name__ == "__main__":
    app.run(debug=True)
