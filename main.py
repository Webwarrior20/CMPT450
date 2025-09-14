import dash
from dash import html

# Initialize app
app = dash.Dash(__name__)

# Layout with only heading
app.layout = html.Div([
    html.H1("Fashion Collect", style={"textAlign": "center", "color": "#333"})
])

# Run app
if __name__ == "__main__":
    app.run(debug=True)
