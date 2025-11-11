from dash import html, dcc

NAV = {
    "listening-journey": {
        "label": "Listening Journey",
        "href": "/listening-journey",
        "sections": [
            ("introduction", "Introduction", "/listening-journey#introduction"),
        ],
    },
    "analytics": {
        "label": "Analytics",
        "href": "/analytics/overview",
        "sections": [
            ("overview", "Overview", "/analytics/overview"),
            ("tracks", "Top Tracks", "/analytics/tracks"),
            ("artists", "Top Artists", "/analytics/artists"),
            ("genres", "Genres", "/analytics/genres"),
            ("features", "Track Features", "/analytics/features"),
        ],
    },
}

def sidebar(active_page="listening-journey", active_section="overview"):
    top_links = [
        dcc.Link(
            NAV[key]["label"],
            href=NAV[key]["href"],
            className=f"sidebar-link{' active' if key == active_page else ''} bold",
        )
        for key in NAV.keys()
    ]

    sublinks = []
    if active_page in NAV:
        sublinks = [
            dcc.Link(
                label,
                href=href,
                className=f"sidebar-link{' active' if section_key == active_section else ''} bold",
            )
            for section_key, label, href in NAV[active_page]["sections"]
        ]

    return html.Div(
        className="sidebar",
        children=[
            html.Div(
                [
                    html.Img(src="/assets/images/icon-spotify-green.png", className="sidebar-logo"),
                    html.H2("RhythmGraph", className="heading-4 sidebar-title"),
                ],
                className="sidebar-header",
            ),
            html.Div(top_links, className="sidebar-links"),
            html.Div(sublinks, className="sidebar-sub-links"),
        ],
    )
