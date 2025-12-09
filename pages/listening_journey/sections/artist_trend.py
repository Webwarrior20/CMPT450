from dash import html, dcc
import plotly.express as px
import pandas as pd
from utils.css_vars import load_css_variables

def _load_style_vars():
    css = load_css_variables("assets/styles/variables.css")
    green0   = css.get("--color-green-0"  , "#016250")
    green100 = css.get("--color-green-100", "#93D5A3")
    green500 = css.get("--color-green-500", "#1ED760")
    green700 = css.get("--color-green-700", "#2C5C35")
    green900 = css.get("--color-green-900", "#1E3E27")
    black = css.get("--color-black", "#181414")
    grey600 = css.get("--color-grey-600", "#211D1D")
    return {
        "green0": green0,
        "green100": green100,
        "green500": green500,
        "green700": green700,
        "green900": green900,
        "black": black,
        "grey600": grey600,
    }

def artist_trend_section(df):
    if df is None or df.empty:
        return html.Div(
            className="section",
            children=[
                html.H2("Artist Trends - Error", className="heading-1"),
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
            html.H2("Artist Trends", className="heading-1"),
            html.Div(
                children=[
                    html.P(
                "This section explores your top artists over time, showcasing who you've listened to the most "
                "and how your preferences have evolved. Discover your musical obsessions and see how your favorite "
                "artists rank.",
                        className="body"
                    )
                ]
            ),

            html.Div(
                children=[
                    html.H3(
                        "Top 10 Artists of All Time",
                        className="heading-3"
                    )
                ]
            ),

            html.Div(
                children=[
                    dcc.Graph(
                        figure=build_artist_bar_figure(df, top_n=10),
                        config={"displayModeBar": False, "responsive": True},
                        style={"width": "100%"},
                    )
                ]
            ),

            html.Div(
                children=[
                    html.P(
                        "The bar chart above displays your top 10 artists based on total hours played. "
                        "This visualization highlights the artists you've spent the most time listening to"
                        ", reflecting your enduring favorites and musical influences over your listening journey.",
                        className="body"
                    )
                ]
            ),

            html.Div(
                children=[
                    html.H3(
                        "Artist Bump Chart",
                        className="heading-3"
                    )
                ]
            ),

            html.Div(
                children=[
                    dcc.Graph(
                        figure=create_bump_chart(df, top_n=5),
                        config={"displayModeBar": True, "responsive": True},
                        style={"width": "100%"},
                    )
                ]
            ),

            html.Div(
                children=[
                    html.P(
                        " The bump chart above illustrates how your top 5 artists' rankings have changed over time."
                        " This visualization helps you see shifts in your listening habits and which artists have gained "
                        "or lost favor in your musical journey.",
                        className="body"
                    )
                ]
            ),

            html.Div(
                children=[
                    html.H3(
                        "How Well Do You Know Your Top Artists?",
                        className="heading-3"
                    )
                ]
            ),

            html.Div(
                children=[
                    dcc.Graph(
                        figure=create_obsession_scatter(df),
                        config={"displayModeBar": True, "responsive": True},
                        style={"width": "100%"},
                    )
                ]
            ),

            html.Div(
                children=[
                    html.P(
                        "The scatter plot above compares the number of unique tracks you've listened to "
                        "from your top artists against the total hours you've spent listening to them. "
                        "This visualization reveals your depth of engagement (or obsession) with each artist.",
                        className="body"
                    ),
                ]
            ),
        ]
    )

