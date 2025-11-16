from dash import Input, Output, State, html
from utils.parser import parse_uploaded_files
from app.store import set_uploaded_data
import dash


def register_upload_callbacks(app):
    @app.callback(
        Output("upload-progress", "children"),   # progress bar + text
        Output("redirect", "pathname"),          # still auto-redirect
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True,
    )
    def handle_upload(contents, filenames):
        print("📥 Upload callback triggered")

        if not contents or not filenames:
            print("❌ Upload failed: no contents or filenames.")
            raise dash.exceptions.PreventUpdate

        # Ensure lists for multi-upload
        if not isinstance(contents, list):
            contents = [contents]
            filenames = [filenames]

        print(f"📂 Files received: {len(filenames)}")
        print(f"📝 Filenames: {filenames}")

        files = [{"name": n, "content": c} for n, c in zip(filenames, contents)]

        # ---- parsing step ----
        print("⚙️  Parsing uploaded files...")
        df = parse_uploaded_files(files)
        print(f"✅ Parsing complete. DataFrame shape: {df.shape}")
        print(f"🔎 Columns: {list(df.columns)}\n")

        set_uploaded_data(df)

        # UI: show a 100% progress bar + text
        progress_children = html.Div(
            className="upload-progress-container",
            children=[
                html.Div(
                    className="upload-progress-track",
                    children=html.Div(className="upload-progress-bar"),
                ),
                html.Div(
                    "Upload & processing complete. Redirecting to dashboard…",
                    className="upload-progress-text",
                ),
            ],
        )

        # redirect to Listening Journey (or Overview if you prefer)
        return progress_children, "/listening-journey"
