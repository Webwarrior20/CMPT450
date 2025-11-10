from dash import html

def build_card(title, value, color):
    return html.Div(
        style={
            "backgroundColor": color,
            "borderRadius": "10px",
            "padding": "20px",
            "color": "#FFF",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.25)",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "minHeight": "120px",
            "transition": "transform 0.2s ease, box-shadow 0.2s ease",
        },
        children=[
            html.H4(title, style={"marginBottom": "8px", "fontSize": "15px", "opacity": "0.9"}),
            html.H2(value, style={"margin": "0", "fontSize": "26px", "fontWeight": "bold"}),
        ],
    )
