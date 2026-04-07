# def build_sql_prompt(user_query: str, table_name: str, schema: list):
#     schema_str = "\n".join(
#         [f"- {c['name']} ({c['type']})" for c in schema]
#     )

#     return [
#         {
#             "role": "system",
#             "content": (
#                 "You are a senior data engineer.\n"
#                 "Generate ONLY a valid SQLite SQL query.\n"
#                 "Do NOT explain.\n"
#                 "Do NOT use markdown.\n"
#                 "Do NOT hallucinate columns.\n"
#             )
#         },
#         {
#             "role": "user",
#             "content": (
#                 f"Table name: {table_name}\n\n"
#                 f"Schema:\n{schema_str}\n\n"
#                 f"Task:\n{user_query}"
#             )
#         }
#     ]

def build_sql_prompt(
    user_query: str,
    schema_map: dict[str, list],
    preferred_table: str | None = None,
):
    schema_blocks = []
    for table_name, columns in schema_map.items():
        col_str = ", ".join([f"{c['name']} ({c['type']})" for c in columns]) or "No columns"
        schema_blocks.append(f"- {table_name}: {col_str}")
    schema_str = "\n".join(schema_blocks)

    preferred_table_instruction = (
        f"Preferred table: {preferred_table}\n\n"
        if preferred_table
        else ""
    )

    return [
        {
            "role": "system",
            "content": (
                "You are a senior data engineer using SQLite.\n\n"
                "Rules:\n"
                "- Output ONLY executable SQLite SQL\n"
                "- Use only the tables and columns provided\n"
                "- You MAY use SELECT, UPDATE, DELETE, INSERT, CREATE TABLE, ALTER TABLE\n"
                "- Multiple SQL statements are allowed\n"
                "- If aggregation is asked, include clear aliases in output columns\n"
                "- NEVER explain\n"
                "- NEVER use markdown\n"
                "- NEVER hallucinate columns or tables\n"
            )
        },
        {
            "role": "user",
            "content": (
                f"{preferred_table_instruction}"
                f"Available schema:\n{schema_str}\n\n"
                f"Task:\n{user_query}"
            )
        }
    ]
