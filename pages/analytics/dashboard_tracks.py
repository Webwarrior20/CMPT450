import dash
from dash import html
from layout.analytics_layout import analytics_layout


dash.register_page(__name__, path="/analytics/tracks", name="Your Top Tracks - Analytics")

layout = analytics_layout(
        [

        ],
    "Top Tracks"
    )
