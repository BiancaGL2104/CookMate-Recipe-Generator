import os
import ast
import logging
from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("cookmate-backend")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CLEAN_PATH = os.path.join(BASE_DIR, "data", "cleaned", "cleaned_recipes.json")
EMB_PATH = os.path.join(BASE_DIR, "embeddings", "recipe_embeddings.npy")
INDEX_PATH = os.path.join(BASE_DIR, "embeddings", "faiss_index.bin")
IDMAP_PATH = os.path.join(BASE_DIR, "embeddings", "id_mapping.csv")

df_clean = pd.read_json(CLEAN_PATH)
embeddings = np.load(EMB_PATH).astype("float32")
N = embeddings.shape[0]
df_emb = df_clean.iloc[:N].reset_index(drop=True)

index = faiss.read_index(INDEX_PATH)
id_map = pd.read_csv(IDMAP_PATH)

model = SentenceTransformer("all-MiniLM-L6-v2")


def _parse_list_field(value) -> List[Any]:
    """
    Ensure that a column value becomes a Python list.
    Handles:
    - already-a-list
    - stringified list (e.g. '["a","b"]' or "['a','b']")
    - plain string
    """
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            return [value]

    if value is None:
        return []

    return [value]


def _merge_ingredient_quantities(row: pd.Series) -> List[Dict[str, Optional[str]]]:
    """
    Returns a list of objects:
    [
        {"ingredient": "...", "quantity": "..."},
        ...
    ]
    """
    names = _parse_list_field(row.get("ingredients_list"))
    qtys = _parse_list_field(row.get("quantities_list"))

    merged = []
    for i, name in enumerate(names):
        q = qtys[i] if i < len(qtys) else None
        merged.append(
            {
                "ingredient": str(name),
                "quantity": str(q) if q is not None else None,
            }
        )

    return merged


def _extract_steps(row: pd.Series) -> List[str]:
    steps = _parse_list_field(row.get("steps_list"))
    return [str(s) for s in steps]


def _safe_float(x) -> Optional[float]:
    try:
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return None
        return float(x)
    except Exception:
        return None


def search_recipes(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Search recipes using a free-form query string (already built by build_query).
    Returns top-k matching recipes as a list of dicts, including structured
    ingredients with quantities and full steps.
    """
    query_text = query

    query_emb = model.encode(
        [query_text],
        normalize_embeddings=True,
    ).astype("float32")

    ntotal = index.ntotal
    if k > ntotal:
        k = ntotal

    scores, indices = index.search(query_emb, k)
    scores = scores[0]
    indices = indices[0]

    # Deduplicate indices while preserving order
    seen = set()
    unique_indices = []
    unique_scores = []

    for idx, s in zip(indices, scores):
        idx_int = int(idx)
        if idx_int not in seen:
            seen.add(idx_int)
            unique_indices.append(idx_int)
            unique_scores.append(float(s))

    indices = unique_indices
    scores = unique_scores

    results: List[Dict[str, Any]] = []

    for idx in indices:
        row = df_emb.iloc[int(idx)]

        structured_ingredients = _merge_ingredient_quantities(row)
        steps = _extract_steps(row)

        result = {
            "recipe_id": int(row["recipe_id"]),
            "title": row["title"],
            "ingredients_list": _parse_list_field(row.get("ingredients_list")),
            "ingredients_structured": structured_ingredients,
            "steps_list": steps,
            "calories": _safe_float(row.get("Calories")),
            "fat": _safe_float(row.get("FatContent")),
            "carbs": _safe_float(row.get("CarbohydrateContent")),
            "protein": _safe_float(row.get("ProteinContent")),
        }

        results.append(result)

    logger.info(
        "RETRIEVAL | query='%s' | top_k=%d | indices=%s | scores=%s",
        query_text,
        k,
        indices,
        scores,
    )

    return results
