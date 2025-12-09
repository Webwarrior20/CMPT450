from dash import html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd
from utils.css_vars import load_css_variables

# --- GLOBAL DATA HOLDER ---
df_for_callback = None

def _load_style_vars():
    css = load_css_variables("assets/styles/variables.css")
    return {
        "purple0": css.get("--color-purple-0", "#4E3750"),
        "green0": css.get("--color-green-0", "#016250"),
        "green100": css.get("--color-green-100", "#93D5A3"),
        "green500": css.get("--color-green-500", "#1ED760"),
        "blue300": css.get("--color-blue-300", "#0D70E4"),
        "red0": css.get("--color-red-0", "#BF182E"),
        "green700": css.get("--color-green-700", "#2C5C35"),
        "black": css.get("--color-black", "#181414"),
        "grey600": css.get("--color-grey-600", "#211D1D"),
        "grey500": css.get("--color-grey-500", "#2A2626"),
        "grey400": css.get("--color-grey-400", "#343131"),
        "grey300": css.get("--color-grey-300","#464343"),
        "grey200": css.get("--color-grey-200","#5D5A5A"),
        "grey100": css.get("--color-grey-100","#747272"),
        "grey0": css.get("--color-grey-0","#8B8989"),
        "green900": css.get("--color-green-900", "#1E3E27"),
        "white": css.get("--color-white", "#FFFFFF"),
    }

def song_trend_section(df):
    global df_for_callback
    df_for_callback = df
    styles = _load_style_vars()

    if df is None or df.empty:
        return html.Div(
            className="section",
            children=[
                html.H2("Song Trends - Error", className="heading-1"),
                html.Div(html.P("Dataframe is empty", className="body"))
            ]
        )

    # --- PREPARE DATA ---
    track_col = "master_metadata_track_name"

    # 1. Get the #1 most played song for the default value
    most_played_song = df[track_col].mode()[0] if not df.empty else None

    # 2. Prepare Dropdown List
    song_counts = df[track_col].value_counts()
    popular_songs = song_counts[song_counts > 5].index.sort_values().tolist()

    return html.Div(
        className="section",
        children=[
            html.H2("Song Trends", className="heading-1"),
            html.Div(
                children=[
                    html.P(
                        "Dive into your listening habits at the song level."
                        " See your all-time favorites and analyze exactly when you listen to them."
                        " Understand if certain songs are tied to specific times of day or days of the week"
                        " and maybe it'll reveal some interesting patterns about your music preferences!",
                        className="body"
                    )
                ]
            ),

            # --- TOP 10 SONGS ---
            html.Div(children=[html.H3("Top 10 Songs of All Time", className="heading-3")]),
            html.Div(
                children=[
                    dcc.Graph(
                        figure=build_top_songs_figure(df),
                        config={"displayModeBar": False, "responsive": True},
                        style={"width": "100%", "height": "400px"},
                    )
                ]
            ),

            # --- SECTION 2: DEEP DIVE ---
            html.Div(children=[html.H3("Song Deep Dive", className="heading-3")]),

            html.Div(
                children=[
                    html.P("Select a song to analyze its Daily and Monthly patterns:", className="body"),

                    dcc.Dropdown(
                        id='song-trend-dropdown',
                        options=[{'label': s, 'value': s} for s in popular_songs],
                        value=most_played_song,
                        clearable=False,
                        searchable=True,
                        placeholder="Type to search...",
                        style={'backgroundColor': styles['white'], 'color': '#000', 'marginBottom': '20px'}
                    ),
                ]
            ),

            # CHART A: HEATMAP
            html.Div(
                children=[
                    html.H4("Time of Day & Week", className="heading-4"),
                    dcc.Graph(
                        id='song-heatmap-graph',
                        config={"displayModeBar": False, "responsive": True},
                        style={"width": "100%", "height": "600px"},
                    )
                ]
            ),

            # CHART B: MONTHLY TREND
            html.Div(
                children=[
                    html.H4("Trends Over the Years", className="heading-4"),
                    dcc.Graph(
                        id='song-monthly-graph',
                        config={"displayModeBar": False, "responsive": True},
                        style={"width": "100%", "height": "450px"},
                    ),
                    html.P(
                        "The charts above shows the daily, weekly and monthly listening for the selected song. "
                        "This helps identify if a song was a temporary 'phase' or a long-term favorite.",
                        className="body",
                        style={'marginTop': '10px'}
                    )
                ],
                style={'marginTop': '30px'}
            ),
        ]
    )


