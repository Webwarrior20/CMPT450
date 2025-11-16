from dash import html
from components.sidebar import sidebar
from app.store import get_uploaded_data


def listening_journey_layout(children):
    """
    Layout for Listening Journey section with sidebar + toast notification.
    """
    uploaded_df = get_uploaded_data()

    # Show toast only if data exists
    show_toast = uploaded_df is not None and not uploaded_df.empty

    toast_component = (
        html.Div(
            "Upload successful — your data is ready!",
            className="toast"
        )
        if show_toast else None
    )

    return html.Div(
        className="listening-journey",
        children=[
            # 🌟 Toast Notification (only shown when upload succeeded)
            toast_component,

            # Sidebar Navigation
            sidebar("listening-journey"),

            # Main Content
            html.Main(
                className="listening-journey-content",
                children=children
            ),
        ],
    )
