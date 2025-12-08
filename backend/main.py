from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from rag_pipeline.query_builder import build_query
from rag_pipeline.search import search_recipes
from rag_pipeline.generator import generate_recipe

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="CookMate Backend")

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


class IngredientQuantity(BaseModel):
    ingredient: str
    quantity: Optional[str] = None


class RecipeOut(BaseModel):
    recipe_id: int
    title: str

    ingredients_list: List[str] | str

    ingredients_structured: Optional[List[IngredientQuantity]] = None

    steps_list: List[str] | str

    calories: Optional[float] = None
    fat: Optional[float] = None
    carbs: Optional[float] = None
    protein: Optional[float] = None


class GenerateRequest(BaseModel):
    ingredients: List[str] | str
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    k: int = 3
    max_retries: int = 1


class GeneratedRecipeOut(BaseModel):
    success: bool
    pantry: List[str]
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    recipe: Optional[dict] = None
    raw_output: Optional[str] = None
    error: Optional[str] = None
    validation_message: Optional[str] = None


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
    if isinstance(payload.ingredients, str):
        ingredients = [x.strip() for x in payload.ingredients.split(",") if x.strip()]
    else:
        ingredients = payload.ingredients

    query = build_query(
        ingredients=ingredients,
        diet=payload.diet,
        cuisine=payload.cuisine,
    )

    results = search_recipes(query, k=payload.k)
    return results

@app.post("/generate_recipe", response_model=GeneratedRecipeOut)
def generate_recipe_endpoint(payload: GenerateRequest):
    if isinstance(payload.ingredients, str):
        pantry = [x.strip() for x in payload.ingredients.split(",") if x.strip()]
    else:
        pantry = payload.ingredients

    result = generate_recipe(
        pantry=pantry,
        diet=payload.diet,
        cuisine=payload.cuisine,
        k=payload.k,
        max_retries=payload.max_retries,
    )

    return {
        "success": result.get("success", False),
        "pantry": result.get("pantry", pantry),
        "diet": result.get("diet", payload.diet),
        "cuisine": result.get("cuisine", payload.cuisine),
        "recipe": result.get("recipe"),
        "raw_output": result.get("raw_output"),
        "error": result.get("error"),
        "validation_message": result.get("validation_message"),
    }
