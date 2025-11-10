from dash import html, dcc

def Sidebar(active="/dashboard/overview"):
    nav_items = [
        ("Listening Journey", "/dashboard/journey"),
        ("Analytics", "/dashboard/analytics"),
        ("Overview", "/dashboard/overview"),
        ("Top Tracks", "/dashboard/tracks"),
        ("Top Artists", "/dashboard/artists"),
        ("Genres", "/dashboard/genres"),
        ("Track Features", "/dashboard/features"),
    ]

    return html.Div(
        style={
            "width": "250px",
            "backgroundColor": "#181818",
            "padding": "30px 20px",
            "display": "flex",
            "flexDirection": "column",
            "borderRight": "1px solid #333",
        },
        children=[
            html.Div(
                [
                    html.Img(
                        src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
                        style={"width": "35px", "height": "35px", "marginRight": "10px"},
                    ),
                    html.H2("RhythmGraph", style={"color": "#1DB954", "fontSize": "20px", "margin": 0}),
                ],
                style={"display": "flex", "alignItems": "center", "marginBottom": "30px"},
            ),
            html.Div(
                [nav_link(text, href, active=(href == active)) for text, href in nav_items]
            ),
        ],
    )

def nav_link(label, href, active=False):
    color = "#1DB954" if active else "#CCC"
    bg = "#202020" if active else "transparent"
    return dcc.Link(
        html.Div(
            label,
            style={
                "color": color,
                "padding": "10px 15px",
                "borderRadius": "8px",
                "cursor": "pointer",
                "fontWeight": "500",
                "transition": "all 0.3s",
                "backgroundColor": bg,
            },
        ),
        href=href,
        style={"textDecoration": "none"},
    )
