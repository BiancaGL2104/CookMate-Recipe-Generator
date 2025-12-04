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

    # This line is only so you see something when running with python3
    print("✅ test_search_recipes_basic passed. Returned", len(data), "results.")


if __name__ == "__main__":
    # When running as a normal script: actually run the test function
    print("Running test_search_recipes_basic manually...")
    test_search_recipes_basic()
