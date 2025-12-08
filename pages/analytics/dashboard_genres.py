import dash
from dash import html, dcc, Input, Output
import plotly.express as px
from layout.analytics_layout import analytics_layout
from utils.genre import get_genre_data, get_genre_counts, get_top5_breakdown, get_genre_stats
from components.time_select_period import time_select_period

dash.register_page(__name__, path="/analytics/genres", name="Your Top Genres - Analytics")

layout = analytics_layout(
    [
        time_select_period(),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H2("Genre Distribution"),
                        dcc.Store(id="selected-time-period"),
                        dcc.Graph(id="top-genres-graph"),
                    ],
                    className="genre-top-genre"
                ),
                html.Div(id="genre-breakdown"),
            ],
            className="genre-graphs"
        ),
        html.Div(id="genre-stats-row", className="genre-stats-row"),
    ],
    "Top Genres"
)


@dash.callback(
    Output("top-genres-graph", "figure"),
    Input("selected-time-period", "data")
)
def update_genre_chart(time_period):
    exploded = get_genre_data(time_period)
    genre_counts = get_genre_counts(exploded)

    if genre_counts.empty:
        return px.bar(title="No genre data found")

    df = genre_counts.head(5)

    fig = px.bar(
        df,
        x="genre",
        y="genre_count",
        color_discrete_sequence=["#1ED760"],
    )

    fig.update_layout(
        title=None,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=60),
        xaxis=dict(
            title=None,
            tickfont=dict(size=16, color="white"),
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=16, color="white"),
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.1)"
        )
    )

    fig.update_traces(marker_line_width=0)

    return fig


@dash.callback(
    Output("genre-breakdown", "children"),
    Input("selected-time-period", "data")
)
def update_genre_breakdown(time_period):
    exploded = get_genre_data(time_period)
    genre_counts = get_genre_counts(exploded)

    if genre_counts.empty:
        return [html.Div("No genre data available")]

    breakdown = get_top5_breakdown(genre_counts)

    rows = []

    for row in breakdown:
        pct_num = row["pct"]
        pct = f"{pct_num}%"

        rows.append(
            html.Div(
                [
                    html.Div(
                        children=[
                            html.Div(row["genre"].capitalize(), className="genre-name"),
                            html.Div(pct, className="genre-percent"),
                        ],
                        className="genre-bar-label"
                    ),
                    html.Div(
                        [
                            html.Div(
                                className="genre-bar-fill",
                                style={"width": pct}
                            )
                        ],
                        className="genre-bar"
                    )
                ],
                className="genre-row"
            )
        )

    return rows


@dash.callback(
    Output("genre-stats-row", "children"),
    Input("selected-time-period", "data")
)
def update_genre_stats_row(time_period):
    exploded = get_genre_data(time_period)
    genre_counts = get_genre_counts(exploded)

    most_played, pct, diversity, avg = get_genre_stats(genre_counts)

    if most_played is None:
        return [html.Div("No statistics available")]

    return [
        html.Div(
            [
                html.Div("Most Played", className="stats-title"),
                html.Div(most_played, className="stats-value"),
                html.Div(f"{pct}% of your music", className="stats-sub")
            ],
            className="stats-card"
        ),
        html.Div(
            [
                html.Div("Genre Diversity", className="stats-title"),
                html.Div(diversity, className="stats-value"),
                html.Div("Different genres", className="stats-sub")
            ],
            className="stats-card"
        ),
        html.Div(
            [
                html.Div("Avg. per Genre", className="stats-title"),
                html.Div(avg, className="stats-value"),
                html.Div("Tracks per genre", className="stats-sub")
            ],
            className="stats-card"
        )
    ]
