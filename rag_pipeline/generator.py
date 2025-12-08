import json
from typing import List, Optional, Dict, Any

import requests

from rag_pipeline.query_builder import build_query
from rag_pipeline.search import search_recipes
from rag_pipeline.prompt_builder import UserRequest, build_rag_prompt
from nutrition.estimator import estimate_nutrition_from_retrieved

import logging

logger = logging.getLogger("cookmate-backend")


def run_local_llm(
    prompt: str,
    model: str = "llama3",
    temperature: float = 0.2,
    timeout: int = 120,
) -> str:
    """
    Call the local LLaMA model via Ollama.

    Make sure `ollama serve` is running in another terminal:
        ollama run llama3
    """
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "")


def validate_recipe_json(text: str):
    """
    Checks that the model output is valid JSON and matches required fields.
    Returns (True, parsed_json) or (False, error_message).
    """
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        return False, f"JSON decode error: {e}"

    required_fields = [
        "title",
        "ingredients",
        "steps",
        "time_minutes",
        "servings",
        "diet",
        "cuisine",
        "reason",
    ]

    missing = [f for f in required_fields if f not in parsed]
    if missing:
        return False, f"Missing fields: {missing}"

    if not isinstance(parsed["ingredients"], list):
        return False, "ingredients must be a list"

    if not isinstance(parsed["steps"], list):
        return False, "steps must be a list"

    return True, parsed


def generate_recipe(
    pantry: List[str],
    diet: Optional[str] = None,
    cuisine: Optional[str] = None,
    k: int = 3,
    max_retries: int = 1,
) -> Dict[str, Any]:
    """
    Full CookMate RAG pipeline in one function.

    1. Build query from pantry + diet + cuisine
    2. Retrieve similar recipes with search_recipes(...)
    3. Estimate nutrition from retrieved recipes
    4. Build RAG prompt with build_rag_prompt(...)
    5. Call local LLM (Ollama / LLaMA 3)
    6. Validate JSON against our schema
    7. Retry once if JSON is invalid (optional)
    8. Return either a recipe dict or an error description
    """

    user = UserRequest(
        ingredients=pantry,
        diet=diet,
        cuisine=cuisine,
    )

    query = build_query(
        ingredients=user.ingredients,
        diet=user.diet,
        cuisine=user.cuisine,
    )

    retrieved = search_recipes(query, k=k)
    if not retrieved:
        return {
            "success": False,
            "error": "no_recipes_found",
            "message": "search_recipes returned no candidates",
            "pantry": pantry,
            "diet": diet,
            "cuisine": cuisine,
        }

    nutrition_estimate = estimate_nutrition_from_retrieved(retrieved)

    prompt = build_rag_prompt(user, retrieved)

    prompt += """
    
IMPORTANT: You must answer ONLY with a single JSON object that matches this schema.

- "title": string
- "ingredients": an ARRAY.
  Each element SHOULD be an OBJECT with:
    - "item": ingredient name (string)
    - "quantity": quantity and unit as a single string (e.g. "1 cup", "2 tbsp", "200 g", "1 small", "2 cloves").
  Example:
  "ingredients": [
    { "item": "rice", "quantity": "1 cup" },
    { "item": "onion", "quantity": "1 small" },
    { "item": "garlic", "quantity": "2 cloves" }
  ]

If the retrieved recipes do not give an exact quantity, infer a reasonable quantity
for 1 batch of the recipe based on typical home cooking. NEVER leave out the quantity;
always provide something like "1 cup", "2 tbsp", "200 g", etc.

Do NOT include any commentary, explanation, prose, or markdown. 
Return ONLY the JSON object.
"""

    last_raw_output = ""
    last_error_message = ""

    for attempt in range(max_retries + 1):
        last_raw_output = run_local_llm(prompt)

        ok, result = validate_recipe_json(last_raw_output)
        if ok:
            recipe = result

            if nutrition_estimate:
                recipe["nutrition"] = nutrition_estimate

            return {
                "success": True,
                "recipe": recipe,
                "raw_output": last_raw_output,
                "pantry": pantry,
                "diet": diet,
                "cuisine": cuisine,
            }
        else:
            last_error_message = result

            if attempt < max_retries:
                prompt = (
                    prompt
                    + "\n\nYou produced INVALID JSON. "
                    "Regenerate the ENTIRE recipe as VALID JSON that matches the schema. "
                    "Do NOT include any text outside the JSON object."
                )

    return {
        "success": False,
        "error": "invalid_json",
        "validation_message": last_error_message,
        "raw_output": last_raw_output,
        "pantry": pantry,
        "diet": diet,
        "cuisine": cuisine,
    }
