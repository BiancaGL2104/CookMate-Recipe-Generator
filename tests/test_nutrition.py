import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nutrition.estimator import estimate_nutrition_from_retrieved


def test_estimate_nutrition_average():
    retrieved = [
        {"calories": 300, "fat": 10, "carbs": 40, "protein": 15},
        {"calories": 500, "fat": 20, "carbs": 60, "protein": 25},
    ]

    result = estimate_nutrition_from_retrieved(retrieved)

    assert result["calories"] == 400
    assert result["fat"] == 15
    assert result["carbs"] == 50
    assert result["protein"] == 20

    print("✅ test_estimate_nutrition_average passed.")
    print("   Output:", result)


if __name__ == "__main__":
    print("Running test_estimate_nutrition_average manually...")
    test_estimate_nutrition_average()
