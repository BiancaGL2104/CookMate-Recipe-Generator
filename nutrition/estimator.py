from typing import List, Dict, Any


def estimate_nutrition_from_retrieved(retrieved: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Estimate nutrition for the generated recipe by averaging the calories/macros
    from the top-k retrieved recipes.

    retrieved: list of dicts returned by search_recipes()
               Each contains: calories, fat, carbs, protein

    Returns a dict:
        {
            "calories": ...,
            "fat": ...,
            "carbs": ...,
            "protein": ...
        }
    or {} if no nutrition data exists.
    """

    if not retrieved:
        return {}

    keys = ["calories", "fat", "carbs", "protein"]
    sums = {k: 0.0 for k in keys}
    count = 0

    for r in retrieved:
        try:
            valid = False
            for k in keys:
                val = r.get(k)
                if val is not None:
                    sums[k] += float(val)
                    valid = True
            
            if valid:
                count += 1
        except Exception:
            continue

    if count == 0:
        return {}

    return {k: sums[k] / count for k in keys}
