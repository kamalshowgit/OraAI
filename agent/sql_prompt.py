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

def build_sql_prompt(user_query: str, table_name: str, schema: list):
    schema_str = "\n".join(
        [f"- {c['name']} ({c['type']})" for c in schema]
    )

    return [
        {
            "role": "system",
            "content": (
                "You are a senior data engineer using SQLite.\n\n"
                "Rules:\n"
                "- Output ONLY executable SQLite SQL\n"
                "- You MAY use SELECT, UPDATE, DELETE, INSERT, ALTER TABLE\n"
                "- You MAY modify the table in-place\n"
                "- Multiple SQL statements are allowed\n"
                "- NEVER explain\n"
                "- NEVER use markdown\n"
                "- NEVER hallucinate columns\n"
            )
        },
        {
            "role": "user",
            "content": (
                f"Table name: {table_name}\n\n"
                f"Schema:\n{schema_str}\n\n"
                f"Task:\n{user_query}"
            )
        }
    ]
