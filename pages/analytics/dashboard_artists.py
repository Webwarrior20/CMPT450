import dash
from dash import html
from layout.analytics_layout import analytics_layout

dash.register_page(__name__, path="/analytics/artists", name="Your Top Artists - Analytics")

layout = analytics_layout(
        [

        ],
    "Top Artists"
    )
