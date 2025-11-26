import io
import json
import base64
import zipfile
import pandas as pd

# ================================================================
# Canonical column map → unified schema
# ================================================================
CANONICAL_COLUMNS = {
    "ts": "ts",
    "endTime": "ts",

    "master_metadata_track_name": "track",
    "trackName": "track",
    "track_name": "track",
    "name": "track",

    "master_metadata_album_artist_name": "artist",
    "artistName": "artist",
    "artist": "artist",

    "master_metadata_album_album_name": "album",
    "albumName": "album",
    "album": "album",

    "spotify_track_uri": "track_uri",
    "track_uri": "track_uri",
    "spotify_episode_uri": "track_uri",

    "reason_start": "reason_start",
    "reason_end": "reason_end",

    "shuffle": "shuffle",
    "skipped": "skipped",
    "offline": "offline",

    "ms_played": "ms_played",
    "msPlayed": "ms_played",
    "duration_ms": "ms_played",
    "seconds_played": "seconds_played",
}


# ================================================================
# Normalize DF
# ================================================================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    rename_map = {
        col: CANONICAL_COLUMNS[col]
        for col in df.columns if col in CANONICAL_COLUMNS
    }
    df = df.rename(columns=rename_map)

    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")

    if "seconds_played" in df.columns and "ms_played" not in df.columns:
        df["ms_played"] = df["seconds_played"] * 1000

    if "ms_played" in df.columns:
        df["minutes"] = df["ms_played"] / 60000.0

    return df


# ================================================================
# JSON parser
# ================================================================
def read_json_string(decoded: bytes) -> pd.DataFrame:
    text = decoded.decode("utf-8", errors="ignore")

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            data = [data]
    except Exception:
        # NDJSON fallback
        data = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except Exception:
                pass

    return normalize_columns(pd.DataFrame(data))


# ================================================================
# CSV parser
# ================================================================
def parse_csv_bytes(decoded: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(decoded))
    return normalize_columns(df)


# ================================================================
# ZIP parser
# ================================================================
def parse_zip_bytes(decoded: bytes) -> pd.DataFrame:
    dfs = []
    with zipfile.ZipFile(io.BytesIO(decoded)) as z:
        for name in z.namelist():
            try:
                if name.lower().endswith(".csv"):
                    dfs.append(parse_csv_bytes(z.read(name)))
                elif name.lower().endswith(".json"):
                    dfs.append(read_json_string(z.read(name)))
            except Exception:
                pass

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


# ================================================================
# Main upload handler
# ================================================================
def parse_uploaded_files(files):
    dfs = []

    for file in files:
        print(f"Processing File: {file['name']}")

        try:
            _, encoded = file["content"].split(",", 1)
            decoded = base64.b64decode(encoded)
        except Exception as e:
            print(f"Failed to decode {file['name']}: {e}")
            continue

        name = file["name"].lower()

        try:
            if name.endswith(".csv"):
                df = parse_csv_bytes(decoded)
            elif name.endswith(".json"):
                df = read_json_string(decoded)
            elif name.endswith(".zip"):
                df = parse_zip_bytes(decoded)
            else:
                print(f"Unsupported file: {file['name']}")
                continue

            print(f"Loaded: {df.shape}")
            dfs.append(df)

        except Exception as e:
            print(f"Failed parsing {file['name']}: {e}")

    final = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    print(f"TOTAL ROWS PARSED: {len(final)}")

    return final
