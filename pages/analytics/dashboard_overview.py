import dash
from dash import html
from layout.analytics_layout import analytics_layout
from app.store import get_uploaded_data
from utils.stats import compute_overview_stats   # uses real data

dash.register_page(__name__, path="/analytics/overview", name="Overview - Analytics")


def stat_card(title, value, color):
    return html.Div(
        className="stat-card",
        style={"--card-color": color},
        children=[
            html.H2(title, className="caption semi-bold"),
            html.P(value, className="heading-4 card-value"),
        ],
    )


def layout():
    df = get_uploaded_data()

    # If user hasn't uploaded anything yet — show hint
    if df is None or df.empty:
        return analytics_layout(
            [
                html.H2("No data uploaded yet.", className="warning"),
                html.P("Upload a CSV or JSON file from Spotify to see insights.", className="body"),
            ],
            "Overview"
        )

    # Compute real values from uploaded data
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
        "Overview"
    )
