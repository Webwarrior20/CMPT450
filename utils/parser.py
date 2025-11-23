import io
import json
import base64
import zipfile
import pandas as pd


# ================================================================
# Canonical column map (any mapping → standardized schema)
# ================================================================
CANONICAL_COLUMNS = {
    # timestamps
    "ts": "ts",
    "endTime": "ts",

    # track title
    "master_metadata_track_name": "track",
    "trackName": "track",
    "track_name": "track",
    "name": "track",

    # artist
    "master_metadata_album_artist_name": "artist",
    "artistName": "artist",
    "artist": "artist",

    # album
    "master_metadata_album_album_name": "album",
    "albumName": "album",
    "album": "album",

    # track ID
    "spotify_track_uri": "track_uri",
    "track_uri": "track_uri",
    "spotify_episode_uri": "track_uri",

    # play reasons
    "reason_start": "reason_start",
    "reason_end": "reason_end",

    # playback info
    "shuffle": "shuffle",
    "skipped": "skipped",
    "offline": "offline",

    # duration
    "ms_played": "ms_played",
    "msPlayed": "ms_played",
    "duration_ms": "ms_played",
    "seconds_played": "seconds_played",
}


# ================================================================
# Helpers
# ================================================================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names & compute derived fields."""
    rename_map = {col: CANONICAL_COLUMNS[col] for col in df.columns if col in CANONICAL_COLUMNS}
    df = df.rename(columns=rename_map)

    # Convert to datetime
    if "ts" in df.columns:
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")

    # Convert duration fields
    if "seconds_played" in df.columns and "ms_played" not in df.columns:
        df["ms_played"] = df["seconds_played"] * 1000

    if "ms_played" in df.columns:
        df["minutes"] = df["ms_played"] / 60000

    return df


# ================================================================
# File Readers
# ================================================================
def read_json_string(decoded: bytes) -> pd.DataFrame:
    """Parses both list-style JSON and line-delimited JSON."""
    text = decoded.decode("utf-8")

    try:
        data = json.loads(text)
        if isinstance(data, dict):  # single entry
            data = [data]
    except json.JSONDecodeError:
        # Try NDJSON
        data = []
        for line in text.splitlines():
            try:
                data.append(json.loads(line))
            except:
                pass

    return normalize_columns(pd.DataFrame(data))


def parse_csv_bytes(decoded: bytes) -> pd.DataFrame:
    return normalize_columns(pd.read_csv(io.BytesIO(decoded)))


def parse_zip_bytes(decoded: bytes) -> pd.DataFrame:
    """Extract folder of streaming files."""
    dfs = []
    with zipfile.ZipFile(io.BytesIO(decoded)) as z:
        for name in z.namelist():
            lower = name.lower()
            if lower.endswith(".csv"):
                dfs.append(parse_csv_bytes(z.read(name)))
            elif lower.endswith(".json"):
                dfs.append(read_json_string(z.read(name)))

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


# ================================================================
# Main Function (called by Dash)
# ================================================================
def parse_uploaded_files(files):
    dfs = []

    for file in files:
        print(f"\n📂 Processing File: {file['name']}")

        try:
            _, encoded = file["content"].split(",", 1)
            decoded = base64.b64decode(encoded)
        except Exception as e:
            print(f"❌ Failed to decode {file['name']}: {e}")
            continue

        name = file["name"].lower()

        if name.endswith(".csv"):
            df = parse_csv_bytes(decoded)
        elif name.endswith(".json"):
            df = read_json_string(decoded)
        elif name.endswith(".zip"):
            df = parse_zip_bytes(decoded)
        else:
            print(f"⚠ Unsupported file: {file['name']}")
            continue

        print(f"   → Loaded: {df.shape}")
        dfs.append(df)

    final = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    print(f"\n📊 TOTAL ROWS PARSED: {len(final)}\n")

    return final
