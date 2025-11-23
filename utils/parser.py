import io
import base64
import pandas as pd

# Expected columns for Spotify Extended Streaming History
EXPECTED_COLUMNS = [
    "ts",
    "ms_played",
    "master_metadata_track_name",
    "master_metadata_album_artist_name",
    "master_metadata_album_album_name",
    "spotify_track_uri",
    "reason_start",
    "reason_end",
    "shuffle",
    "skipped",
    "offline",
    "offline_timestamp",
    "seconds_played"
]

def parse_uploaded_files(files):
    dfs = []

    for file in files:
        print(f"\n==============================")
        print(f"Processing file: {file['name']}")

        # Decode file
        try:
            _, content = file["content"].split(",", 1)
            decoded = base64.b64decode(content)
        except Exception as e:
            print(f"❌ Error decoding file {file['name']}: {e}")
            continue

        # Load CSV
        if file["name"].lower().endswith(".csv"):
            try:
                df = pd.read_csv(io.BytesIO(decoded))
                print(f"  → Loaded CSV with shape: {df.shape}")
            except Exception as e:
                print(f"❌ Failed to read CSV: {e}")
                continue
        else:
            print(f"⚠ Skipping non-CSV file: {file['name']}")
            continue

        # Keep only the columns we expect
        available_cols = [c for c in df.columns if c in EXPECTED_COLUMNS]
        missing = set(EXPECTED_COLUMNS) - set(available_cols)

        print(f"  ✓ Columns loaded: {len(available_cols)}")
        if missing:
            print(f"  ⚠ Missing columns: {missing}")

        df = df[available_cols]

        # Normalize field names
        df.rename(columns={
            "master_metadata_track_name": "track",
            "master_metadata_album_artist_name": "artist",
            "master_metadata_album_album_name": "album"
        }, inplace=True)

        # Parse timestamps
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")

        # Calculate minutes played
        if "ms_played" in df.columns:
            df["minutes"] = df["ms_played"] / 60000

        dfs.append(df)

    # Combine all parsed files
    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)
        print(f"\n==============================")
        print(f"TOTAL ROWS LOADED ACROSS ALL FILES: {len(final_df)}")
        print(f"==============================\n")
        return final_df

    print("⚠ No valid files were parsed.")
    return pd.DataFrame()