# --- CALLBACKS ---
@callback(
    [Output('song-heatmap-graph', 'figure'),
     Output('song-monthly-graph', 'figure')],
    Input('song-trend-dropdown', 'value')
)
def update_song_graphs(selected_song):
    if df_for_callback is None or df_for_callback.empty or not selected_song:
        return {}, {}

    fig_heatmap = create_song_heatmap(df_for_callback, selected_song)
    fig_monthly = create_monthly_trend(df_for_callback, selected_song)

    return fig_heatmap, fig_monthly


def build_top_songs_figure(df, top_n=10):
    styles = _load_style_vars()
    track_col = "master_metadata_track_name"
    df = df.copy()

    if "hours_played" not in df.columns:
        if "ms_played" in df.columns:
            df["hours_played"] = df["ms_played"] / 3_600_000
        elif "total_ms" in df.columns:
            df["hours_played"] = df["total_ms"] / 3_600_000

    song_stats = df.groupby(track_col, observed=False).agg(
        hours_played=("hours_played", "sum")
    ).reset_index()

    song_stats["hours_played"] = song_stats["hours_played"].round(2)
    top_songs = song_stats.sort_values("hours_played", ascending=False).head(top_n).reset_index(drop=True)

    fig = px.bar(
        top_songs,
        x="hours_played",
        y=track_col,
        orientation="h",
        text="hours_played",
        labels={"hours_played": "Hours Played", track_col: "Artists"},
        title=""
    )
    # bar styles
    fig.update_traces(
        marker=dict(
            color=styles["green700"],
            line=dict(color=styles["green900"], width=1.5)  # outline color & thickness
        ),
        texttemplate="%{x:.2f} h",
        textfont_color=styles["white"],
        selector=dict(type="bar")
    )

    # layout using greys as primary colors
    fig.update_layout(
        autosize=True,
        plot_bgcolor=styles["green500"],
        paper_bgcolor=styles["green500"],
        font=dict(family="Open Sans", size=14, color=styles["black"]),
        xaxis=dict(title="Hours Played", showgrid=False, showline=True, linecolor="rgba(0,0,0,0.12)",
                   tickfont=dict(color=styles["black"])),
        yaxis=dict(
            title="Artists",
            showticklabels=True,
            tickfont=dict(color=styles["black"], size=13),
            autorange="reversed",
            showgrid=False,
            automargin=True
        ),
        showlegend=False,
        margin=dict(t=10, l=200, r=10, b=10),
        height=380,
        hoverlabel=dict(
            bgcolor=styles["green100"],
            font_size=12,
            font_color=styles["black"],
            bordercolor=styles["black"]
        )
    )

    return fig

