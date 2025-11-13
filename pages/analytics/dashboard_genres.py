import dash
from dash import html, dcc
from layout.analytics_layout import analytics_layout
from components.time_select_period import time_select_period

dash.register_page(__name__, path="/analytics/genres", name="Your Top Genres - Analytics")

layout = analytics_layout(
    [
        time_select_period(),
        dcc.Store(id="selected-time-period"),
    ],
    "Top Genres"
)
