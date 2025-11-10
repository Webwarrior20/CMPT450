from dash import html
from components.cards import build_card

def OverviewPage(stats):
    return html.Div(
        [
            html.H1("Overview", style={"fontSize": "28px", "fontWeight": "700", "marginBottom": "25px"}),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                    "gap": "20px",
                },
                children=[
                    build_card("Top Genre", stats["top_genre"], "#2951A3"),
                    build_card("Top Artist", stats["top_artist"], "#006D5B"),
                    build_card("Listening Streak", f"{stats['listening_streak']} days", "#C62828"),
                    build_card("New Discoveries", str(stats["new_discoveries"]), "#5E35B1"),
                    build_card("Average Song Length", stats["avg_song_length"], "#283593"),
                    build_card("Listening Time", f"{stats['listening_hours']} Hours", "#0277BD"),
                ],
            ),
        ]
    )