def create_song_heatmap(df, song_name):
    styles = _load_style_vars()
    # Filter
    song_df = df[df['master_metadata_track_name'] == song_name].copy()

    # find timestamp column safely
    ts_col = None
    for cand in ("ts", "played_at", "timestamp", "date"):
        if cand in song_df.columns:
            ts_col = cand
            break

    if ts_col is None:
        return px.imshow([[0]], labels=dict(x="Hour of Day", y="Day", color="Plays"),
                         x=[0], y=["No timestamp"], color_continuous_scale=[styles["grey100"], styles["grey300"], styles["grey500"], styles["grey600"]])

    # ensure ts is datetime and drop rows without valid timestamps
    song_df[ts_col] = pd.to_datetime(song_df[ts_col], errors='coerce')
    song_df = song_df.dropna(subset=[ts_col])
    if song_df.empty:
        return px.imshow([[0]], labels=dict(x="Hour of Day", y="Day", color="Plays"),
                         x=[0], y=["No data"], color_continuous_scale=[styles["grey100"], styles["grey300"], styles["grey500"], styles["grey600"]])

    # Extract hour and weekday
    song_df['hour'] = song_df[ts_col].dt.hour
    song_df['weekday'] = song_df[ts_col].dt.day_name()

    # Aggregate plays by weekday/hour
    agg = song_df.groupby(['weekday', 'hour'], observed=False).size().reset_index(name='plays')

    # Ensure Monday -> Sunday order and 0..23 columns
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hours = list(range(24))
    pivot = agg.pivot(index='weekday', columns='hour', values='plays').reindex(weekdays).fillna(0)
    pivot = pivot.reindex(columns=hours, fill_value=0)

    # 12-hour labels for x-axis
    hour_labels = [f"{12 if (h % 12) == 0 else (h % 12)} {'AM' if h < 12 else 'PM'}" for h in hours]

    # use the same green scale as listening_pattern, keep background color unchanged
    greenscale = [styles["green100"], styles["green500"], styles["green700"], styles["green900"]]

    fig = px.imshow(
        pivot.values,
        labels=dict(x="Hour of Day", y="Weekday", color="Plays"),
        x=hours,
        y=weekdays,
        color_continuous_scale=greenscale,
        origin="lower",
        aspect="auto",
    )

    fig.update_xaxes(tickmode="array", tickvals=hours, ticktext=hour_labels, dtick=2,
                     tickfont=dict(size=11, color=styles["black"]))
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=11, color=styles["black"]))

    fig.update_traces(
        hovertemplate="%{y} %{x}: %{z}<extra></extra>",
        selector=dict(type="heatmap"),
        colorbar=dict(
            bgcolor=styles["grey600"],
            tickfont=dict(color=styles["green100"]),
            outlinewidth=0,
            thickness=10,
        )
    )

    fig.update_layout(
        title=dict(text=f"When do you listen to '{song_name}'?", x=0.5),
        margin=dict(l=40, r=20, t=50, b=40),
        plot_bgcolor=styles["green500"],
        paper_bgcolor=styles["green500"],
        font=dict(size=13, color=styles["black"], family="Open Sans"),
        xaxis=dict(showgrid=False, showline=True, linecolor="rgba(0,0,0,0.12)"),
        yaxis=dict(showgrid=False, showline=True, linecolor="rgba(0,0,0,0.12)"),
        hoverlabel=dict(
            bgcolor=styles["green100"],
            font_size=12,
            font_color=styles["black"],
            bordercolor=styles["grey400"]
        ),
    )

    # add border around heatmap for easier reading
    border_color = styles["green900"]
    fig.add_shape(
        type="rect",
        xref="x",
        yref="y",
        x0=min(hours) - 0.5,
        x1=max(hours) + 0.5,
        y0=-0.5,
        y1=len(weekdays) - 0.5,
        line=dict(color=border_color, width=2),
        fillcolor="rgba(0,0,0,0)",  # transparent fill
        layer="above"
    )

    try:
        fig.data[0].zmin = float(pivot.values.min())
        fig.data[0].zmax = float(pivot.values.max())
    except Exception:
        pass

    return fig

def create_monthly_trend(df, song_name):
    styles = _load_style_vars()
    # Filter
    song_df = df[df['master_metadata_track_name'] == song_name].copy()

    # Group by Month
    song_df['ts'] = pd.to_datetime(song_df['ts'], errors='coerce')
    song_df['month_str'] = song_df['ts'].dt.to_period('M').astype(str)
    monthly_data = song_df.groupby('month_str').size().reset_index(name='plays')

    # Plot
    fig = px.bar(
        monthly_data,
        x='month_str',
        y='plays',
        title=f"Monthly Trends: {song_name}"
    )

    # bar styles
    fig.update_traces(
        marker=dict(
            color=styles["green700"],
            line=dict(color=styles["green900"], width=1.5)
        ),
        selector=dict(type="bar")
    )

    fig.update_layout(
        plot_bgcolor=styles["green500"],
        paper_bgcolor=styles["green500"],
        margin=dict(l=20, r=20, t=50, b=40),
        xaxis=dict(title="Month", showgrid=False, tickfont=dict(color=styles["black"])),
        yaxis=dict(title="Total Plays", showgrid=True, gridcolor='rgba(255,255,255,0.06)', tickfont=dict(color=styles["black"])),
        autosize=True,
        font=dict(family="Open Sans", size=13, color=styles["black"]),
        hoverlabel=dict(bgcolor=styles["green100"], font_color=styles["black"])
    )

    return fig
