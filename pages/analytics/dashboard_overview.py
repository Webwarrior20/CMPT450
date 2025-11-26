import dash
from dash import html
from layout.analytics_layout import analytics_layout
from utils.stats import compute_overview_stats, get_uploaded_dataframe

dash.register_page(__name__, path="/analytics/overview", name="Overview - Analytics")


def stat_card(title, value, color):
    return html.Div(
        className="stat-card",
        style={"--card-color": color},
        children=[
            html.H2(title, className="caption semi-bold"),
            html.P(str(value), className="heading-4 card-value"),
        ],
    )


def layout():
    df = get_uploaded_dataframe()

    if df is None or df.empty:
        return analytics_layout(
            [
                html.H2("No data loaded yet.", className="warning"),
                html.P(
                    "Upload a Spotify CSV/JSON file on the landing page to see your analytics.",
                    className="body",
                ),
            ],
            "Overview",
        )

    stats = compute_overview_stats(df)

    return analytics_layout(
        [
            html.Div(
                className="overview-stats",
                children=[
                    stat_card("Top Genre", stats["top_genre"], "#283C92"),
                    stat_card("Top Artist", stats["top_artist"], "#016250"),
                    stat_card("Listening Streak", f"{stats['streak']} days", "#BF182E"),
                    stat_card("New Discoveries", stats["discoveries"], "#4E3750"),
                    stat_card("Average Song Length", stats["avg_length"], "#1E3162"),
                    stat_card("Listening Time", f"{stats['listening_time_hours']} Hours", "#0D70E4"),
                ],
            )
        ],
        "Overview",
    )
