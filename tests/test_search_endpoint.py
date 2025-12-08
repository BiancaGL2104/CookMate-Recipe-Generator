import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_search_recipes_basic():
    payload = {
        "ingredients": ["tomato", "garlic", "pasta"],
        "diet": "vegetarian",
        "cuisine": "Italian",
        "k": 5,
    }
    resp = client.post("/search_recipes", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0

    first = data[0]
    for key in [
        "recipe_id",
        "title",
        "ingredients_list",
        "steps_list",
        "calories",
        "fat",
        "carbs",
        "protein",
    ]:
        assert key in first

    print("✅ test_search_recipes_basic passed. Returned", len(data), "results.")


if __name__ == "__main__":
    print("Running test_search_recipes_basic manually...")
    test_search_recipes_basic()
