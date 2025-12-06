import dash
from dash import html, dcc, Input, Output
import plotly.express as px

from layout.analytics_layout import analytics_layout
from components.time_select_period import time_select_period
from utils.features import get_feature_data, compute_audio_profile, AUDIO_FEATURES

dash.register_page(__name__, path="/analytics/features", name="Track Features Analysis - Analytics")

layout = analytics_layout(
    [
        time_select_period(),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H2("Your Audio Profile"),
                        dcc.Store(id="selected-time-period"),
                        dcc.Graph(id="audio-profile-radar"),
                    ],
                    className="feature-top-feature"
                ),
                html.Div(id="feature-breakdown")
            ],
            className="feature-graphs"
        ),
    ],
    "Track Features"
)

@dash.callback(
    Output("audio-profile-radar", "figure"),
    Input("selected-time-period", "data")
)
def update_audio_profile(time_period):
    df = get_feature_data(time_period)
    profile = compute_audio_profile(df)

    if profile is None:
        return px.scatter_polar(title="Not enough audio feature data")

    fig = px.line_polar(
        r=profile.values,
        theta=AUDIO_FEATURES,
        line_close=True
    )

    fig.update_traces(
        fill="toself",
        line_color="#1DB954",
        line_width=3
    )

    fig.update_layout(
        title=None,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            angularaxis=dict(
                tickfont=dict(size=14, color="white"),
                showline=False,
                gridcolor="rgba(255,255,255,0.1)"
            ),
            radialaxis=dict(
                range=[0, 100],
                showticklabels=False,
                ticks="",
                gridcolor="rgba(255,255,255,0.1)",
            ),
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20)
    )

    return fig


@dash.callback(
    Output("feature-breakdown", "children"),
    Input("selected-time-period", "data")
)
def update_feature_breakdown(time_period):
    df = get_feature_data(time_period)
    profile = compute_audio_profile(df)

    if profile is None:
        return [html.Div("No feature data available")]

    rows = []

    for feature, value in profile.items():
        pct = f"{int(value)}%"

        rows.append(
            html.Div(
                [
                    html.Div(
                        children=[
                            html.Div(feature.capitalize(), className="feature-name"),
                            html.Div(pct, className="feature-percent"),
                        ],
                        className="feature-bar-label"
                    ),

                    html.Div(
                        [
                            html.Div(
                                className="feature-bar-fill",
                                style={"width": pct}
                            )
                        ],
                        className="feature-bar"
                    )
                ],
                className="feature-row"
            )
        )

    return rows