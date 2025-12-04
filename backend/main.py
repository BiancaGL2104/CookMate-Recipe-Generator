from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from rag_pipeline.search import search_recipes  
from rag_pipeline.generator import generate_recipe_with_rag

from fastapi.middleware.cors import CORSMiddleware

import logging
import time


app = FastAPI(title="CookMate Backend")

logging.basicConfig(
    filename="logs/backend.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("cookmate-backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    ingredients: List[str] | str
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    k: int = 5

class RecipeOut(BaseModel):
    recipe_id: int
    title: str
    ingredients_list: List[str]
    steps_list: List[str]
    calories: float
    fat: float
    carbs: float
    protein: float

class GenerateRequest(BaseModel):
    ingredients: List[str] | str
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    k: int = 5


class GeneratedRecipeOut(BaseModel):
    # very loose structure, enough for frontend to use
    input_ingredients: List[str]
    diet: Optional[str]
    cuisine: Optional[str]
    generated_recipe: dict

def normalize_ingredients(ing):
    """
    Accepts either a string 'tomato, garlic, pasta' or a list of strings.
    Always returns a list of cleaned ingredient strings.
    """
    if isinstance(ing, str):
        return [x.strip() for x in ing.split(",") if x.strip()]
    return ing


@app.get("/")
def root():
    return {"status": "ok", "message": "Welcome to CookMate API"}

@app.get("/health")
def health():
    return {"status": "ok", "message": "CookMate backend running"}

@app.post("/search_recipes", response_model=List[RecipeOut])
def search_recipes_endpoint(payload: SearchRequest):
    start = time.time()
    ingredients = normalize_ingredients(payload.ingredients)

    results = search_recipes(
        ingredients=ingredients,
        diet=payload.diet,
        cuisine=payload.cuisine,
        k=payload.k,
    )

    elapsed = time.time() - start

    logger.info(
        "SEARCH | ingredients=%s | diet=%s | cuisine=%s | k=%d | results=%d | time=%.3fs",
        ingredients, payload.diet, payload.cuisine, payload.k, len(results), elapsed
    )
    return results



@app.post("/generate_recipe", response_model=GeneratedRecipeOut)
def generate_recipe_endpoint(payload: GenerateRequest):
    ingredients = normalize_ingredients(payload.ingredients)

    start = time.time()
    result = generate_recipe_with_rag(
        ingredients=ingredients,
        diet=payload.diet,
        cuisine=payload.cuisine,
        k=payload.k,
    )
    elapsed = time.time() - start

    logger.info(
        "GENERATE | ingredients=%s | diet=%s | cuisine=%s | k=%d | time=%.3fs",
        ingredients, payload.diet, payload.cuisine, payload.k, elapsed
    )

    generated_recipe = result.get("generated_recipe") or {}

    return {
        "input_ingredients": result.get("input_ingredients", ingredients),
        "diet": result.get("diet", payload.diet),
        "cuisine": result.get("cuisine", payload.cuisine),
        "generated_recipe": generated_recipe,
    }


