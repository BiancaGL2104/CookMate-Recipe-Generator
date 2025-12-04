import os
import requests
import streamlit as st

# =========================
# CONFIG
# =========================

BACKEND_URL = os.environ.get("COOKMATE_BACKEND_URL", "http://127.0.0.1:8000")
HERO_IMAGE_PATH = os.path.join("assets", "cookmate_hero.jpg")  # your AI image

st.set_page_config(
    page_title="CookMate – Smart Recipe Assistant",
    page_icon="🍝",
    layout="wide",
)

# =========================
# CUSTOM STYLES
# =========================

CUSTOM_CSS = """
<style>
/* Overall light background */
.stApp {
    background: radial-gradient(circle at top left, #ffe8e0 0, #fffdf8 40%, #f4f7ff 75%, #eaf5ff 100%);
    font-family: "Inter", -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
}

/* Tighten main container a bit */
.main > div {
    padding-top: 1.25rem;
}

/* Hero card (left) */
.hero-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 24px;
    padding: 1.75rem 2rem;
    box-shadow: 0 18px 55px rgba(15, 23, 42, 0.10);
    border: 1px solid rgba(243, 244, 246, 0.9);
    backdrop-filter: blur(18px);
    min-height: 320px;              /* roughly match image height */
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

/* Section cards */
.section-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 1.5rem 1.75rem;
    box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06);
    border: 1px solid rgba(229, 231, 235, 0.9);
}

/* Pills / chips */
.pill {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
    background: linear-gradient(135deg, #f9fafb, #eef2ff);
    border: 1px solid rgba(148, 163, 184, 0.35);
    color: #111827;
}

/* Divider */
.divider {
    border-top: 1px dashed rgba(148, 163, 184, 0.6);
    margin: 1rem 0 1rem 0;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    padding: 0.45rem 1rem;
    border-radius: 999px;
    background-color: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(209, 213, 219, 0.8);
}

/* Buttons */
.stButton > button {
    background-color: #f97316 !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.2rem !important;
    font-weight: 600 !important;
    border: none !important;
}
.stButton > button:hover {
    background-color: #ea580c !important;
}

/* Inputs */
.stTextArea textarea,
.stTextInput input {
    background-color: #ffffff !important;
    color: #111827 !important;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}

[data-testid="stSelectbox"] > div {
    background-color: #ffffff !important;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}

/* Typography */
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5,
[data-testid="stMarkdownContainer"] h6,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span {
    color: #111827 !important;
}

/* Hero image: only style the IMG, not the container */
[data-testid="stImage"] img {
    border-radius: 24px;
    object-fit: cover;
    width: 100%;
    max-height: 320px;   /* keeps it from going super tall */
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =========================
# HELPERS
# =========================

def parse_ingredients(text: str) -> list[str]:
    """Turn a comma-separated string into a list of non-empty ingredient strings."""
    return [x.strip() for x in text.split(",") if x.strip()]


def call_backend_search(ingredients: list[str], diet: str | None, cuisine: str | None, k: int = 5):
    payload = {"ingredients": ingredients, "diet": diet, "cuisine": cuisine, "k": k}
    resp = requests.post(f"{BACKEND_URL}/search_recipes", json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def call_backend_generate(ingredients: list[str], diet: str | None, cuisine: str | None, k: int = 5):
    payload = {"ingredients": ingredients, "diet": diet, "cuisine": cuisine, "k": k}
    resp = requests.post(f"{BACKEND_URL}/generate_recipe", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


def render_pills(items, prefix_icon=""):
    if not items:
        return
    pills_html = "".join(
        f'<span class="pill">{prefix_icon}{item}</span>' for item in items
    )
    st.markdown(pills_html, unsafe_allow_html=True)

# =========================
# LAYOUT – HERO (SIDE BY SIDE)
# =========================

left_col, right_col = st.columns([1.6, 1.2])

with left_col:
    st.markdown(
        """
        <div class="hero-card">
            <div>
                <div style="font-size:0.9rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#6b7280;">
                    🍳 COOKMATE
                </div>
                <h1 style="margin:0.35rem 0 0.5rem 0; font-size:2.3rem; line-height:1.2;">
                    Turn your fridge into <span style="color:#f97316;">recipes</span>.
                </h1>
                <p style="margin:0.25rem 0 0.75rem 0; font-size:0.98rem; color:#4b5563;">
                    Type the ingredients you have at home and let CookMate transform them
                    into a complete, easy-to-follow recipe.
                </p>
            </div>
            <div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin-top:0.5rem;">
                <span class="pill">✨ AI-powered recipe ideas</span>
                <span class="pill">🧊 Use what’s already in your kitchen</span>
                <span class="pill">🥗 Adaptable to your diet</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    if os.path.exists(HERO_IMAGE_PATH):
        # IMPORTANT: no use_column_width -> we use the new flag
        st.image(HERO_IMAGE_PATH, use_container_width=True)
    else:
        st.caption("Add your hero image at: " + HERO_IMAGE_PATH)

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# =========================
# INPUT CARD
# =========================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### 1 · Tell CookMate what you have")
st.markdown("<div style='margin-top: -0.5rem;'></div>", unsafe_allow_html=True)

