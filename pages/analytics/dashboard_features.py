import dash
from dash import html
from layout.analytics_layout import analytics_layout

dash.register_page(__name__, path="/analytics/features", name="Track Features Analysis - Analytics")

layout = analytics_layout(
        [

        ],
    "Track Features"
    )
