from dash import html

def TrackFeaturesPage():
    return html.Div([
        html.H1("Track Features", style={"fontSize": "28px", "marginBottom": "20px"}),
        html.P("Explore danceability, energy, tempo, and valence of your favorite songs."),
    ])
