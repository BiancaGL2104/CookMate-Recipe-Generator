import os
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

import logging
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


def build_query_text(ingredients, diet=None, cuisine=None):
    """
    ingredients: list[str] or comma-separated string
    diet, cuisine: optional strings
    """
    if isinstance(ingredients, str):
        ingredients_str = ingredients
    else:
        ingredients_str = ", ".join(ingredients)

    parts = [f"Ingredients: {ingredients_str}"]
    if diet:
        parts.append(f"Diet: {diet}")
    if cuisine:
        parts.append(f"Cuisine: {cuisine}")
    return ". ".join(parts)


def search_recipes(ingredients, diet=None, cuisine=None, k=5):
    """
    Returns top-k matching recipes as a list of dicts.
    """
    query_text = build_query_text(ingredients, diet=diet, cuisine=cuisine)
    query_emb = model.encode(
        [query_text],
        normalize_embeddings=True
    ).astype("float32")

    ntotal = index.ntotal
    if k > ntotal:
        k = ntotal

    scores, indices = index.search(query_emb, k)
    scores = scores[0]
    indices = indices[0]

    # ---- DEDUPLICATION STEP ----
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

    results = []
    for idx in indices:
        row = df_emb.iloc[int(idx)]
        results.append({
            "recipe_id": int(row["recipe_id"]),
            "title": row["title"],
            "ingredients_list": row["ingredients_list"],
            "steps_list": row["steps_list"],
            "calories": float(row["Calories"]),
            "fat": float(row["FatContent"]),
            "carbs": float(row["CarbohydrateContent"]),
            "protein": float(row["ProteinContent"])
        })
    
    logger.info(
        "RETRIEVAL | query='%s' | top_k=%d | indices=%s",
        query_text, k, indices
    )
    logger.info("RETRIEVAL | scores=%s", scores)

    return results