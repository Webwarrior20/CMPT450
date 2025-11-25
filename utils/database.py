from sqlalchemy import create_engine, text, inspect
import pandas as pd

DB_PATH = "data/spotify.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False}
)

# ------------------------------------------------------
#   Get Table Columns
# ------------------------------------------------------
def get_table_columns(table="streams"):
    try:
        inspector = inspect(engine)
        return [col["name"] for col in inspector.get_columns(table)]
    except Exception:
        return []

# ------------------------------------------------------
#   Save DF → DB
# ------------------------------------------------------
def save_df_to_db(df: pd.DataFrame, table="streams"):
    inspector = inspect(engine)

    try:
        db_columns = {col["name"] for col in inspector.get_columns(table)}
    except Exception:
        print(f"Table '{table}' not found in DB.")
        return

    if not db_columns:
        print(f"Table '{table}' has no columns. Check DB schema.")
        return

    df_to_save = df.copy()
    df_to_save = df_to_save[[c for c in df_to_save.columns if c in db_columns]]

    if "track_uri" in df_to_save.columns:
        df_to_save = df_to_save.drop_duplicates(subset=["track_uri"], keep="last")

    try:
        df_to_save.to_sql(table, engine, if_exists="append", index=False)
        print(f"Saved {len(df_to_save)} rows into '{table}'")
    except Exception as e:
        print(f"DB insert failed: {e}")

# ------------------------------------------------------
#   STREAMED LOADING (for large DB)
# ------------------------------------------------------
def load_from_db(table="streams", chunksize=50000):
    print(f"Loading DB table '{table}' in chunks (chunk={chunksize})...")

    dfs = []

    try:
        with engine.connect() as conn:
            for chunk in pd.read_sql(
                text(f"SELECT * FROM {table}"),
                conn,
                chunksize=chunksize
            ):
                if "ts" in chunk.columns:
                    chunk["ts"] = pd.to_datetime(chunk["ts"], errors="coerce")

                dfs.append(chunk)

        if not dfs:
            return pd.DataFrame()

        final = pd.concat(dfs, ignore_index=True)
        print(f"Loaded {len(final)} rows total")
        return final

    except Exception as e:
        print(f"DB load failed: {e}")
        return pd.DataFrame()

# ------------------------------------------------------
#   Check if DB contains rows
# ------------------------------------------------------
def db_has_data(table="streams") -> bool:
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            return count > 0
    except Exception as e:
        print(f"db_has_data failed for table '{table}': {e}")
        return False
