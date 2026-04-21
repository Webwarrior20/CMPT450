from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

DB_PATH = "data/spotify.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False}
)


# -----------------------------
# CHECK CONNECTION
# -----------------------------
def db_connected():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connected to database successfully")
        return True
    except SQLAlchemyError as e:
        print(f"Database connection failed: {e}")
        return False


# -----------------------------
# SAFE LOAD (LIMITED DATA ONLY)
# -----------------------------
def load_recent_data(months=6):
    """
    Load a safe subset of data (NO ts dependency)
    """
    try:
        with engine.connect() as conn:
            df = pd.read_sql(
                text('SELECT * FROM extracted LIMIT 50000'),
                conn
            )

        print(f"Loaded {len(df)} rows (safe subset)")
        return df

    except Exception as e:
        print(f"DB error: {e}")
        return pd.DataFrame()


# -----------------------------
# FALLBACK FUNCTION (IMPORTANT)
# -----------------------------
def load_table(table):
    print("⚠️ load_table fallback → loading limited data")

    try:
        with engine.connect() as conn:
            df = pd.read_sql(
                text(f'SELECT * FROM "{table}" LIMIT 50000'),
                conn
            )

        print(f"Loaded {len(df)} rows (limited fallback)")
        return df

    except Exception as e:
        print(f"Fallback load failed: {e}")
        return pd.DataFrame()


# -----------------------------
# CHECK IF TABLE HAS DATA
# -----------------------------
def table_has_rows(table: str) -> bool:
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f'SELECT 1 FROM "{table}" LIMIT 1'))
            return result.fetchone() is not None
    except SQLAlchemyError:
        return False