ing_col, meta_col = st.columns([2.4, 1.6])

with ing_col:
    ingredients_text = st.text_area(
        "Ingredients (comma-separated)",
        "chicken, rice, onion, garlic",
        help="Example: tomato, onion, chicken, garlic",
        height=90,
    )

    ing_list_preview = parse_ingredients(ingredients_text)
    if ing_list_preview:
        st.caption("CookMate understands:")
        render_pills(ing_list_preview)

with meta_col:
    st.write("")
    diet_choice = st.selectbox(
        "Diet (optional)",
        ["None", "vegetarian", "vegan", "gluten-free", "low-carb", "pescatarian"],
        index=1,
        help="Used to adapt the recipe to your dietary preferences.",
    )

    cuisine_choice = st.selectbox(
        "Cuisine (optional)",
        ["None", "Italian", "Asian", "Mexican", "French", "Mediterranean", "Middle Eastern"],
        index=1,
        help="Helps CookMate style the recipe in the cuisine you like.",
    )

    with st.expander("⚙️ Advanced options"):
        k = st.slider(
            "How many similar recipes to use as inspiration (k)",
            min_value=1,
            max_value=15,
            value=5,
            help="CookMate quietly looks at k similar recipes in the background. Higher values may be a bit slower.",
        )
        st.caption("You can leave this as default if you’re not sure.")

diet = None if diet_choice == "None" else diet_choice
cuisine = None if cuisine_choice == "None" else cuisine_choice

