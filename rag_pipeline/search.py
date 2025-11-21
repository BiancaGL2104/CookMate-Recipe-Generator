import os
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(__file__)) 

CLEAN_PATH = os.path.join(BASE_DIR, "data", "cleaned", "cleaned_recipes.json")
EMB_PATH = os.path.join(BASE_DIR, "embeddings", "recipe_embeddings.npy")
INDEX_PATH = os.path.join(BASE_DIR, "embeddings", "faiss_index.bin")
IDMAP_PATH = os.path.join(BASE_DIR, "embeddings", "id_mapping.csv")

df_clean = pd.read_json(CLEAN_PATH)
df_emb = df_clean.iloc[:522513].reset_index(drop=True)  

embeddings = np.load(EMB_PATH)
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
    query_emb = model.encode([query_text], normalize_embeddings=True)
    
    scores, indices = index.search(query_emb.astype(np.float32), k)
    indices = indices[0]

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
    return results

