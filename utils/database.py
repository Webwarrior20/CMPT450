from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

DB_PATH = "data/spotify.db"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False}
)


def db_connected():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Connected to database successfully")
        return True
    except SQLAlchemyError as e:
        print(f"Database connection failed: {e}")
        return False


def load_table(table):
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(f'SELECT * FROM "{table}"'), conn)
        print(f"Loaded {len(df)} rows from table '{table}'")
        return df
    except SQLAlchemyError as e:
        print(f"Failed to load table '{table}': {e}")
        return pd.DataFrame()

def table_has_rows(table: str) -> bool:
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f'SELECT 1 FROM "{table}" LIMIT 1'))
            return result.fetchone() is not None
    except SQLAlchemyError:
        return False