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





import re

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

CREATE_TABLE_PATTERN = re.compile(
    r"(?i)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<name>(?:\"[^\"]+\"|`[^`]+`|\[[^\]]+\]|\w+))"
)


def normalize_create_table_statements(sql: str) -> str:
    """Add DROP TABLE IF EXISTS before CREATE TABLE statements."""
    def replacement(match):
        name = match.group("name")
        return f"DROP TABLE IF EXISTS {name};\n{match.group(0)}"

    return CREATE_TABLE_PATTERN.sub(replacement, sql)

def clean_sql(sql: str) -> str:
    lines = sql.strip().splitlines()
    lines = [l for l in lines if not l.strip().startswith("```")]
    return "\n".join(lines).strip()

SQL_IDENTIFIER_PATTERN = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
SQL_NORMALIZE_PATTERN = re.compile(r"[^A-Za-z0-9_]+")

def normalize_sql_identifier(name: str) -> str:
    return SQL_NORMALIZE_PATTERN.sub("_", name).strip("_").lower()

def build_identifier_map(schema_map: dict[str, list]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for table_name, columns in schema_map.items():
        normalized_table = normalize_sql_identifier(table_name)
        if normalized_table and normalized_table != table_name.lower():
            mapping[normalized_table] = table_name

        for column in columns:
            column_name = column.get("name", "")
            normalized_column = normalize_sql_identifier(column_name)
            if normalized_column and normalized_column != column_name.lower():
                mapping[normalized_column] = column_name

    return mapping

def normalize_ai_identifiers(sql: str, schema_map: dict[str, list]) -> str:
    identifier_map = build_identifier_map(schema_map)
    if not identifier_map:
        return sql

    def replace_token(match: re.Match) -> str:
        token = match.group(0)
        normalized_token = token.lower()
        replacement = identifier_map.get(normalized_token)
        return f'"{replacement}"' if replacement else token

    return SQL_IDENTIFIER_PATTERN.sub(replace_token, sql)

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
    sql = normalize_ai_identifiers(sql, schema_map)
    sql = normalize_create_table_statements(sql)

    if not is_safe_sql(sql):
        raise ValueError("Unsafe SQL detected")

    return sql
