from typing import List
from dash import html, dcc
from collections import Counter, defaultdict
from app.store import get_uploaded_data
from utils.css_vars import load_css_variables
import pandas as pd
import plotly.graph_objects as go
import ast

def genre_dist_section(df, db):
    if df is None or df.empty:
        return html.Div(
            className="section",
            children=[
                html.H2("Genre Distribution - Error", className="heading-1"),
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
    # Merge with metadata to get genres
    lh = get_uploaded_data()
    merged_df = lh.merge(
        db,
        left_on="spotify_track_uri",
        right_on="track_uri",
        how="left"
    )

    return html.Div(
        className="section",
        children=[
            html.H2("Genre Distribution", className="heading-1"),
            html.Div(
                children=[
                    html.P(
                        " Genres play a significant role in shaping our musical preferences and listening habits. "
                        "In this section, we explore the distribution of genres in your listening history, "
                        "providing insights into your favorite styles of music and how they contribute to your overall "
                        "musical taste. Discover the variety and depth of genres that define your unique listening journey",

                        className="body"
                    )
                ]
            ),
            # Genre Breakdown Sankey
            html.Div(
                children=[
                    html.H3(
                        "Breaking Down Your Genres",
                        className="heading-3"
                    )
                ]
            ),

            html.Div(
                children=[
                    dcc.Graph(
                        figure=sankey_genre_subgenre(
                            merged_df,
                        ),
                        config={"displayModeBar": False},
                    )
                ]
            ),

            html.Div(
                children=[
                    html.P(
                        " You have listened to a diverse range of genres over your Spotify journey. "
                        "The Sankey diagram above illustrates the relationship between the main genres and their subgenres "
                        "based on your listening history. The left side represents the main genres, while the right side "
                        "displays the subgenres associated with each main genre. The width of the connections "
                        "indicates the volume of songs you've listened to within each genre pairing. This visualization "
                        "provides a clear overview of your genre preferences and how they interconnect, "
                        "highlighting the richness of your musical taste.",

                        className="body"
                    )
                ]
            ),

            # Heading for Top Genres Treemap
            html.Div(
                children=[
                    html.H3(
                        "Your Top Genres",
                        className="heading-3"
                    )
                ]
            ),

            html.Div(
                children=[
                    dcc.Graph(
                        figure=genre_treemap(
                            merged_df,
                        ),
                        config={"displayModeBar": False},
                    )
                ]
            ),

            html.Div(
                children=[
                    html.P(
                        " The treemap above showcases your top genres based on the number of songs you've listened to in each genre. "
                        "Each rectangle represents a genre, with the size of the rectangle corresponding to the volume of songs "
                        "you've enjoyed within that genre. Larger rectangles indicate genres that dominate your listening habits, "
                        "while smaller rectangles represent less frequently played genres. This visualization provides a quick and "
                        "intuitive overview of your genre preferences, allowing you to see at a glance which styles of music resonate most with you.",
                        className="body"
                    )
                ]
            ),
        ]
    )

def _parse_genres_cell(val) -> List[str]:
    """Return a list of genre strings for one cell (robust to lists or comma-delimited)."""
    if val is None:
        return []
    if isinstance(val, (list, tuple)):
        return [str(x).strip() for x in val if x and str(x).strip()]
    if not isinstance(val, str):
        val = str(val)
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, (list, tuple)):
            return [str(x).strip() for x in parsed if x and str(x).strip()]
        if isinstance(parsed, str):
            # fall though to comma split
            pass
    except (ValueError, SyntaxError):
        pass
    # fallback: comma-delimited string
    return [g.strip() for g in val.split(",") if g.strip()]


def sankey_genre_subgenre(
    df_linked: pd.DataFrame,
    top_n_main: int = 8,
    top_m_sub_per_main: int = 10,
    right_spacing_factor: float = 1.5,
) -> go.Figure:
    """
    Build a Sankey diagram mapping Songs -> Main Genre -> Subgenre.
    Includes single-word genres as mains (no subnodes) and places nodes
    with explicit `node.x` and `node.y` so right-most (subgenre)
    nodes get extra vertical spacing controlled by `right_spacing_factor`.
    """
    if df_linked is None or df_linked.empty or 'artist_genres' not in df_linked.columns:
        raise ValueError("No `artist_genres` column data available.")

    css = load_css_variables("assets/styles/variables.css")
    green500 = css.get("--color-green-500", "#1ED760")


    # First pass: count exact (normalized) genre-string occurrences across rows
    genre_string_counts = Counter()
    for val in df_linked['artist_genres'].dropna():
        for item in _parse_genres_cell(val):
            s = str(item).strip()
            if s:
                genre_string_counts[s.title()] += 1

    main_song_sets = defaultdict(set)
    edge_counts = Counter()
    # gather per-row unique main/sub pairs, include single-word mains
    for idx, val in df_linked['artist_genres'].dropna().items():
        items = _parse_genres_cell(val)
        seen_mains = set()
        seen_pairs = set()
        for item in items:
            s = str(item).strip()
            if not s:
                continue
            canon = s.title()
            parts = s.split()
            # If multi-word but appears only once, treat the full string as a main (no sub)
            if len(parts) >= 2 and genre_string_counts.get(canon, 0) == 1:
                main = canon
                seen_mains.add(main)
            elif len(parts) >= 2:
                main = parts[-1].title()
                sub = canon
                seen_mains.add(main)
                if (main, sub) not in seen_pairs:
                    edge_counts[(main, sub)] += 1
                    seen_pairs.add((main, sub))
            else:
                # single-word genre -> treat as main with no subs
                main = canon
                seen_mains.add(main)
        for m in seen_mains:
            main_song_sets[m].add(idx)

    if not main_song_sets:
        raise ValueError("No main genres extracted from the data.")

    main_song_counts = {m: len(idxs) for m, idxs in main_song_sets.items()}
    top_mains = [m for m, _ in Counter(main_song_counts).most_common(top_n_main)]
    if not top_mains:
        raise ValueError("No top mains selected.")

    # build nodes: Songs -> mains -> subs
    nodes = []
    node_index = {}
    node_index['Songs'] = len(nodes); nodes.append('Songs')
    for m in top_mains:
        node_index[m] = len(nodes); nodes.append(m)

    # add subs for chosen mains (limit per-main) and maintain related order
    subs_per_main = {}
    for m in top_mains:
        related = [(s, c) for (mm, s), c in edge_counts.items() if mm == m]
        related.sort(key=lambda x: -x[1])
        chosen = [s for s, _ in related[:top_m_sub_per_main]]
        subs_per_main[m] = chosen
        for s in chosen:
            if s not in node_index:
                node_index[s] = len(nodes)
                nodes.append(s)

    # build links
    sources, targets, values = [], [], []
    for m in top_mains:
        sources.append(node_index['Songs'])
        targets.append(node_index[m])
        values.append(main_song_counts.get(m, 0))

    for (m, s), c in edge_counts.items():
        if m not in top_mains:
            continue
        if s not in node_index:
            continue
        sources.append(node_index[m])
        targets.append(node_index[s])
        values.append(c)

    if not values:
        raise ValueError("No links remain after processing filters.")

    # compute explicit node positions (normalized 0..1)
    start_y = 0.04
    end_y = 0.96
    span = end_y - start_y

    # X positions: left / middle / right
    x_songs = 0.02
    x_mains = 0.45
    x_subs = 0.95

    # prepare y positions for subs with extra spacing per main
    # compute total slot count (subs + extra gaps)
    slot_count = 0
    per_main_slots = {}
    for m in top_mains:
        n = len(subs_per_main.get(m, []))
        extra = int(n * (right_spacing_factor - 1)) if n > 0 else 0
        per_main_slots[m] = (n, extra)
        slot_count += n + extra

    # if no subs, fall back to simple equal spacing
    if slot_count == 0:
        slot_count = max(1, len(top_mains))

    # assign subs slots sequentially so subs for same main are contiguous
    subs_y = {}
    current_slot = 0
    for m in top_mains:
        n, extra = per_main_slots.get(m, (0, 0))
        total_slots_for_main = n + extra
        for i, s in enumerate(subs_per_main.get(m, [])):
            # use 1..slot_count range for centers
            slot_pos = (current_slot + 1 + i) / (slot_count + 1)
            center = start_y + slot_pos * span
            subs_y[s] = center
        current_slot += total_slots_for_main

    # compute mains y: average of their subs if available, else by weighted distribution
    mains_y = {}
    # fallback distribution for mains without subs: proportional to their song counts
    mains_without_subs = [m for m in top_mains if len(subs_per_main.get(m, [])) == 0]
    # compute weighted baseline positions for all mains
    total_main_count = sum(main_song_counts.get(m, 1) for m in top_mains) or len(top_mains)
    cumulative = 0.0
    for m in top_mains:
        weight = main_song_counts.get(m, 1) / total_main_count
        center = start_y + (cumulative + weight / 2.0) * span
        mains_y[m] = center
        cumulative += weight
    # override with average of subs where subs exist
    for m in top_mains:
        subs = subs_per_main.get(m, [])
        if subs:
            mains_y[m] = sum(subs_y[s] for s in subs) / len(subs)

    # build final x and y lists in node order
    x_list = []
    y_list = []
    for label in nodes:
        if label == 'Songs':
            x_list.append(x_songs)
            y_list.append(0.5)
        elif label in top_mains:
            x_list.append(x_mains)
            y_list.append(max(start_y, min(end_y, mains_y[label])))
        else:
            # subs
            x_list.append(x_subs)
            y_list.append(max(start_y, min(end_y, subs_y.get(label, 0.5))))

        # color nodes (simple)
        color_palette = ["#4C78A8", "#F58518", "#E45756", "#72B7B2", "#54A24B", "#EECA3B", "#B279A2", "#9D755D"]
        node_colors = []
        for label in nodes:
            if label == 'Songs':
                node_colors.append("black")
            elif label in top_mains:
                node_colors.append(color_palette[top_mains.index(label) % len(color_palette)])
            else:
                node_colors.append("lightgrey")

        # increase pad/thickness and figure height for more vertical spacing
        node_pad = 26
        node_thickness = 26
        fig = go.Figure(go.Sankey(
            arrangement="fixed",
            node=dict(
                pad=node_pad,
                thickness=node_thickness,
                line=dict(color="black", width=0.5),
                label=nodes,
                color=node_colors,
                x=x_list,
                y=y_list
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values
            )
        ))

        # match section background and give more vertical room
        fig.update_layout(
            height=760,
            font_size=11,
            margin=dict(t=10, l=20, r=20, b=20),
            plot_bgcolor=green500,
            paper_bgcolor=green500,
        )
        return fig

def genre_treemap(
    df_linked: pd.DataFrame,
    top_n_genres: int = 12,
) -> go.Figure:
    """
    Build a treemap of the user's top genres by song count.
    Matches section background using CSS vars for visual consistency.
    """
    if df_linked is None or df_linked.empty or 'artist_genres' not in df_linked.columns:
        raise ValueError("No `artist_genres` column data available.")

    css = load_css_variables("assets/styles/variables.css")
    green500 = css.get("--color-green-500", "#1ED760")

    genre_counts = Counter()
    for val in df_linked['artist_genres'].dropna():
        for item in _parse_genres_cell(val):
            s = str(item).strip()
            if s:
                genre_counts[s.title()] += 1

    top_genres = genre_counts.most_common(top_n_genres)
    if not top_genres:
        raise ValueError("No genres extracted from the data.")

    labels = [g for g, _ in top_genres]
    values = [c for _, c in top_genres]

    fig = go.Figure(go.Treemap(
        labels=labels,
        values=values,
        parents=[""] * len(labels),
        textinfo="label+value",
        marker=dict(colorscale='Greens', showscale=False, line=dict(width=0)),
        root=dict(color='rgba(0,0,0,0)'),
    ))

    fig.update_traces(marker=dict(cornerradius=5))

    # make a treemap background match section
    fig.update_layout(
        height=480,
        margin=dict(t=1, l=10, r=10, b=10),
        plot_bgcolor=green500,
        paper_bgcolor=green500,
    )
    return fig