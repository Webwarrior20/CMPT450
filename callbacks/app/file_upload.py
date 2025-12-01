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

        if not contents or not filenames:
            print("Upload failed — contents or filenames missing.")
            raise dash.exceptions.PreventUpdate

        # Dash sends a single string for 1 file, list for multiple
        if not isinstance(contents, list):
            contents = [contents]
            filenames = [filenames]

        print(f"Files received: {filenames}")

        files = [{"name": n, "content": c} for n, c in zip(filenames, contents)]

        print("\nParsing uploaded file(s)…")
        df = parse_uploaded_files(files)

        if df is None or df.empty:
            print("Parsing produced no rows. Check file format or contents.")
            error_children = html.Div(
                className="upload-progress-container",
                children=[
                    html.Div(
                        "Upload failed: no valid data found in the provided files.",
                        className="upload-progress-text",
                    )
                ],
            )
            return error_children, dash.no_update

        print(f"Parsed {len(df)} rows")

        # Store in memory for this session
        set_uploaded_data(df)

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

        return progress_children, "/listening-journey"
