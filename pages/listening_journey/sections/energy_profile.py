from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

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
        "grey300": css.get("--color-grey-300", "#464343"),
        "grey200": css.get("--color-grey-200", "#5D5A5A"),
        "grey100": css.get("--color-grey-100", "#747272"),
        "grey0": css.get("--color-grey-0", "#8B8989"),
        "green900": css.get("--color-green-900", "#1E3E27"),
        "white": css.get("--color-white", "#FFFFFF"),
    }


def energy_profile_section(df):
    global df_for_callback
    styles = _load_style_vars()

    # --- 1. DATA PREP ---
    if df is None or df.empty:
        return html.Div(children=[html.P("Dataframe is empty", className="body")])

    # Ensure datetime
    df_chart = df.copy()
    if 'ts' in df_chart.columns and not pd.api.types.is_datetime64_any_dtype(df_chart['ts']):
        df_chart['ts'] = pd.to_datetime(df_chart['ts'])

    # Mock Data Logic (if audio features missing)
    features = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'valence']
    missing_cols = [c for c in features if c not in df_chart.columns]
    if missing_cols:
        np.random.seed(42)
        for c in missing_cols:
            df_chart[c] = np.random.uniform(0, 1, size=len(df_chart))

    # Save to global for callback
    df_for_callback = df_chart

    # Prepare Dropdown List (Popular songs first)
    track_col = "master_metadata_track_name"
    # Fallback if column name differs
    if track_col not in df_chart.columns:
        track_col = "track_name" if "track_name" in df_chart.columns else df_chart.columns[0]

    song_counts = df_chart[track_col].value_counts()
    popular_songs = song_counts[song_counts > 5].index.tolist()
    default_song = popular_songs[0] if popular_songs else None

    # --- 2. LAYOUT ---
    return html.Div(
        className="section",
        children=[
            html.H2("Energy Profile", className="heading-1"),
            html.P("This section uses your data along with a dataset containing over two million songs and their"
                   " track features. This includes data such as Danceability, Energy, Acousticness, Speechiness, "
                   " Instramentalness, and Valence. These features can explain what kind of music you like and find songs"
                   " that fit into your music taste.", className="body"),

            html.H3("Danceability", className="heading-3"),
            html.P("Danceability describes how suitable a track is for dancing based on a combination of musical "
                   "elements including tempo, rhythm stability, beat strength, and overall regularity. "
                   "A value of 0.0 is least danceable and 1.0 is most danceable.", className="body"),

            html.H3("Energy", className="heading-3"),
            html.P("Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and "
                   "activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high "
                   "energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this"
                   " attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.",
                   className="body"),


            html.H3("Speechiness", className="heading-3"),
            html.P("Speechiness detects the presence of spoken words in a track. The more exclusively "
                   "speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value."
                   " Values above 0.66 describe tracks that are probably made entirely of spoken words. "
                   "Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in "
                   "sections or layered, including such cases as rap music. Values below 0.33 most likely represent "
                   "music and other non-speech-like tracks.",
                   className="body"),

            html.H3("Acousticness", className="heading-3"),
            html.P("A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high "
                   "confidence the track is acoustic.",
                   className="body"),

            html.H3("Instrumentalness", className="heading-3"),
            html.P(
                "Predicts whether a track contains no vocals. \"Ooh\" and \"aah\" sounds are treated as instrumental "
                "in this context. Rap or spoken word tracks are clearly \"vocal\". The closer the instrumentalness"
                " value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are"
                " intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.",
                className="body"),

            html.H3("Valence", className="heading-3"),
            html.P("A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks "
                   "with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low "
                   "valence sound more negative (e.g. sad, depressed, angry).",
                   className="body"),

            # --- FEATURE DISTRIBUTIONS (New Section) ---
            html.Div(
                children=[
                    html.H3("Feature Distributions", className="heading-3", style={'marginTop': '50px'}),
                    html.P(
                        "The following histograms show the distribution of these 6 audio features across your "
                        "entire library.",
                        className="body"),
                    create_feature_histograms(df_chart, styles)
                ]
            ),

            html.P(
                "Compare your overall music taste (Left) against specific songs (Right). "
                "The green shape represents the audio signature.",
                className="body",
                style={'marginBottom': '30px', 'marginTop': '50px'}
            ),

            # --- SPLIT VIEW CONTAINER ---
            html.Div(
                style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px', 'justifyContent': 'center'},
                children=[

                    # LEFT COLUMN: LIBRARY AVERAGE
                    html.Div(
                        style={'flex': '1', 'minWidth': '300px', 'maxWidth': '500px'},
                        children=[
                            html.H3("Your Library Aura", className="heading-3", style={'textAlign': 'center'}),
                            dcc.Graph(
                                figure=create_library_radar(df_chart),
                                config={"displayModeBar": False},
                                style={'height': '450px', 'backgroundColor': styles["grey600"]}
                            )
                        ]
                    ),

                    # RIGHT COLUMN: SONG COMPARISON (dropdown removed from here)
                    html.Div(
                        style={'flex': '1', 'minWidth': '300px', 'maxWidth': '500px'},
                        children=[
                            html.H3("Song Comparator", className="heading-3", style={'textAlign': 'center'}),

                            # Interactive Graph
                            dcc.Graph(
                                id='energy-song-radar',
                                config={"displayModeBar": False},
                                style={'height': '450px', 'backgroundColor': styles["grey600"]}
                            ),
                        ]
                    )
                ]
            ),

            # Full-width white search bar spanning both graphs
            html.Div(
                style={'maxWidth': '1000px', 'margin': '18px auto 0', 'width': '100%'},
                children=[
                    dcc.Dropdown(
                        id='energy-song-dropdown',
                        options=[{'label': s, 'value': s} for s in popular_songs],
                        value=default_song,
                        clearable=False,
                        searchable=True,
                        placeholder="Select a song...",
                        style={
                            'backgroundColor': styles['white'],
                            'color': '#000',
                            'width': '100%',
                            'border': '1px solid rgba(0,0,0,0.12)',
                            'borderRadius': '8px',
                            'padding': '6px'
                        }
                    )
                ]
            ),
        ]
    )


