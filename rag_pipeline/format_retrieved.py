from typing import List, Dict, Any


def _as_list(x) -> list:
    """Ensure a value is treated as a list."""
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, str) and x.startswith("[") and x.endswith("]"):
        cleaned = x.strip("[]").replace("'", "").replace('"', "")
        return [item.strip() for item in cleaned.split(",") if item.strip()]
    return [x]


def format_single_recipe(recipe: Dict[str, Any], idx: int) -> str:
    """
    Format a single retrieved recipe as a structured text block.
    This will be inserted into the RAG prompt for the LLM to read,
    NOT as final JSON.
    """
    title = recipe.get("title", "").strip()
    category = recipe.get("category", "") or ""
    keywords = _as_list(recipe.get("keywords", []))
    ingredients = _as_list(recipe.get("ingredients_list", []))
    quantities = _as_list(recipe.get("quantities_list", []))
    steps = _as_list(recipe.get("steps_list", []))

    calories = recipe.get("calories", None)
    fat = recipe.get("fat", None)
    carbs = recipe.get("carbs", None)
    protein = recipe.get("protein", None)

    lines = []

    lines.append(f"Recipe {idx}:")
    lines.append(f"Title: {title}")

    if category:
        lines.append(f"Category: {category}")

    if keywords:
        lines.append("Keywords: " + ", ".join(str(k) for k in keywords))

    if quantities and len(quantities) == len(ingredients):
        lines.append("Ingredients:")
        for q, ing in zip(quantities, ingredients):
            lines.append(f"- {q} {ing}".strip())
    else:
        if ingredients:
            lines.append("Ingredients:")
            for ing in ingredients:
                lines.append(f"- {ing}")

    if steps:
        lines.append("Steps:")
        for i, step in enumerate(steps, start=1):
            lines.append(f"{i}. {step}")

    if any(v is not None for v in [calories, fat, carbs, protein]):
        lines.append("Nutrition (approx):")
        if calories is not None:
            lines.append(f"- Calories: {calories}")
        if fat is not None:
            lines.append(f"- Fat: {fat}")
        if carbs is not None:
            lines.append(f"- Carbs: {carbs}")
        if protein is not None:
            lines.append(f"- Protein: {protein}")

    return "\n".join(lines)


def format_retrieved(recipes: List[Dict[str, Any]]) -> str:
    """
    Format a list of retrieved recipes into a single text block
    to be inserted into the RAG prompt under {{RETRIEVED_RECIPES}}.
    """
    if not recipes:
        return "No retrieved recipes."

    blocks = []
    for i, r in enumerate(recipes, start=1):
        blocks.append(format_single_recipe(r, i))

    return "\n\n".join(blocks)