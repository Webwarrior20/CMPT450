from dash import Input, Output, State
from utils.parser import parse_uploaded_files
from app.store import set_uploaded_data

def register_upload_callbacks(app):
    @app.callback(
        Output("redirect", "pathname"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        prevent_initial_call=True,
    )
    def handle_upload(contents, filenames):
        if contents and filenames:
            files = [{"name": n, "content": c} for n, c in zip(filenames, contents)]
            uploaded = parse_uploaded_files(files)
            set_uploaded_data(uploaded)
            return "/listening-journey"
        raise Exception("No file uploaded.")
