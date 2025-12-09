from dash import html, dcc
from utils.stats import get_first_listen_date, get_total_listening_time, get_uploaded_dataframe
from pathlib import Path
import re
import pandas as pd
import plotly.express as px

#dash.register_page(__name__, path="/listening-journey#introduction", name="Listening Journey - Introduction")

def _load_css_variables(path: str) -> dict:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except Exception:
        return {}
    pairs = re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', text)
    return {name: value.strip() for name, value in pairs}

"""
Build the introduction section. Accepts a pandas dataframe as input.
"""
def introduction_section(df=None):
    if df is None:
        df = get_uploaded_dataframe()

    if df is None or df.empty:
        return html.Div(className="section", children=[
            html.H2("Introduction - Error", className="heading-1"),
            html.Div(children=[html.P("Dataframe being passed into the function is empty", className="body")])
        ])

    css = _load_css_variables("assets/styles/variables.css")
    green500 = css.get("--color-green-500", "#1ED760")

    first_listen_date = get_first_listen_date(df)
    total_time = get_total_listening_time(df)
    total_time_graph = total_listening_time_line_graph(df)
    return html.Div(
        id="introduction",
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

            # First listen date and total listening time
            html.P(
                [
                    html.Span("You first hit play on ", className="body"),
                    html.B(first_listen_date, className="body"),
                    html.Br(),
                    html.Span("You've listened to Spotify for ", className="body"),
                    html.B(total_time, className="body"),
                    html.B(" Hours", className="body"),
                    html.Br(),
                    html.Span("That is equivalent to ", className="body"),
                    html.B(f"{total_time / 24:.1f} Days!", className="body"),
                ],
                className=None,
            ),

            # Heading for the total listening time graph
            html.Div(
                children=[
                    html.H3(
                        "Monthly Listening Time Over Your Spotify Journey",
                        className="heading-3"
                    )
                ]
            ),

            # Graph under the total listening time
            html.Div(
                children=[
                    dcc.Graph(
                        figure=total_time_graph,
                        config={"displayModeBar": True},
                        style={"backgroundColor": green500}
                    )
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
    # load CSS variables from `assets/styles/variables.css`
    css = _load_css_variables("assets/styles/variables.css")
    green100 = css.get("--color-green-100", "#93D5A3")
    green500 = css.get("--color-green-500", "#1ED760")
    black = css.get("--color-black", "#181414")
    grey600 = css.get("--color-grey-600", "#211D1D")
    grey400 = css.get("--color-grey-700", "#211D1D")

    if df is None or df.empty:
        return px.line()  # empty figure

    df = df.copy()

    # ensure timestamp column exists and is datetime
    if "ts" not in df.columns:
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

    df["month"] = df["ts"].dt.to_period("M").astype(str)
    monthly_play = (
        df.groupby("month", observed=False)
        .agg(hours=("hours_played", "sum"))
        .reset_index()
    )

    if monthly_play.empty:
        return px.line()

    monthly_play["month_dt"] = pd.to_datetime(monthly_play["month"])
    try:
        max_idx = monthly_play["hours"].idxmax()
        max_row = monthly_play.loc[max_idx]
    except Exception:
        max_row = None

    avg_hours = monthly_play["hours"].mean()

    # create line chart without a title (use page heading), set markers
    fig = px.line(
        monthly_play,
        x="month_dt",
        y="hours",
        markers=True,
        labels={"hours": "Hours Played", "month_dt": "Month"},
        title=None,
        line_shape="linear",
    )

    # Use CSS variable colors: line and main markers -> grey600
    fig.update_traces(mode="lines", line=dict(color=grey600, width=2)
                      #, marker=dict(size=8, color=grey600, line=dict(width=0))
                      )

    # Highlight the highest point using --color-black
    if max_row is not None:
        fig.add_scatter(
            x=[max_row["month_dt"]],
            y=[max_row["hours"]],
            mode="markers+text",
            marker=dict(color=black, size=14, symbol="circle", line=dict(color=black, width=2)),
            text=[f"{max_row['hours']:.1f} Hours"],
            textposition="top center",
            textfont=dict(size=12, color=black),
            showlegend=False,
        )

    fig.add_hline(
        y=avg_hours,
        line_dash="dash",
        line_color=grey400,
        opacity=0.6,
        annotation_text="Avg. Listening Time",
        annotation_position="top right",
        annotation_font=dict(size=12, color=grey400),
    )

    # Apply background colors from CSS variables and layout tweaks to avoid cutoff
    fig.update_layout(
        height=360,
        title_font=dict(size=18, color=black),
        font=dict(size=13, color=black),
        plot_bgcolor=green500,
        paper_bgcolor=green500,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor="rgba(0,0,0,0.12)",
            tickformat="%b %Y",
            tickangle=-45,
            tickfont=dict(size=11, color=black),
            tickmode="auto",
        ),
        yaxis=dict(
            showgrid=False,
            showline=True,
            linecolor="rgba(0,0,0,0.12)",
            tickfont=dict(size=11, color=black),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=green100,
            font_size=12,
            font_color=black,
            bordercolor=black
        ),
    )

    return fig

