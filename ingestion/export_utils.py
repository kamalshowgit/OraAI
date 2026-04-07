
import pandas as pd
from sqlalchemy import create_engine
from ingestion.db_config import DB_PATH, DATA_ROOT
from pathlib import Path

def export_table(table_name: str, format: str = "csv") -> Path:
    engine = create_engine(f"sqlite:///{DB_PATH}")
    quoted_table_name = '"' + table_name.replace('"', '""') + '"'
    df = pd.read_sql(f"SELECT * FROM {quoted_table_name}", engine)

    out = DATA_ROOT / "exports"
    out.mkdir(parents=True, exist_ok=True)

    if format.lower() == "xlsx":
        path = out / f"{table_name}_updated.xlsx"
        df.to_excel(path, index=False)
    else:
        path = out / f"{table_name}_updated.csv"
        df.to_csv(path, index=False)

    return path
