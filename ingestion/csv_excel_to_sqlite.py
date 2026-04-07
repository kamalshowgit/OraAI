from sqlalchemy import create_engine
import pandas as pd
from ingestion.db_config import DB_PATH

def dataframe_to_sqlite(
    df: pd.DataFrame,
    table_name: str
):
    # Ensure database directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    engine = create_engine(f"sqlite:///{DB_PATH}")

    df.to_sql(
        table_name,
        engine,
        if_exists="replace",   # safe because table_name is unique
        index=False
    )

    return {
        "database_path": str(DB_PATH),
        "table_name": table_name,
        "rows": len(df),
        "columns": list(df.columns)
    }
