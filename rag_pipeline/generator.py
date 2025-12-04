import os
import json
import re
import time
from typing import List, Optional

from openai import OpenAI
from .search import search_recipes
from nutrition.estimator import estimate_nutrition_from_retrieved

import logging
logger = logging.getLogger("cookmate-backend")

# 🔑 Hugging Face Router config (OpenAI-compatible)
HF_BASE_URL = "https://router.huggingface.co/v1"
MODEL_NAME = "HuggingFaceTB/SmolLM3-3B:hf-inference"


# -----------------------------
#  Helper: Lazy client creation
# -----------------------------
def get_client() -> OpenAI:
    """
    Lazily create the OpenAI-compatible client.
    This avoids crashing on import if HF_API_TOKEN is not set.
    """
    hf_token = os.environ.get("HF_API_TOKEN")
    if not hf_token:
        msg = "HF_API_TOKEN is not set. Please export HF_API_TOKEN before running CookMate."
        logger.error("RAG | %s", msg)
        raise RuntimeError(msg)

    return OpenAI(
        base_url=HF_BASE_URL,
        api_key=hf_token,
    )


# -----------------------------
#  Helper: extract JSON block
# -----------------------------
def extract_json_from_text(text: str) -> str:
    """
    Try to extract a JSON object substring from noisy text.
    If nothing is found, return the original text.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


# -----------------------------
#  Prompt Builder
# -----------------------------
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


# -----------------------------
#  Main RAG Pipeline
# -----------------------------
def generate_recipe_with_rag(
    ingredients: List[str],
    diet: Optional[str] = None,
    cuisine: Optional[str] = None,
    k: int = 5,
):
    if not ingredients:
        raise ValueError("At least one ingredient is required")

    # 1) Retrieve similar recipes via FAISS
    retrieved = search_recipes(ingredients, diet, cuisine, k)

    # 2) Build RAG prompt
    prompt = build_rag_prompt(ingredients, diet, cuisine, retrieved)

    logger.info(
        "RAG | ingredients=%s | diet=%s | cuisine=%s | retrieved=%d",
        ingredients, diet, cuisine, len(retrieved),
    )

    # 3) Call HF Router
    try:
        client = get_client()
        start = time.time()
        logger.info("RAG | Calling LLM model=%s", MODEL_NAME)

        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful cooking assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=512,
            temperature=0.7,
        )
        elapsed = time.time() - start

        raw_text = completion.choices[0].message.content or ""
        logger.info(
            "RAG | LLM call succeeded | time=%.3fs | response_length=%d",
            elapsed, len(raw_text),
        )

    except Exception as e:
        # If the API fails, log and fallback
        logger.error("RAG | LLM error: %r", e)
        error_nutrition = estimate_nutrition_from_retrieved(retrieved)

        return {
            "input_ingredients": ingredients,
            "diet": diet,
            "cuisine": cuisine,
            "retrieved": retrieved,
            "generated_recipe": {
                "title": "Generation error",
                "raw_text": f"HuggingFace Router error: {repr(e)}",
                "nutrition": error_nutrition,
            },
        }

    # -----------------------------
    # 4) Clean + Parse JSON
    # -----------------------------
    raw_text_clean = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()

    if raw_text_clean.startswith("```"):
        raw_text_clean = re.sub(r"^```[a-zA-Z0-9]*\s*", "", raw_text_clean)
        if raw_text_clean.endswith("```"):
            raw_text_clean = raw_text_clean.rsplit("```", 1)[0].strip()

    # NEW: JSON extraction fallback
    candidate = extract_json_from_text(raw_text_clean)

    try:
        recipe = json.loads(candidate)
        logger.info("RAG | JSON parse success")
    except Exception:
        logger.warning("RAG | JSON parse failed, returning raw_text")
        recipe = {
            "title": "Generated Recipe (unparsed JSON)",
            "raw_text": raw_text,
        }

    # -----------------------------
    # 5) Estimate Nutrition
    # -----------------------------
    nutrition = estimate_nutrition_from_retrieved(retrieved)

    # -----------------------------
    # 6) Attach Nutrition
    # -----------------------------
    if isinstance(recipe, dict):
        recipe_with_nutrition = {
            **recipe,
            "nutrition": nutrition,
        }
    else:
        recipe_with_nutrition = {
            "title": "Generated Recipe (unexpected format)",
            "raw_text": raw_text,
            "nutrition": nutrition,
        }

    return {
        "input_ingredients": ingredients,
        "diet": diet,
        "cuisine": cuisine,
        "retrieved": retrieved,
        "generated_recipe": recipe_with_nutrition,
    }
