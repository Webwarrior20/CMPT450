from dash import html

def ListeningJourneyPage():
    return html.Div([
        html.H1("Listening Journey", style={"fontSize": "28px", "marginBottom": "20px"}),
        html.P("Visualize your listening habits and evolution over time."),
    ])
