import requests

payload = {
    "ingredients": ["tomato", "garlic", "pasta"],
    "diet": "vegetarian",
    "cuisine": "Italian",
    "k": 3
}

resp = requests.post("http://127.0.0.1:8000/search_recipes", json=payload)
print(resp.status_code)
print(resp.json())
