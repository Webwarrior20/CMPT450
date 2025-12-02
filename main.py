from dash import Dash
from layout.main_app_layout import app_layout
from callbacks.app.file_upload import register_upload_callbacks
from utils.auth import spotify_client_connection
from utils.database import db_connected, load_table, table_has_rows
from app.store import set_main_database
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
spotify_client_connection()

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True
)

app.layout = app_layout()

# Register upload callbacks
register_upload_callbacks(app)

try:
    if db_connected():
        if table_has_rows("extracted"):

            df = load_table("extracted")
            set_main_database(df)
        else:
            print("Database connected but table 'extracted' is empty")
    else:
        print("Database connection failed")

except Exception as e:
    print(f"DB load failed: {e}")

# Run App
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
