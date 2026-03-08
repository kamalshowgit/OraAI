# from agent.groq_client import call_groq
# from agent.sql_prompt import build_sql_prompt
# from agent.schema_linker import schema_link
# from ingestion.schema_utils import get_table_schema

# FORBIDDEN = ["DROP", "DELETE", "UPDATE", "INSERT", "INSERT", "ALTER"]

# def is_safe_sql(query: str) -> bool:
#     return not any(word in query.upper() for word in FORBIDDEN)


# def generate_sql(user_query: str, table_name: str) -> str:
#     schema = get_table_schema(table_name)

#     # 🔹 Annotate query (not rewrite)
#     enriched_query = schema_link(user_query, schema)

#     messages = build_sql_prompt(
#         enriched_query,
#         table_name,
#         schema
#     )

#     sql = call_groq(messages).strip()

#     if not sql.lower().startswith("select"):
#         raise ValueError("Only SELECT queries are allowed")

#     if not is_safe_sql(sql):
#         raise ValueError("Unsafe SQL detected")

#     return sql





from agent.groq_client import call_groq
from agent.sql_prompt import build_sql_prompt
from ingestion.schema_utils import get_table_schema, list_all_tables

BLOCKED_KEYWORDS = [
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "DROP DATABASE",
    "VACUUM"
]

def clean_sql(sql: str) -> str:
    lines = sql.strip().splitlines()
    lines = [l for l in lines if not l.strip().startswith("```")]
    return "\n".join(lines).strip()

def is_safe_sql(sql: str) -> bool:
    upper = sql.upper()
    return not any(bad in upper for bad in BLOCKED_KEYWORDS)

def build_schema_map() -> dict[str, list]:
    tables = list_all_tables()
    return {name: get_table_schema(name) for name in tables}

def generate_sql(user_query: str, table_name: str | None = None) -> str:
    schema_map = build_schema_map()

    messages = build_sql_prompt(
        user_query,
        schema_map,
        preferred_table=table_name,
    )

    raw_sql = call_groq(messages)
    sql = clean_sql(raw_sql)

    if not is_safe_sql(sql):
        raise ValueError("Unsafe SQL detected")

    return sql
