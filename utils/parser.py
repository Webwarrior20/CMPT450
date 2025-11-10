import io, base64, pandas as pd

def parse_uploaded_files(files):
    dfs = []
    for file in files:
        _, content = file["content"].split(",", 1)
        decoded = base64.b64decode(content)
        df = pd.read_csv(io.BytesIO(decoded)) if file["name"].endswith(".csv") else pd.DataFrame()
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
