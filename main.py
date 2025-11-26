from dash import Dash
from layout.main_app_layout import app_layout
from callbacks.app.file_upload import register_upload_callbacks
from utils.auth import spotify_client_connection
from utils.database import db_has_data, load_from_db
from app.store import set_uploaded_data
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()

# -------------------------------
# Connect to Spotify (safe)
# -------------------------------
try:
    spotify_client_connection()
except Exception as e:
    print(f"Spotify connection failed: {e}")

# -------------------------------
# Initialize Dash App
# -------------------------------
app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True
)

app.layout = app_layout()

# Register upload callbacks
register_upload_callbacks(app)

# -------------------------------
# Pre-load DB data (if exists)
# -------------------------------
print("Checking SQLite DB...")

try:
    if db_has_data():
        print("Loading data from SQLite DB...")
        df = load_from_db()
        set_uploaded_data(df)
        print(f"Loaded {len(df)} rows from DB")


    else:
        print("DB is empty, waiting for uploads.")
except Exception as e:
    print(f"DB load failed: {e}")

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    # Fix PyCharm reloader doubling
    app.run(debug=True, use_reloader=False)