# --- CALLBACKS ---
@callback(
    Output('energy-song-radar', 'figure'),
    Input('energy-song-dropdown', 'value')
)
def update_song_radar(selected_song):
    if df_for_callback is None or not selected_song:
        return go.Figure()

    return create_comparison_radar(df_for_callback, selected_song)


# --- HELPER FUNCTIONS ---
def create_feature_histograms(df, styles):
    features = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'valence']
    graphs = []

    for feature in features:
        # Create Histogram
        fig = px.histogram(
            df,
            x=feature,
            nbins=30,
            color_discrete_sequence=[styles['green500']]
        )

        # Style layout - larger title and taller figure
        fig.update_layout(
            title=dict(
                text=feature.capitalize(),
                font=dict(color=styles['white'], size=18),
                x=0.5,
                xanchor='center'
            ),
            plot_bgcolor=styles['grey600'],
            paper_bgcolor=styles['grey600'],
            font_color=styles['grey100'],
            xaxis=dict(
                showgrid=False,
                title="",
                range=[0, 1],
                gridcolor=styles['grey500']
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=styles['grey500'],
                title=""
            ),
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=False,
            height=320  # increased height for bigger appearance
        )

        # Add to list (grid cell; minWidth allows responsive wrapping)
        graphs.append(
            html.Div(
                style={'minWidth': '260px', 'width': '100%'},
                children=[
                    dcc.Graph(
                        figure=fig,
                        config={"displayModeBar": False},
                        style={'height': '320px', 'backgroundColor': styles["grey600"]}
                    )
                ]
            )
        )

    # Return container grid with 3 columns (results in 2 rows × 3 cols for 6 items on wide screens)
    return html.Div(
        style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(3, 1fr)',  # three equal columns
            'gap': '16px',
            'maxWidth': '1000px',
            'margin': '0 auto',
            'paddingTop': '8px'
        },
        children=graphs
    )

def create_library_radar(df):
    """Creates static radar for the whole library."""
    features = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'valence']
    avg_values = df[features].mean().tolist()

    # Close the loop
    values = avg_values + [avg_values[0]]
    categories = features + [features[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Library Avg',
        line_color='#1DB954',  # Spotify Green
        fillcolor='rgba(29, 185, 84, 0.4)'
    ))

    return apply_radar_styling(fig, "Your Audio Signature")


def create_comparison_radar(df, song_name):
    """Creates comparison radar: Song (Green) vs Library (Grey)."""
    features = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'valence']

    # 1. Library Average
    avg_values = df[features].mean().tolist()
    avg_values += [avg_values[0]]

    # 2. Song Values
    # Handle song not found or multiple entries
    track_col = "master_metadata_track_name" if "master_metadata_track_name" in df.columns else "track_name"
    song_data = df[df[track_col] == song_name][features]

    if song_data.empty:
        song_values = [0] * len(features)
    else:
        song_values = song_data.mean().tolist()  # Mean in case of duplicates

    song_values += [song_values[0]]
    categories = features + [features[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=song_values,
        theta=categories,
        fill='toself',
        name=song_name,
        line_color='#1DB954',  # Spotify Green
        fillcolor='rgba(29, 185, 84, 0.6)'
    ))

    return apply_radar_styling(fig, f"{song_name}")


def apply_radar_styling(fig, title_text):
    """Apply dark theme for the radar and remove the Plotly figure title
    (use the surrounding html.H3 headings instead to avoid overlap)."""
    styles = _load_style_vars()
    fig.update_layout(
        paper_bgcolor=styles["grey600"],
        plot_bgcolor=styles["grey600"],
        polar=dict(
            bgcolor=styles["grey600"],
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                showticklabels=False,
                gridcolor=styles["grey500"]
            ),
            angularaxis=dict(
                tickfont=dict(color=styles["white"], size=12),
                gridcolor=styles["grey500"],
                rotation=90,
                direction='clockwise'
            )
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=20)  # smaller top margin since no figure title
    )
    return fig