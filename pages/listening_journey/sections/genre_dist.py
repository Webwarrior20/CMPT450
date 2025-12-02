from typing import List
from dash import html, dcc
from collections import Counter, defaultdict
import pandas as pd
import plotly.graph_objects as go
import ast

def genre_dist_section(df, df_filtered):
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
    return html.Div(
        className="section",
        children=[
            html.H2("Genre Distribution", className="heading-1"),
            html.Div(
                children=[
                    html.H3("Header - H2", className="heading-2"),
                    html.P(
                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                        className="body"
                    )
                ]
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        figure=sankey_genre_subgenre(
                            df_filtered,
                            title="Your Genre Breakdown"
                        ),
                        config={"displayModeBar": False},
                    )
                ]
            )
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
    title: str = "Songs → Main Genre → Subgenre Sankey"
) -> go.Figure:
    """
    Build a Sankey diagram mapping Songs -> Main Genre -> Subgenre.
    Includes single-word genres as mains (no subnodes) and places nodes
    with explicit `node.x` and `node.y` so right-most (subgenre)
    nodes get extra vertical spacing controlled by `right_spacing_factor`.

    New behavior: if a multi-word genre string appears only once across the
    dataset, treat that exact string as a main genre (no main->sub edge).
    """
    if df_linked is None or df_linked.empty or 'artist_genres' not in df_linked.columns:
        raise ValueError("No `artist_genres` column data available.")

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

    fig = go.Figure(go.Sankey(
        arrangement="fixed",
        node=dict(
            pad=15,
            thickness=20,
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

    fig.update_layout(title_text=title, font_size=10)
    return fig