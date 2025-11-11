from dash import html, dcc, callback, Input, Output
from components.sidebar import sidebar


def analytics_layout(children, title):
    return html.Div(
        className="analytics",
        children=[
            dcc.Location(id="url", refresh=False),
            html.Div(id="sidebar-container"),
            html.Main(className="analytics-content", children=[
                html.Div(
                    children=[
                        html.H1(title,className="analytics-header heading-2")
                    ]
                ),
                *children
            ]),
        ],
    )

@callback(
    Output("sidebar-container", "children"),
    Input("url", "pathname")
)
def update_sidebar(pathname):
    if not pathname:
        return sidebar("analytics", "overview")

    section = pathname.strip("/").split("/")[-1]
    return sidebar("analytics", section)