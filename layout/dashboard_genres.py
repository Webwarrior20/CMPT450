from dash import html

def GenresPage():
    return html.Div([
        html.H1("Genres", style={"fontSize": "28px", "marginBottom": "20px"}),
        html.P("This section will show your most listened genres and mood clusters."),
    ])
