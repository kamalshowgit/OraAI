# from sqlalchemy import create_engine, text
# from ingestion.db_config import DB_PATH

# def execute_sql(query: str):
#     engine = create_engine(f"sqlite:///{DB_PATH}")

#     with engine.connect() as conn:
#         result = conn.execute(text(query))
#         rows = result.fetchall()
#         columns = result.keys()

#     return {
#         "columns": columns,
#         "rows": rows
#     }


# from sqlalchemy import create_engine, text
# from ingestion.db_config import DB_PATH

# def execute_sql(sql: str):
#     engine = create_engine(f"sqlite:///{DB_PATH}")

#     statements = [
#         stmt.strip()
#         for stmt in sql.split(";")
#         if stmt.strip()
#     ]

#     rows = None
#     columns = None

#     with engine.begin() as conn:
#         for stmt in statements:
#             result = conn.execute(text(stmt))
#             if result.returns_rows:
#                 rows = result.fetchall()
#                 columns = result.keys()

#     return {
#         "columns": columns,
#         "rows": rows
#     }



from sqlalchemy import create_engine, text
from ingestion.db_config import DB_PATH

def execute_sql(sql: str):
    engine = create_engine(f"sqlite:///{DB_PATH}")

    statements = [
        stmt.strip()
        for stmt in sql.split(";")
        if stmt.strip()
    ]

    rows = None
    columns = None

    with engine.begin() as conn:
        for stmt in statements:
            result = conn.execute(text(stmt))

            if result.returns_rows:
                columns = list(result.keys())
                rows = [list(row) for row in result.fetchall()]

    return {
        "columns": columns,
        "rows": rows
    }