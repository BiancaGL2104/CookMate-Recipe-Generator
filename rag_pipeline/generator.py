import os
import json
from typing import List, Optional

from .search import search_recipes
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load model ONCE at import (much faster)
MODEL_NAME = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def build_rag_prompt(
    user_ingredients: List[str],
    diet: Optional[str],
    cuisine: Optional[str],
    retrieved_recipes: List[dict],
) -> str:

    ingredients_str = ", ".join(user_ingredients)
    diet_str = diet or "no specific diet"
    cuisine_str = cuisine or "any cuisine"

    context_parts = []
    for r in retrieved_recipes:
        ing = ", ".join(r["ingredients_list"])
        steps = " ".join(r["steps_list"][:3])
        context_parts.append(
            f"Title: {r['title']}\nIngredients: {ing}\nSteps: {steps}\n"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are CookMate, an AI that creates recipes.

User ingredients: {ingredients_str}
Diet: {diet_str}
Cuisine: {cuisine_str}

Here are example recipes from our database:

{context}

TASK:
Create a NEW recipe (not copied) that uses the user's ingredients.
Respect the diet/cuisine if provided.

Return ONLY JSON in this format:
{{
 "title": "...",
 "ingredients": ["..."],
 "steps": ["..."],
 "notes": "..."
}}
"""

    return prompt.strip()

def generate_recipe_with_rag(
    ingredients: List[str],
    diet: Optional[str] = None,
    cuisine: Optional[str] = None,
    k: int = 5,
):
    # 1. Retrieve similar recipes
    retrieved = search_recipes(ingredients, diet, cuisine, k)

    # 2. Build prompt
    prompt = build_rag_prompt(ingredients, diet, cuisine, retrieved)

    # 3. Tokenize + generate
    input_ids = tokenizer(prompt, return_tensors="pt", truncation=True).input_ids
    output_ids = model.generate(
        input_ids,
        max_length=512,
        temperature=0.7,
    )

    raw_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # 4. Try parsing JSON
    try:
        recipe = json.loads(raw_text)
    except:
        recipe = {"title": "Generated Recipe", "raw_text": raw_text}

    return {
        "input_ingredients": ingredients,
        "diet": diet,
        "cuisine": cuisine,
        "retrieved": retrieved,
        "generated_recipe": recipe
    }

