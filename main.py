from dash import Dash
from layout.main_app_layout import app_layout
from callbacks.app.file_upload import register_upload_callbacks

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

# Main App Layout
app.layout = app_layout()

# Register callbacks
register_upload_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
