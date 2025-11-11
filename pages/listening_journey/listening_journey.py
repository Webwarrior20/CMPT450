import dash
from layout.listening_journey_layout import listening_journey_layout
from .sections.introduction import introduction_section

dash.register_page(__name__, path="/listening-journey", name="Your Listening Journey")

layout = listening_journey_layout(
    [
        introduction_section(),
        introduction_section(),
        introduction_section()
    ]
)
