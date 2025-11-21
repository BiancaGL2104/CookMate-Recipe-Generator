from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

from rag_pipeline.search import search_recipes  

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

class RecipeOut(BaseModel):
    recipe_id: int
    title: str
    ingredients_list: List[str]
    steps_list: List[str]
    calories: float
    fat: float
    carbs: float
    protein: float

@app.get("/")
def root():
    return {"status": "ok", "message": "Welcome to CookMate API"}

@app.get("/health")
def health():
    return {"status": "ok", "message": "CookMate backend running"}

@app.post("/search_recipes", response_model=List[RecipeOut])
def search_recipes_endpoint(payload: SearchRequest):
    results = search_recipes(
        ingredients=payload.ingredients,
        diet=payload.diet,
        cuisine=payload.cuisine,
        k=payload.k,
    )
    return results
