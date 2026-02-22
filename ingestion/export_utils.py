
import pandas as pd
from sqlalchemy import create_engine
from ingestion.db_config import DB_PATH
from pathlib import Path

def export_table(table_name: str) -> Path:
    engine = create_engine(f"sqlite:///{DB_PATH}")
    df = pd.read_sql(f"SELECT * FROM {table_name}", engine)

    out = Path("exports")
    out.mkdir(exist_ok=True)

    path = out / f"{table_name}_updated.csv"
    df.to_csv(path, index=False)

    return path
