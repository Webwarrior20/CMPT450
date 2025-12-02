from dash import html, dcc
from utils.stats import get_first_listen_date, get_total_listening_time, get_uploaded_dataframe
import pandas as pd
import plotly.express as px

"""
Build the introduction section. Accepts a pandas dataframe as input.
"""
def introduction_section(df=None):
    if df is None:
        df = get_uploaded_dataframe()

    if df is None or df.empty:
        return html.Div(
            className="section",
            children=[
                html.H2("Introduction - Error", className="heading-1"),
                html.Div(
                    children=[
                        html.P(
                            """
                            Dataframe being passed into the function is empty
                            """,
                            className="body"
                        )
                    ]
                )
            ]
        )

    first_listen_date = get_first_listen_date(df)
    total_time = get_total_listening_time(df)
    total_time_graph = total_listening_time_line_graph(df)
    return html.Div(
        className="section",
        children=[
            html.H2("Introduction", className="heading-1"),
            html.Div(
                children=[
                    html.P(
                        """
                        Welcome to your Listening Journey! This section provides an in-depth analysis of your music 
                        listening habits based on the data you've uploaded from Spotify. Explore various aspects of your 
                        listening patterns, including genre preferences, artist trends, song popularity, and energy profiles. 
                        Dive in to discover insights about your musical tastes and how they have evolved over time.
                        """,
                        className="body"
                    )
                ]
            ),

            # First listen date
            html.Div(
                children=[
                    html.H3(
                        ["You first hit play on ", html.Span(first_listen_date, className="emphasis")],
                        className="body",
                    )
                ]
            ),

            # Total listening time
            html.Div(
                children=[
                    html.H3(
                        ["Your total listening time on Spotify is ", html.Span(total_time, className="emphasis")],
                        className="body",
                    )
                ]
            ),

            # Graph under the total listening time
            html.Div(
                children=[
                    dcc.Graph(figure=total_time_graph, config={"displayModeBar": False})
                ],
                className="graph-section"
            )
        ]
    )

# ---------------- Total Personal Listening Time on Spotify Since Beginning to Present ----------------
"""
Build a monthly hours-played line chart from the provided DataFrame.
Falls back to computing 'hours_played' from common ms columns if missing.
Returns a Plotly Figure (empty Figure if data is insufficient).
"""
def total_listening_time_line_graph(df):

    # sensible defaults for Spotify colors
    spotify_green = "#1DB954"
    spotify_dark = "#191414"

    if df is None or df.empty:
        return px.line()  # empty figure

    df = df.copy()

    # ensure timestamp column exists and is datetime
    if "ts" not in df.columns:
        # try common alternatives
        for alt in ("played_at", "timestamp", "date"):
            if alt in df.columns:
                df = df.rename(columns={alt: "ts"})
                break
    try:
        df["ts"] = pd.to_datetime(df["ts"])
    except Exception:
        return px.line()

    # ensure hours_played column exists; try to compute from milliseconds if needed
    if "hours_played" not in df.columns:
        if "ms_played" in df.columns:
            df["hours_played"] = df["ms_played"] / (1000 * 60 * 60)
        elif "duration_ms" in df.columns:
            df["hours_played"] = df["duration_ms"] / (1000 * 60 * 60)
        else:
            return px.line()

    # build monthly aggregation
    df["month"] = df["ts"].dt.to_period("M").astype(str)
    monthly_play = (
        df.groupby("month", observed=False)
        .agg(hours=("hours_played", "sum"))
        .reset_index()
    )

    if monthly_play.empty:
        return px.line()

    monthly_play["month_dt"] = pd.to_datetime(monthly_play["month"])
    # protective indexing for max row
    try:
        max_idx = monthly_play["hours"].idxmax()
        max_row = monthly_play.loc[max_idx]
    except Exception:
        max_row = None

    avg_hours = monthly_play["hours"].mean()

    # Create line chart
    fig = px.line(
        monthly_play,
        x="month_dt",
        y="hours",
        markers=True,
        labels={"hours": "Hours Played", "month_dt": "Month"},
        title="Total Personal Listening Time on Spotify Since 2020 to Present",
        line_shape="linear",
    )

    # Style line and markers
    fig.update_traces(line_color=spotify_green, marker=dict(size=8, color=spotify_green))

    # Highlight the highest point if available
    if max_row is not None:
        fig.add_scatter(
            x=[max_row["month_dt"]],
            y=[max_row["hours"]],
            mode="markers+text",
            marker=dict(color="#006400", size=14, symbol="circle"),
            text=[f"{max_row['hours']:.1f} Hours"],
            textposition="top center",
            textfont=dict(size=16, family="Open Sans", color="#006400"),
            showlegend=False,
        )

    # Add average line
    fig.add_hline(
        y=avg_hours,
        line_dash="dash",
        line_color="grey",
        opacity=0.6,
        annotation_text="Average Listening Time",
        annotation_position="top right",
        annotation_font=dict(size=14, family="Open Sans", color="grey"),
    )

    # Update layout aesthetics
    fig.update_layout(
        title_font=dict(family="Open Sans", size=22, color=spotify_dark),
        font=dict(family="Open Sans", size=14, color=spotify_dark),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=False, showline=True, linecolor="lightgrey", tickformat="%b %Y"),
        yaxis=dict(showgrid=False, showline=True, linecolor="lightgrey"),
    )

    return fig

