import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_generate_recipe_structure():
    payload = {
        "ingredients": ["tomato", "garlic", "pasta"],
        "diet": "vegetarian",
        "cuisine": "Italian",
        "k": 3,
    }

    resp = client.post("/generate_recipe", json=payload)
    assert resp.status_code == 200

    data = resp.json()

    assert "input_ingredients" in data
    assert "generated_recipe" in data

    recipe = data["generated_recipe"]
    assert isinstance(recipe, dict)

    # Always should have a title (even on error)
    assert "title" in recipe

    # Nutrition should always be present (even on error)
    assert "nutrition" in recipe
    nutrition = recipe["nutrition"]
    assert isinstance(nutrition, dict)
    for key in ["calories", "fat", "carbs", "protein"]:
        assert key in nutrition

    print("✅ test_generate_recipe_structure passed.")
    print("   Title:", recipe.get("title"))
    print("   Nutrition:", nutrition)


if __name__ == "__main__":
    print("Running test_generate_recipe_structure manually...")
    test_generate_recipe_structure()
