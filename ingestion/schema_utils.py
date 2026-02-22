from sqlalchemy import create_engine, inspect
from ingestion.db_config import DB_PATH

def get_table_schema(table_name: str):
    engine = create_engine(f"sqlite:///{DB_PATH}")
    inspector = inspect(engine)

    return [
        {
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": col["nullable"]
        }
        for col in inspector.get_columns(table_name)
    ]


def list_all_tables():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    inspector = inspect(engine)
    return inspector.get_table_names()
