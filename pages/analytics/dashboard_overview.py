import dash
from dash import html
from layout.analytics_layout import analytics_layout
from utils.stats import get_mock_stats

dash.register_page(__name__, path="/analytics/overview", name="Overview - Analytics")
stats = get_mock_stats()

def stat_card(title, value, color):
    return html.Div(
        className="stat-card",
        style={"--card-color": color},
        children=[
            html.H2(title, className="caption semi-bold"),
            html.P(value, className="heading-4 card-value"),
        ],
    )

layout = analytics_layout(
        [
            html.Div(
                children=[
                    stat_card("Top Genre", stats["top_genre"], "#283C92"),
                    stat_card("Top Artist", stats["top_artist"], "#016250"),
                    stat_card("Listening Streak", f"{stats['listening_streak']} days", "#BF182E"),
                    stat_card("New Discoveries", str(stats["new_discoveries"]), "#4E3750"),
                    stat_card("Average Song Length", stats["avg_song_length"], "#1E3162"),
                    stat_card("Listening Time", f"{stats['listening_hours']} Hours", "#0D70E4"),
                ],
                className="overview-stats",
            ),
        ],
    "Overview"
    )
