import dash
from layout.listening_journey_layout import listening_journey_layout
from .sections.introduction import introduction_section
from .sections.listening_pattern import listening_pattern_section
from .sections.genre_dist import genre_dist_section
from .sections.artist_trend import artist_trend_section
from .sections.song_trend import song_trend_section
from .sections.energy_profile import energy_profile_section

dash.register_page(__name__, path="/listening-journey", name="Your Listening Journey")

layout = listening_journey_layout(
    [
        introduction_section(),
        listening_pattern_section(),
        genre_dist_section(),
        artist_trend_section(),
        song_trend_section(),
        energy_profile_section()
    ]
)
