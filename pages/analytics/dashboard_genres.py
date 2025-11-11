import dash
from dash import html
from layout.analytics_layout import analytics_layout

dash.register_page(__name__, path="/analytics/genres", name="Your Top Genres - Analytics")

layout = analytics_layout(
        [

        ],
    "Top Genres"
    )
