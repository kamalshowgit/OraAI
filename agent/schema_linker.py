def schema_link(user_query: str, schema: list) -> str:
    """
    Annotates the user query with schema hints
    without removing semantic intent.
    """

    columns = [col["name"] for col in schema]

    annotation = (
        "\n\n"
        "Relevant columns (use if applicable): "
        + ", ".join(columns)
    )

    return user_query + annotation