def build_artist_bar_figure(df, top_n: int = 10):
    """
    Build and return a horizontal bar Plotly figure for top artists by hours played.
    """
    if df is None or df.empty:
        raise ValueError("Dataframe is empty")

    styles = _load_style_vars()

    group_key = 'master_metadata_album_artist_name'
    if 'ms_played' in df.columns:
        artist_stats = df.groupby(group_key, observed=False).agg(
            ms_played=('ms_played', 'sum'),
            song_count=('master_metadata_track_name', 'count')
        ).reset_index()
        artist_stats['hours_played'] = artist_stats['ms_played'] / 3_600_000
    elif 'hours_played' in df.columns:
        artist_stats = df.groupby(group_key, observed=False).agg(
            hours_played=('hours_played', 'sum'),
            song_count=('master_metadata_track_name', 'count')
        ).reset_index()
    else:
        raise ValueError("Dataframe must contain either `ms_played` or `hours_played` column")
    top_artists = artist_stats.sort_values('hours_played', ascending=False).head(top_n)

    fig = px.bar(
        top_artists,
        x='hours_played',
        y=group_key,
        orientation='h',
        text='hours_played',
        labels={'hours_played': 'Hours Played', group_key: 'Artist'},
    )
    fig.update_traces(
        marker_color=styles["green500"],
        texttemplate='%{x:.2f} h',
        textfont=dict(color=styles["black"]),
        selector=dict(type="bar")
    )
    fig.update_layout(
        autosize=True,
        plot_bgcolor=styles["grey600"],
        paper_bgcolor=styles["grey600"],
        font=dict(family='Open Sans', size=14, color=styles["green100"]),
        xaxis=dict(showgrid=False, showline=True, linecolor="rgba(0,0,0,0.12)"),
        yaxis=dict(showgrid=False, showline=True, linecolor="rgba(0,0,0,0.12)", autorange='reversed'),
        showlegend=False,
        margin=dict(t=10, l=10, r=10, b=10),
        height=380,
        hoverlabel=dict(
            bgcolor=styles["green500"],
            font_size=12,
            font_color=styles["black"],
            bordercolor=styles["black"]
        )
    )
    return fig

def create_bump_chart(df, top_n=5, period='M'):
    """
    Creates a bump chart showing how artist rankings change over time.
    - Detects artist and timestamp column names from common alternatives.
    - Uses `ms_played` or `hours_played` as the play metric.
    """
    if df is None or df.empty:
        raise ValueError("Dataframe is empty")

    styles = _load_style_vars()
    df = df.copy()

    # detect artist column
    artist_candidates = [
        'artist_name',
        'master_metadata_album_artist_name',
        'master_metadata_artist_name',
        'artist'
    ]
    artist_col = next((c for c in artist_candidates if c in df.columns), None)
    if artist_col is None:
        raise ValueError(f"Missing artist column. Available columns: {df.columns.tolist()}")

    # detect timestamp column
    ts_candidates = ['ts', 'played_at', 'timestamp', 'time', 'date']
    ts_col = next((c for c in ts_candidates if c in df.columns), None)
    if ts_col is None:
        raise ValueError(f"Missing timestamp column. Available columns: {df.columns.tolist()}")

    # detect play metric
    if 'ms_played' in df.columns:
        df['play_value'] = df['ms_played']
    elif 'hours_played' in df.columns:
        df['play_value'] = df['hours_played']
    else:
        raise ValueError("Dataframe must contain either `ms_played` or `hours_played` column")

    # ensure timestamp is datetime
    df[ts_col] = pd.to_datetime(df[ts_col], errors='coerce')
    if df[ts_col].isna().all():
        raise ValueError(f"Could not parse any datetimes from column `{ts_col}`")

    # create period column and aggregate
    df['period'] = df[ts_col].dt.to_period(period).astype(str)
    period_plays = df.groupby(['period', artist_col])['play_value'].sum().reset_index()

    # compute rank within each period
    period_plays['rank'] = period_plays.groupby('period')['play_value'] \
                                       .rank(method='first', ascending=False)

    # select stable top N artists overall
    top_artists_list = df.groupby(artist_col)['play_value'].sum().nlargest(top_n).index
    filtered_data = period_plays[period_plays[artist_col].isin(top_artists_list)] \
                    .sort_values(['period', 'rank'])

    # plot
    fig = px.line(
        filtered_data,
        x='period',
        y='rank',
        color=artist_col,
        markers=True,
        labels={'period': 'Time Period', 'rank': 'Rank', artist_col: 'Artist'},
        color_discrete_sequence=[styles["green0"], styles["green100"], styles["green700"],
                                 styles["green500"], styles["green900"]],
        template="plotly_white"
    )
    fig.update_traces(line=dict(width=2), marker=dict(size=6))
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        autosize=True,
        plot_bgcolor=styles["grey600"],
        paper_bgcolor=styles["grey600"],
        font=dict(family='Open Sans', size=13, color=styles["green100"]),
        xaxis=dict(showgrid=False, showline=True, linecolor="rgba(0,0,0,0.12)"),
        yaxis=dict(showgrid=False, showline=True, linecolor="rgba(0,0,0,0.12)"),
        margin=dict(t=30, l=40, r=20, b=40),
        height=400,
        hoverlabel=dict(
            bgcolor=styles["green500"],
            font_size=12,
            font_color=styles["black"],
            bordercolor=styles["black"]
        )
    )
    return fig

