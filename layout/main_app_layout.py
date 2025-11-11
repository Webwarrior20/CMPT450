from dash import html, dcc
import dash


def app_layout():
    return html.Main(
        className="app-container",
        children=[
            dcc.Location(id="url", refresh=False),
            dash.page_container,
        ]
    )
