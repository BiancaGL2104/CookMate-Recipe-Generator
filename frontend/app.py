import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.title("CookMate – Recipe Finder")

ingredients_input = st.text_input("Ingredients (comma-separated)", "tomato, garlic")
diet = st.text_input("Diet (optional)", "vegetarian")
cuisine = st.text_input("Cuisine (optional)", "Italian")
k = st.slider("Number of recipes", 1, 10, 3)

if st.button("Search recipes"):
    ingredients = [x.strip() for x in ingredients_input.split(",") if x.strip()]
    payload = {
        "ingredients": ingredients,
        "diet": diet or None,
        "cuisine": cuisine or None,
        "k": k,
    }

    resp = requests.post(f"{BACKEND_URL}/search_recipes", json=payload)
    if resp.status_code == 200:
        results = resp.json()
        for r in results:
            st.subheader(r["title"])
            st.write("Ingredients:", ", ".join(r["ingredients_list"]))
            st.write("Calories:", r["calories"])
            st.write("---")
    else:
        st.error(f"Error from backend: {resp.status_code}")
