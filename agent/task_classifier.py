# def classify_task(user_query: str) -> str:
#     q = user_query.lower()

#     if any(word in q for word in ["insert", "add", "create"]):
#         return "CREATE"
#     if any(word in q for word in ["update", "modify", "change"]):
#         return "UPDATE"
#     if any(word in q for word in ["delete", "remove"]):
#         return "DELETE"

#     # default
#     return "EDA"