st.markdown("</div>", unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =========================
# TABS: SEARCH & GENERATE
# =========================

search_tab, generate_tab = st.tabs(["🔍 Explore recipe ideas", "🍽 Create a new recipe"])

# ---------- SEARCH TAB ----------
with search_tab:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 2 · Explore ideas based on your ingredients")
    st.markdown("<div style='margin-top: -0.5rem;'></div>", unsafe_allow_html=True)

    search_clicked = st.button("🔎 Search recipe ideas", use_container_width=True)

    if search_clicked:
        ingredients = parse_ingredients(ingredients_text)

        if not ingredients:
            st.error("Please enter at least one ingredient.")
        else:
            with st.spinner("Looking for recipes that match your ingredients..."):
                try:
                    results = call_backend_search(ingredients, diet, cuisine, k)
                except Exception as e:
                    st.error(f"Search request failed: {e}")
                else:
                    if not results:
                        st.warning(
                            "No recipes found for these ingredients yet. Try changing or adding items."
                        )
                    else:
                        st.markdown("##### Results")
                        for r in results:
                            st.markdown(f"###### {r['title']}")
                            render_pills(r.get("ingredients_list", []), prefix_icon="🧂 ")

                            steps_preview = r.get("steps_list", [])[:3]
                            if steps_preview:
                                st.markdown("**Steps (preview):**")
                                for i, step in enumerate(steps_preview, start=1):
                                    st.markdown(f"{i}. {step}")

                            nutri_bits = []
                            if r.get("calories") is not None:
                                nutri_bits.append(f"{r['calories']:.0f} kcal")
                            if r.get("protein") is not None:
                                nutri_bits.append(f"{r['protein']:.1f} g protein")
                            if r.get("carbs") is not None:
                                nutri_bits.append(f"{r['carbs']:.1f} g carbs")
                            if r.get("fat") is not None:
                                nutri_bits.append(f"{r['fat']:.1f} g fat")

                            if nutri_bits:
                                st.caption(" · ".join(nutri_bits))

                            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- GENERATE TAB ----------
with generate_tab:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 3 · Let CookMate create a recipe for you")
    st.markdown("<div style='margin-top: -0.5rem;'></div>", unsafe_allow_html=True)

    generate_clicked = st.button("🍽 Generate recipe", type="primary", use_container_width=True)

    if generate_clicked:
        ingredients = parse_ingredients(ingredients_text)

        if not ingredients:
            st.error("Please enter at least one ingredient before generating a recipe.")
        else:
            with st.spinner("Creating your recipe..."):
                try:
                    data = call_backend_generate(ingredients, diet, cuisine, k)
                except Exception as e:
                    st.error(f"Generation request failed: {e}")
                else:
                    recipe = data.get("generated_recipe", {}) or {}

                    st.markdown("##### Result")
                    st.title(recipe.get("title", "Generated Recipe"))

                    meta_pills = []
                    if diet:
                        meta_pills.append(f"🥗 {diet}")
                    if cuisine:
                        meta_pills.append(f"🌍 {cuisine}")
                    render_pills(meta_pills)

                    # -------- INGREDIENTS --------
                    ing_list = recipe.get("ingredients")
                    st.subheader("🧂 Ingredients")
                    if isinstance(ing_list, list) and ing_list:
                        for item in ing_list:
                            st.markdown(f"- {item}")
                    else:
                        st.write("No structured ingredients found.")

                    # -------- STEPS --------
                    steps = recipe.get("steps")
                    st.subheader("👩‍🍳 Steps")
                    if isinstance(steps, list) and steps:
                        for i, step in enumerate(steps, start=1):
                            st.markdown(f"{i}. {step}")
                    else:
                        st.write("No structured steps found.")

                    # -------- NOTES --------
                    notes = recipe.get("notes")
                    if notes:
                        st.subheader("📝 Notes")
                        st.write(notes)

                    # -------- NUTRITION --------
                    nutrition = recipe.get("nutrition") or {}
                    if nutrition:
                        st.subheader("⚖️ Approximate nutrition")

                        bits = []
                        if nutrition.get("calories") is not None:
                            bits.append(f"{nutrition['calories']:.0f} kcal")
                        if nutrition.get("protein") is not None:
                            bits.append(f"{nutrition['protein']:.1f} g protein")
                        if nutrition.get("carbs") is not None:
                            bits.append(f"{nutrition['carbs']:.1f} g carbs")
                        if nutrition.get("fat") is not None:
                            bits.append(f"{nutrition['fat']:.1f} g fat")

                        if bits:
                            st.caption(" · ".join(bits))
                            st.caption(
                                "Estimated by averaging nutrition values of similar recipes CookMate used as inspiration."
                            )

                    # -------- RAW DEBUG (only if present) --------
                    if "raw_text" in recipe:
                        with st.expander("🔍 Raw AI output (debug)"):
                            st.code(recipe["raw_text"], language="json")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# FOOTER
# =========================

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption(
    "CookMate – An AI-powered recipe assistant built as a university Generative AI project."
)
