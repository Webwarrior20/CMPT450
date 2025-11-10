from dash import html

def TopTracksPage():
    return html.Div([
        html.H1("Top Tracks", style={"fontSize": "28px", "marginBottom": "20px"}),
        html.P("This section will show your most played tracks, listening duration, and patterns."),
    ])
