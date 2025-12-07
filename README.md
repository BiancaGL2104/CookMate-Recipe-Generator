# 🍳 **CookMate – AI-Powered Recipe Generator using RAG**

CookMate is a smart recipe assistant that transforms the ingredients you already have at home into complete, structured, step-by-step recipes.
It combines **retrieval-augmented generation (RAG)**, **local LLMs (LLaMA 3 via Ollama)**, and a **modern Streamlit UI** to deliver personalized cooking recommendations.

---

# 🌟 **Features**

### 🔍 Retrieval-Based Recipe Search

* Finds the most similar recipes based on your input ingredients
* Uses **SentenceTransformers embeddings** + **Faiss ANN search**
* Displays full ingredient lists, quantities, steps, and nutrition

### 🍽 AI-Generated Recipes (LLaMA 3 + RAG)

* Creates *new* recipes using retrieved examples as grounding
* Ensures structured JSON output (validated)
* Provides:

  * ingredients (with quantities)
  * step-by-step instructions
  * cooking time & servings
  * reasoning
  * approximate nutrition

### ✨ Beautiful, Modern Streamlit UI

* Hero section, clean layout, soft gradients
* Pills/chips for tags
* Recipe cards with shadow & spacing
* Two main tabs: **Search** and **Generate**

### 📊 Evaluation & Testing

* Custom evaluation scenarios
* Unit tests for API, nutrition, generator, retrieval
* Full RAG pipeline notebooks documenting every step

---

# 🏗️ **Architecture Overview**

Each request flows through four components:

```
User (Streamlit UI)
        ↓
FastAPI Backend (main.py)
        ↓
RAG Pipeline (retrieval → prompt → LLM → validation)
        ↓
Ollama (LLaMA 3)
        ↓
Return structured JSON recipe
```

---

# 📁 **Repository Structure**

```
CookMate-Recipe-Generator/
│
├── backend/
│   └── main.py                # FastAPI app (REST API)
│
├── frontend/
│   └── app.py                 # Streamlit interface
│
├── rag_pipeline/              # RAG core logic
│   ├── query_builder.py
│   ├── search.py
│   ├── format_retrieved.py
│   ├── prompt_builder.py
│   ├── generator.py
│   └── prompt_templates/
│       └── cookmate_rag_prompt.txt
│
├── nutrition/
│   ├── estimator.py           # Nutrition estimation
│
├── data/
│   ├── raw/                   # Dataset before cleaning
│   ├── cleaned/
│   │   ├── cleaned_recipes.json
│   │   └── cleaned_recipes.parquet
│   └── evaluation_scenarios.json
│
├── embeddings/                # Ready-made ANN index & embeddings
│   ├── recipe_embeddings.npy
│   ├── faiss_index.bin
│   └── id_mapping.csv
│
├── notebooks/                 # All exploration & development notebooks
│   ├── 00_dataset_compare.ipynb
│   ├── 01_dataset_overview.ipynb
│   ├── 02_clean_dataset.ipynb
│   ├── 03_embeddings_and_faiss.ipynb
│   ├── 04_rag_search_tests.ipynb
│   ├── 05_query_builder.ipynb
│   ├── 06_format_retrieved.ipynb
│   ├── 07_prompt_and_generation.ipynb
│   └── 08_evaluation_scenarios.ipynb
│
├── tests/
│   ├── test_search_endpoint.py
│   ├── test_generate_recipe.py
│   └── test_nutrition.py
│
├── assets/
│   └── cookmate_hero.jpg
│
├── docs/
│   ├── architecture_diagram.png
│   ├── requirements.md
│   └── roles.md
│
├── logs/
│   └── backend.log
│
├── .env.example               # Example environment settings
├── requirements.txt
├── .gitignore
└── README.md
```

---

# ⚙️ **Installation & Setup**

## 1️⃣ Clone the repository

```bash
git clone https://github.com/your-repo-url/CookMate-Recipe-Generator.git
cd CookMate-Recipe-Generator
```

## 2️⃣ Create & activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

## 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

## 4️⃣ Install & start Ollama (local LLM)

Download from: [https://ollama.com](https://ollama.com)

```bash
ollama serve
ollama pull llama3
```

## 5️⃣ Start the backend (FastAPI)

```bash
uvicorn backend.main:app --reload
```

API available at:

* [http://127.0.0.1:8000](http://127.0.0.1:8000)
* [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger)

## 6️⃣ Start the frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

UI launches automatically in your browser.

---

# 🧠 **RAG Pipeline Details**

### Retrieval

* Embedding model: `all-MiniLM-L6-v2`
* ANN index: **Faiss FlatIP**
* Search: cosine similarity
* Deduplication & ranking applied

### Prompt Construction

Prompt includes:

* User pantry
* Dietary restrictions & cuisine
* Retrieved recipe snippets
* Strict JSON schema
* Explicit instructions for ingredient quantities

### Generation

* Local model: **LLaMA 3 via Ollama**
* JSON validation loop (retry on failure)
* Structured fields:

  ```json
  {
    "title": "",
    "ingredients": [
        {"quantity": "...", "unit": "...", "item": "..."}
    ],
    "steps": [],
    "time_minutes": 0,
    "servings": 0,
    "diet": "",
    "cuisine": "",
    "reason": ""
  }
  ```

### Nutrition Estimation

* Averaged from retrieved examples
* Returned as `{ calories, protein, carbs, fat }`

---

# 🧪 **Running Tests**

```bash
pytest tests
```

Covers:

* retrieval correctness
* nutrition estimator
* generation pipeline validity

---

# 📊 **Evaluation**

Evaluation scenarios are defined in:

```
data/evaluation_scenarios.json
```

Notebook `08_evaluation_scenarios.ipynb` tests:

* ingredient match quality
* diet/cuisine adherence
* recipe coherence
* JSON validity
* cooking feasibility

---

# 👥 **Team Roles & Contributions**

### **Bianca-Gabriela Leoveanu**

* Dataset comparison, cleaning, preprocessing
* Embeddings + Faiss index creation
* Retrieval pipeline & search logic
* Frontend UI (Streamlit)
* Backend integration testing
* Project structure & documentation

### **Teammate**

* Query builder
* Retrieved recipe formatter
* Prompt builder
* RAG generator & JSON validation
* Evaluation scenarios & analysis
* Project structure & documentation

---

# 🚧 **Limitations**

* Works best with English datasets
* Dependent on local LLM compute
* Limited dataset size compared to production-scale RAG systems
* No user authentication / history

---

# 🚀 **Future Work**

* Deploy backend & frontend online
* Improve UI responsiveness & animations
* Add user accounts + saved recipes
* Add multilingual support
* Fine-tune a cooking-specific LLM model

---

# 🎉 **Enjoy CookMate!**

Turn your fridge into recipes. Bon appétit! 🍽️💡

