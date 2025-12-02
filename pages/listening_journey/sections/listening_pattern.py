from dash import html, dcc
from utils.stats import get_uploaded_dataframe
import pandas as pd
import plotly.express as px


def listening_pattern_section(df=None):
    if df is None:
        df = get_uploaded_dataframe()

    if df is None or df.empty:
        return html.Div(
            className="section",
            children=[
                html.H2("Listening Patterns - Error", className="heading-1"),
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

    return html.Div(
        className="section",
        children=[
            html.H2("Listening Patterns", className="heading-1"),
            html.Div(
                children=[
                    html.P(
                        """
                        This section delves into your listening patterns analyzing how your music consumption varies from
                        day to day, week to week, and month to month. By examining these trends, we can uncover insights into
                        your listening habits, such as peak listening times, frequency of music engagement, and shifts in
                        your musical preferences over time. Whether you're a casual listener or a dedicated music enthusiast,
                        understanding these patterns can enhance your appreciation of your personal music journey.
                        """,
                        className="body"
                    )
                ]
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        figure=weekly_heatmap(
                            df,
                            metric="auto",
                            title="Your Listening Activity by Weekday and Hour"
                        ),
                        config={"displayModeBar": False},
                    )
                ]
            )
        ]

    )

"""
Build a weekday x hour heatmap using a single-hue green color scale
(hex values taken from `assets/styles/variables.css`).
metric: 'auto' (use hours if available else counts), 'hours' or 'count'.
Returns a plotly.graph_objects.Figure (via plotly.express.imshow).
"""
def weekly_heatmap(df, metric="auto", title="Listening Activity by Weekday and Hour"):

    # Greens from `assets/styles/variables.css` (light -> dark)
    greens = ["#93D5A3", "#1ED760", "#2C5C35", "#1E3E27"]

    if df is None:
        return px.imshow([[0]], labels=dict(x="Hour", y="Weekday"), x=[0], y=["No data"], color_continuous_scale=greens)

    df = df.copy()

    # find timestamp column
    ts_col = None
    for cand in ("ts", "played_at", "timestamp", "date"):
        if cand in df.columns:
            ts_col = cand
            break
    if ts_col is None:
        return px.imshow([[0]], labels=dict(x="Hour", y="Weekday"), x=[0], y=["No timestamp"], color_continuous_scale=greens)

    df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
    df = df.dropna(subset=[ts_col])
    if df.empty:
        return px.imshow([[0]], labels=dict(x="Hour", y="Weekday"), x=[0], y=["No valid timestamps"], color_continuous_scale=greens)

    df["hour"] = df[ts_col].dt.hour
    df["weekday"] = df[ts_col].dt.day_name()

    # decide metric
    use_hours = False
    if metric == "hours":
        use_hours = True
    elif metric == "count":
        use_hours = False
    else:  # auto
        if any(c in df.columns for c in ("hours_played", "ms_played", "duration_ms")):
            use_hours = True

    if use_hours:
        if "hours_played" in df.columns:
            df["hours"] = pd.to_numeric(df["hours_played"], errors="coerce").fillna(0)
        elif "ms_played" in df.columns:
            df["hours"] = pd.to_numeric(df["ms_played"], errors="coerce").fillna(0) / (1000 * 60 * 60)
        elif "duration_ms" in df.columns:
            df["hours"] = pd.to_numeric(df["duration_ms"], errors="coerce").fillna(0) / (1000 * 60 * 60)
        else:
            use_hours = False

    agg_val = "hours" if use_hours else "count"
    if agg_val == "count":
        agg_df = df.groupby(["weekday", "hour"], observed=False).size().reset_index(name="count")
    else:
        agg_df = df.groupby(["weekday", "hour"], observed=False)["hours"].sum().reset_index()

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hours = list(range(24))
    pivot = agg_df.pivot(index="weekday", columns="hour", values=agg_val if agg_val == "count" else "hours").reindex(weekdays).fillna(0)
    pivot = pivot.reindex(columns=hours, fill_value=0)

    fig = px.imshow(
        pivot.values,
        labels=dict(x="Hour of Day", y="Weekday", color="Hours" if use_hours else "Plays"),
        x=hours,
        y=weekdays,
        color_continuous_scale=greens,
        origin="lower",
        aspect="auto",
    )
    fig.update_xaxes(tickmode="array", tickvals=hours, ticktext=[str(h) for h in hours])
    fig.update_yaxes(autorange="reversed")  # Monday at top visually

    # annotate max cell
    try:
        import numpy as np
        max_idx = int(np.argmax(pivot.values))
        r, c = divmod(max_idx, pivot.shape[1])
        max_val = pivot.values[r, c]
        fig.add_annotation(
            x=hours[c],
            y=weekdays[r],
            text=f"{max_val:.1f}" if use_hours else f"{int(max_val)}",
            showarrow=False,
            font=dict(color="white", size=12),
            bgcolor="rgba(0,0,0,0.4)",
        )
    except Exception:
        pass

    fig.update_layout(title=title, margin=dict(l=40, r=20, t=50, b=40))
    return fig

