import os
from dataclasses import dataclass
from typing import List, Dict, Any

from rag_pipeline.format_retrieved import format_retrieved



@dataclass
class UserRequest:
    ingredients: List[str]
    diet: str  
    cuisine: str  



def _load_template() -> str:
    """
    Load the CookMate RAG prompt template from
    rag_pipeline/prompt_templates/cookmate_rag_prompt.txt
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    template_path = os.path.join(
        base_dir,
        "rag_pipeline",
        "prompt_templates",
        "cookmate_rag_prompt.txt",
    )

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()



def build_rag_prompt(user: UserRequest, retrieved_recipes: List[Dict[str, Any]]) -> str:
    """
    Build the full RAG prompt string by:
    - loading the template
    - filling in {{INGREDIENTS}}, {{DIET}}, {{CUISINE}}, {{RETRIEVED_RECIPES}}
    """
    template = _load_template()

    ingredients_text = ", ".join(user.ingredients)

    retrieved_block = format_retrieved(retrieved_recipes)

    prompt = (
        template
        .replace("{{INGREDIENTS}}", ingredients_text)
        .replace("{{DIET}}", user.diet or "none")
        .replace("{{CUISINE}}", user.cuisine or "")
        .replace("{{RETRIEVED_RECIPES}}", retrieved_block)
    )

    return prompt