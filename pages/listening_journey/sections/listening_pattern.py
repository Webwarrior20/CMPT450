from dash import html, dcc
from utils.stats import get_uploaded_dataframe, get_most_listened_day, get_most_listened_hour, get_most_listened_overall_day
from utils.css_vars import load_css_variables
import pandas as pd
import numpy as np
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

    else:
        # calculate most listened to day of the week
        most_listened_day = get_most_listened_day(df)
        # figure out if the user listens more during the day or at night
        most_listened_hours_array = get_most_listened_hour(df)
        if not most_listened_hours_array or len(most_listened_hours_array) == 0:
            most_listened_hour = "N/A"
        else:
            # determine if most listened hours are during the day (6 AM to 6 PM) or night (6 PM to 6 AM)
            day_hours = [h for h in most_listened_hours_array if 6 <= h < 18]
            night_hours = [h for h in most_listened_hours_array if h < 6 or h >= 18]
            if len(day_hours) >= len(night_hours):
                most_listened_hour = "Day"
            else:
                most_listened_hour = "Night"

        # Get the peak hour value
        peak_val = most_listened_hours_array[0] if most_listened_hours_array else None
        format_hour = (lambda
                           h: "N/A" if h is None else f"{12 if (int(h) % 12) == 0 else (int(h) % 12)} {'AM' if int(h) < 12 else 'PM'}")
        formatted_peak = format_hour(peak_val)
        # calulate which day user listened to the most (total hours)
        most_listened_overall_day, total_hour = get_most_listened_overall_day(df)

    return html.Div(
        id="listening-pattern",
        className="section",
        children=[
            html.H2("Listening Patterns", className="heading-1"),
            html.Div(
                children=[
                    html.P(
                        """
                        This section delves into your listening patterns analyzing how your music consumption varies from
                        day to day, week to week, and month to month. By examining these trends, we can uncover insights into
                        your listening habits, such as peak listening times and frequency of music engagement. 
                        Whether you're a casual listener or a dedicated music enthusiast, understanding these patterns 
                        can enhance your appreciation of your personal music journey.
                        """,
                        className="body"
                    )
                ]
            ),

            # Quick stats for Listening Patterns
            html.P(
                [
                    html.Span("You listen the most on ", className="body"),
                    html.B(f"{most_listened_day}s", className="body"),
                    html.Br(),
                    html.Span("You listen more during the ", className="body"),
                    html.B(most_listened_hour, className="body"),
                    html.Span(" with a peak at ", className="body"),
                    html.B(formatted_peak, className="body"),
                    html.Br(),
                    html.Span("Your most listened to day was ", className="body"),
                    html.B(most_listened_overall_day, className="body"),
                    html.Span(" where you listened for ", className="body"),
                    html.B(f"{total_hour / 3_600_000:.1f} Hours!", className="body"), # Convert ms to hours
                ],
                className=None,
            ),

            html.Div(
                children=[
                    html.H3(
                        "Your Listening Activity by Weekday and Hour",
                        className="heading-3"
                    )
                ]
            ),


            html.Div(
                children=[
                    dcc.Graph(
                        figure=weekly_heatmap(
                            df,
                            metric="auto"
                        ),
                        config={"displayModeBar": True},
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
def weekly_heatmap(df, metric="auto", title=None):
    """
    Weekday x hour heatmap. Uses 12-hour tick labels for the x-axis and
    does not annotate the maximum cell.
    """
    # load CSS vars
    css = load_css_variables("assets/styles/variables.css")
    green100 = css.get("--color-green-100", "#93D5A3")
    green500 = css.get("--color-green-500", "#1ED760")
    green700 = css.get("--color-green-700", "#2C5C35")
    green900 = css.get("--color-green-900", "#1E3E27")
    black = css.get("--color-black", "#181414")
    grey600 = css.get("--color-grey-600", "#211D1D")

    # build a sequential greenscale from light to dark using CSS vars
    greenscale = [green100, green500, green700, green900]

    if df is None:
        return px.imshow([[0]], labels=dict(x="Hour", y="Weekday"), x=[0], y=["No data"], color_continuous_scale=greenscale)

    df = df.copy()

    # find timestamp column
    ts_col = None
    for cand in ("ts", "played_at", "timestamp", "date"):
        if cand in df.columns:
            ts_col = cand
            break
    if ts_col is None:
        return px.imshow([[0]], labels=dict(x="Hour", y="Weekday"), x=[0], y=["No timestamp"], color_continuous_scale=greenscale)

    df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
    df = df.dropna(subset=[ts_col])
    if df.empty:
        return px.imshow([[0]], labels=dict(x="Hour", y="Weekday"), x=[0], y=["No valid timestamps"], color_continuous_scale=greenscale)

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

    # 12-hour labels for the x-axis (keep 24 columns, label as 12\-hour)
    hour_labels = [f"{12 if (h % 12) == 0 else (h % 12)} {'AM' if h < 12 else 'PM'}" for h in hours]

    # create heatmap without a figure title (title handled outside)
    fig = px.imshow(
        pivot.values,
        labels=dict(x="Hour of Day", y="Weekday", color="Hours" if use_hours else "Plays"),
        x=hours,
        y=weekdays,
        color_continuous_scale=greenscale,
        origin="lower",
        aspect="auto",
    )

    fig.update_xaxes(tickmode="array", tickvals=hours, ticktext=hour_labels)
    fig.update_yaxes(autorange="reversed")  # Monday at top visually

    # removed max-cell annotation as requested

    # style to blend with page background (use grey600)
    fig.update_traces(
        hovertemplate="%{y} %{x}: %{z}<extra></extra>",
        selector=dict(type="heatmap"),
        colorbar=dict(
            bgcolor=grey600,
            tickfont=dict(color=green100),
            outlinewidth=0,
            thickness=10,
        )
    )

    fig.update_layout(
        # no embedded title; title is placed in layout above the graph
        margin=dict(l=40, r=20, t=10, b=40),
        plot_bgcolor=grey600,
        paper_bgcolor=grey600,
        font=dict(size=13, color=green100),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor="rgba(0,0,0,0.12)",
            tickfont=dict(size=11, color=green100),
        ),
        yaxis=dict(
            showgrid=False,
            showline=True,
            linecolor="rgba(0,0,0,0.12)",
            tickfont=dict(size=11, color=green100),
        ),
        hoverlabel=dict(
            bgcolor=green500,
            font_size=12,
            font_color=black,
            bordercolor=black
        ),
    )

    # optionally set color range to data min/max for consistent mapping
    try:
        fig.data[0].zmin = float(pivot.values.min())
        fig.data[0].zmax = float(pivot.values.max())
    except Exception:
        pass

    return fig