def create_obsession_scatter(df):
    """
    Creates a scatter plot comparing Breadth (Unique Tracks) vs Depth (Hours Played).
    - Detects artist and track column names from common alternatives.
    - Uses `ms_played`, `total_ms`, or `hours_played` as the play metric.
    """
    if df is None or df.empty:
        raise ValueError("Dataframe is empty")

    styles = _load_style_vars()
    df = df.copy()

    # detect artist column
    artist_candidates = [
        'artist_name',
        'master_metadata_album_artist_name',
        'master_metadata_artist_name',
        'artist'
    ]
    artist_col = next((c for c in artist_candidates if c in df.columns), None)
    if artist_col is None:
        raise ValueError(f"Missing artist column. Available columns: {df.columns.tolist()}")

    # detect track column
    track_candidates = [
        'track_name',
        'master_metadata_track_name',
        'name',
        'track'
    ]
    track_col = next((c for c in track_candidates if c in df.columns), None)
    if track_col is None:
        raise ValueError(f"Missing track column. Available columns: {df.columns.tolist()}")

    # detect/compute hours_played
    if 'hours_played' in df.columns:
        df['hours_played'] = df['hours_played']
    elif 'ms_played' in df.columns:
        df['hours_played'] = df['ms_played'] / 3_600_000
    elif 'total_ms' in df.columns:
        df['hours_played'] = df['total_ms'] / 3_600_000
    else:
        raise ValueError("Dataframe must contain one of `ms_played`, `total_ms`, or `hours_played`")

    # 1. Aggregate data
    obsess_data = df.groupby(artist_col).agg(
        unique_tracks=(track_col, 'nunique'),
        hours_played=('hours_played', 'sum')
    ).reset_index()

    # 2. Plot
    fig = px.scatter(
        obsess_data,
        x='unique_tracks',
        y='hours_played',
        hover_name=artist_col,
        size='hours_played',
        color='unique_tracks',
        labels={'unique_tracks': 'Unique Tracks', 'hours_played': 'Hours Played'},
        color_continuous_scale=[styles["green100"], styles["green500"], styles["green900"]],
    )

    fig.update_traces(marker=dict(opacity=0.9, line=dict(width=1, color=styles["grey600"])))
    avg_x = obsess_data['unique_tracks'].mean()
    avg_y = obsess_data['hours_played'].mean()

    fig.add_hline(y=avg_y, line_dash="dash", line_color="rgba(255,255,255,0.15)", annotation_text="Avg Hours")
    fig.add_vline(x=avg_x, line_dash="dash", line_color="rgba(255,255,255,0.15)", annotation_text="Avg Tracks")

    fig.update_layout(
        autosize=True,
        plot_bgcolor=styles["grey600"],
        paper_bgcolor=styles["grey600"],
        font=dict(family='Open Sans', size=13, color=styles["green100"]),
        xaxis=dict(showgrid=False, showline=True, linecolor="rgba(0,0,0,0.12)"),
        yaxis=dict(showgrid=False, showline=True, linecolor="rgba(0,0,0,0.12)"),
        margin=dict(t=30, l=40, r=20, b=40),
        height=420,
        hoverlabel=dict(
            bgcolor=styles["green500"],
            font_size=12,
            font_color=styles["black"],
            bordercolor=styles["black"]
        )
    )

    return fig