from dash import html, dcc
from utils.stats import get_first_listen_date, get_total_listening_time

"""
Build the introduction section. Accepts a pandas dataframe as input.
"""
def introduction_section(df):
    if df is None or df.empty:
        return html.Div(
            className="section",
            children=[
                html.H2("Introduction - Error", className="heading-1"),
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

    first_listen_date = get_first_listen_date(df)
    total_time = get_total_listening_time(df)
    return html.Div(
        className="section",
        children=[
            html.H2("Introduction", className="heading-1"),
            html.Div(
                children=[
                    html.P(
                        """
                        Welcome to your Listening Journey! This section provides an in-depth analysis of your music 
                        listening habits based on the data you've uploaded from Spotify. Explore various aspects of your 
                        listening patterns, including genre preferences, artist trends, song popularity, and energy profiles. 
                        Dive in to discover insights about your musical tastes and how they have evolved over time.
                        """,
                        className="body"
                    )
                ]
            ),

            # First listen date
            html.Div(
                children=[
                    html.H3(
                        ["You first hit play on ", html.Span(first_listen_date, className="emphasis")],
                        className="heading-2",
                    )
                ]
            ),

            # Total listening time
            html.Div(
                children=[
                    html.H3(
                        ["Your total listening time on Spotify is ", html.Span(total_time, className="emphasis")],
                        className="heading-2",
                    )
                ]
            )

        ]
    )
