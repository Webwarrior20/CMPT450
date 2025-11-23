from dash import Input, Output, State, html
from utils.parser import parse_uploaded_files
from app.store import set_uploaded_data
import dash

def register_upload_callbacks(app):
    @app.callback(
        Output("upload-progress", "children"),   # progress bar + status message
        Output("redirect", "pathname"),          # page redirect
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True,
    )
    def handle_upload(contents, filenames):
        print("\n================ UPLOAD EVENT ==================")
        print("📥 Upload callback triggered")

        if not contents or not filenames:
            print("❌ Upload failed — contents or filenames missing.")
            raise dash.exceptions.PreventUpdate

        # Handle single-file uploads (Dash sends a string instead of list)
        if not isinstance(contents, list):
            contents = [contents]
            filenames = [filenames]

        print(f"📂 Total files received: {len(filenames)}")
        for f in filenames:
            print(f"   • {f}")

        # Pair files with content
        files = [{"name": n, "content": c} for n, c in zip(filenames, contents)]

        print("\n⚙️ Parsing uploaded files…")
        df = parse_uploaded_files(files)

        print(f"✅ Parsing complete.")
        print(f"📊 Final DataFrame shape: {df.shape}")
        print(f"🔎 Columns detected: {list(df.columns)}")
        print("=================================================\n")

        # Save the parsed data
        set_uploaded_data(df)

        # ---- UI: Full progress bar animation ----
        progress_children = html.Div(
            className="upload-progress-container",
            children=[
                html.Div(
                    className="upload-progress-track",
                    children=html.Div(className="upload-progress-bar"),
                ),
                html.Div(
                    "Upload complete! Redirecting…",
                    className="upload-progress-text",
                ),
            ],
        )

        # Redirect user automatically
        return progress_children, "/listening-journey"
