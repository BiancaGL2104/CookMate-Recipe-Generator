def build_query(ingredients=None, diet=None, cuisine=None):
    """
    Build a simple text query for semantic search.
    All fields are optional.
    
    ingredients: list of strings
    diet: string
    cuisine: string
    """
    parts = []

    if diet:
        parts.append(str(diet))

    if cuisine:
        parts.append(str(cuisine))

    if ingredients:
        parts.append(" ".join(ingredients))

    query = " ".join(parts)

    return query.strip()