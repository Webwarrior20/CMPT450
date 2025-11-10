from dash import html

def TopArtistsPage():
    return html.Div([
        html.H1("Top Artists", style={"fontSize": "28px", "marginBottom": "20px"}),
        html.P("This section will show your top artists and their trends over time."),
    ])
