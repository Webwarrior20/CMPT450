from dash import html
from components.sidebar import sidebar

def listening_journey_layout(children):
    return html.Div(
        className="listening-journey",
        children=[
            sidebar("listening-journey"),
            html.Main(className="listening-journey-content", children=children),
        ],
    )