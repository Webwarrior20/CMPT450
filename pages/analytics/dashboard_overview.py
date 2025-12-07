import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd

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


# Page layout
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
            # Statistics row
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
            ),

            html.Div(
                className="overview-graphs",
                children=[
                    html.Div(
                        className="trends-container",
                        children=[
                            html.H2("Song Feature Trends (6 Months)"),
                            dcc.Graph(id="listening-trend-graph")
                        ]
                    ),

                    html.Div(
                        className="trends-container",
                        children=[
                            html.H2("Top Genres Over Time (6 Months)"),
                            dcc.Graph(id="genre-trend-graph")
                        ]
                    ),

                ]
            )
        ],
        "Overview",
    )


# Callback for the trend chart
@callback(
    Output("listening-trend-graph", "figure"),
    Input("url", "pathname")
)
def update_trend_graph(_):
    lh = get_uploaded_dataframe()
    if lh is None or lh.empty:
        return go.Figure()

    # timestamps
    lh["ts"] = pd.to_datetime(lh["ts"], errors="coerce")
    lh = lh.dropna(subset=["ts"])

    # merge with audio features
    from app.store import get_main_database
    db = get_main_database()

    if db is None or db.empty:
        return go.Figure()

    df = lh.merge(
        db,
        left_on="spotify_track_uri",
        right_on="track_uri",
        how="left"
    )

    # required metrics
    metrics = ["danceability", "energy", "valence"]

    # ensure numeric and ignore missing
    for col in metrics:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # filter last 6 months
    last_date = df["ts"].max()
    six_months_ago = last_date - pd.DateOffset(months=6)
    df = df[df["ts"] >= six_months_ago]

    if df.empty:
        return go.Figure()

    # aggregate monthly
    df["month"] = df["ts"].dt.strftime("%b")
    df["month_num"] = df["ts"].dt.month

    monthly = df.groupby("month")[metrics].mean() * 100
    monthly = monthly.round(1)

    # sort months chronologically
    order = df.groupby("month")["month_num"].first().sort_values().index
    monthly = monthly.loc[order]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly.index,
        y=monthly["danceability"],
        mode="lines+markers",
        name="Danceability",
        line=dict(color="#1DB954", width=3),
        marker=dict(size=8)
    ))

    fig.add_trace(go.Scatter(
        x=monthly.index,
        y=monthly["energy"],
        mode="lines+markers",
        name="Energy",
        line=dict(color="#A020F0", width=3),
        marker=dict(size=8)
    ))

    fig.add_trace(go.Scatter(
        x=monthly.index,
        y=monthly["valence"],
        mode="lines+markers",
        name="Valence",
        line=dict(color="#FF4F7B", width=3),
        marker=dict(size=8)
    ))

    # styling
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            y=-0.25,
            font=dict(color="white", size=14)
        ),
        xaxis=dict(
            tickfont=dict(color="white", size=16),
            showgrid=False
        ),
        yaxis=dict(
            range=[0, 100],
            tickfont=dict(color="white", size=16),
            gridcolor="rgba(255,255,255,0.1)"
        ),
        margin=dict(l=40, r=40, t=10, b=60)
    )

    return fig

@callback(
    Output("genre-trend-graph", "figure"),
    Input("url", "pathname")
)
def update_genre_trend(_):
    lh = get_uploaded_dataframe()
    if lh is None or lh.empty:
        return go.Figure()

    lh["ts"] = pd.to_datetime(lh["ts"], errors="coerce")
    lh = lh.dropna(subset=["ts"])

    from app.store import get_main_database
    db = get_main_database()

    if db is None or db.empty:
        return go.Figure()

    # Merge to bring in genres
    df = lh.merge(
        db,
        left_on="spotify_track_uri",
        right_on="track_uri",
        how="left"
    )

    # Parse genres
    import ast
    def parse_genres(x):
        if isinstance(x, list):
            return x
        if isinstance(x, str):
            try:
                out = ast.literal_eval(x)
                return out if isinstance(out, list) else [x]
            except:
                return [x]
        return []

    df["parsed_genres"] = df["artist_genres"].apply(parse_genres)
    df = df.explode("parsed_genres").dropna(subset=["parsed_genres"])

    # Clean weird values
    df["parsed_genres"] = df["parsed_genres"].apply(lambda x: x.strip() if isinstance(x, str) else x)
    df = df[df["parsed_genres"] != ""]

    # Filter last 6 months
    last_date = df["ts"].max()
    six_months_ago = last_date - pd.DateOffset(months=6)
    df = df[df["ts"] >= six_months_ago]

    if df.empty:
        return go.Figure()

    # Determine top 5 genres total
    top5 = df["parsed_genres"].value_counts().head(5).index.tolist()

    df_top5 = df[df["parsed_genres"].isin(top5)].copy()

    # Month column
    df_top5["month"] = df_top5["ts"].dt.strftime("%b")
    df_top5["month_num"] = df_top5["ts"].dt.month

    # Count per month per genre
    monthly_counts = (
        df_top5.groupby(["month", "parsed_genres"])
        .size()
        .reset_index(name="count")
    )

    # Ensure month order
    month_order = (
        df_top5.groupby("month")["month_num"]
        .first()
        .sort_values()
        .index
        .tolist()
    )

    monthly_counts["month"] = pd.Categorical(monthly_counts["month"], month_order)
    monthly_counts = monthly_counts.sort_values(["month", "parsed_genres"])

    # Make figure
    fig = go.Figure()

    colors = ["#1DB954", "#A020F0", "#FF4F7B", "#00A0FF", "#FFB800"]

    for genre, color in zip(top5, colors):
        sub = monthly_counts[monthly_counts["parsed_genres"] == genre]
        fig.add_trace(go.Scatter(
            x=sub["month"],
            y=sub["count"],
            mode="lines+markers",
            name=genre.capitalize(),
            line=dict(color=color, width=3),
            marker=dict(size=8)
        ))

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            y=-0.25,
            font=dict(color="white", size=14)
        ),
        xaxis=dict(
            tickfont=dict(color="white", size=16),
            showgrid=False
        ),
        yaxis=dict(
            tickfont=dict(color="white", size=16),
            gridcolor="rgba(255,255,255,0.1)"
        ),
        margin=dict(l=40, r=40, t=10, b=60)
    )

    return fig
