import dash
from app.store import get_main_database, get_uploaded_data
from utils.stats import get_uploaded_dataframe
from layout.listening_journey_layout import listening_journey_layout
from .sections.introduction import introduction_section
from .sections.listening_pattern import listening_pattern_section
from .sections.genre_dist import genre_dist_section
from .sections.artist_trend import artist_trend_section
from .sections.song_trend import song_trend_section
from .sections.energy_profile import energy_profile_section


dash.register_page(__name__, path="/listening-journey", name="Your Listening Journey")

"""
Build the page layout. Accept an optional DataFrame; if None, try to load the current uploaded data.
Returning a function as `layout` lets Dash evaluate the layout at render time (so fresh data is used).
"""
def create_listening_journey_layout():
    df = get_uploaded_dataframe()
    db = get_main_database()

    # Merge with metadata to get genres
    lh = get_uploaded_data()
    merged_df = lh.merge(
        db,
        left_on="spotify_track_uri",
        right_on="track_uri",
        how="left"
    )

    return listening_journey_layout(
        [
            introduction_section(df),
            listening_pattern_section(df),
            genre_dist_section(merged_df),
            artist_trend_section(df),
            song_trend_section(df),
            energy_profile_section(merged_df)
        ]
    )

layout = lambda: create_listening_journey_layout()