from estimator import estimate_nutrition_from_retrieved

dummy = [
    {"calories": 300, "fat": 10, "carbs": 40, "protein": 15},
    {"calories": 500, "fat": 20, "carbs": 60, "protein": 20},
]

print(estimate_nutrition_from_retrieved(dummy))
