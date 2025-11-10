from dash import html

def AnalyticsPage():
    return html.Div([
        html.H1("Analytics", style={"fontSize": "28px", "marginBottom": "20px"}),
        html.P("Dive into advanced statistics and correlations of your listening behavior."),
    ])
