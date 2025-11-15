# CookMate – Requirements Document

---

## 1. Project Summary
CookMate is an AI-powered cooking assistant that generates recipes based on the ingredients a user already has, their dietary preferences, and desired cuisine.  
The goal is to reduce food waste, save time, and provide personalized meal inspiration using GenAI techniques.

---

## 2. Main Features

### 2.1 Ingredient-Based Recipe Generation
- User inputs a list of ingredients they currently have.
- System generates a realistic recipe using mostly those ingredients.

### 2.2 Dietary Preferences
Supports:
- Vegetarian  
- Vegan  
- Halal  
- Gluten-free  
- Lactose-free  
- Allergies (optional stretch goal)

### 2.3 Cuisine & Meal-Type Selection
User can select preferred cuisine (e.g., Italian, Asian, Mediterranean) and meal type (breakfast/lunch/dinner/snack).

### 2.4 Retrieval-Augmented Generation (RAG)
- System retrieves similar recipes from a dataset using embeddings + a vector database.
- Retrieved recipes are passed into the LLM to ensure realistic, grounded output.
- Avoids hallucinated steps or non-existent ingredient combinations.

### 2.5 Nutrition Estimation
- Approximate macronutrient and calorie calculation based on ingredients.
- Rule-based (no external APIs required).

---

## 3. Target Users
GenChef is designed for:
- University students  
- Busy professionals  
- Beginner cooks  
- Anyone who needs fast cooking inspiration  
- Users with dietary constraints  

---

## 4. User Inputs

Users provide the following:

### 4.1 Ingredients
List of available ingredients.

### 4.2 Preferences
- Diet type  
- Cuisine  
- Meal type  
- Maximum cooking time  
- Number of servings  

### 4.3 Input JSON Format (Backend API)
```json
{
  "ingredients": ["tomato", "pasta", "garlic"],
  "diet": "vegetarian",
  "cuisine": "Italian",
  "meal_type": "dinner",
  "max_time_minutes": 30,
  "servings": 2
}
```

---

## 5. System Output 

System returns a structured JSON recipe:

### 5.1 Output JSON Format
```json
{
  "title": "Creamy Tomato Garlic Pasta",
  "ingredients": [
    {"name": "pasta", "quantity": 200, "unit": "g"},
    {"name": "tomato", "quantity": 2, "unit": "pcs"},
    {"name": "garlic", "quantity": 3, "unit": "cloves"},
    {"name": "olive oil", "quantity": 1, "unit": "tbsp"}
  ],
  "steps": [
    "Boil the pasta according to package instructions.",
    "Sauté garlic in olive oil.",
    "Add chopped tomatoes and cook until soft.",
    "Mix with pasta and serve warm."
  ],
  "time_minutes": 25,
  "servings": 2
}
```

---

## 6. Constraints

### 6.1 Ingredient Constraints
* Recipe must use **mostly** user-provided ingredients.
* System may add *small staple items*, like salt, oil, pepper and basic spices.

### 6.2 Dietary Constraints
Must strictly follow the selected diet:
* Vegan $\rightarrow$ no animal products
* Vegetarian $\rightarrow$ no mean/fish
* Gluten-free $\rightarrow$ no wheat/pasta unless GF
* Halal $\rightarrow$ no pork, alcohol

### 6.3 Output Structure
* Must return valid JSON.
Must include all required fields.

---

## 7. Functional Requirements

### 7.1 Retrieval
* Convert recipes to embeddings.
* Retrieve top-k relevant recipes from FAISS/Chroma.
* Use retrieved recipes in the LLM prompt.

### 7.2 Generation
* Use LLM to produce final recipe based on user input + retrieved recipes.

### 7.3 Backend
* Expose a /generate_recipe API endpoint.
* Handle JSON input and output.

### 7.4 Frontend
* Simple UI for entering ingredients and preferences.
* Displays generated recipe and nutritional info.

### 7.5 Nutrition Calculation
* Rule-based estimation after recipe generation.

---

## 8. Non-Functional Requirements
### 8.1 Performance
* Recipe generation should complete within 3-8 seconds.

### 8.2 Usability
* Simple, beginner-friendly UI.
* Provide error messages when needed.

### 8.3 Stability
* LLM outputs should be consistent.
* System must handle invalid input gracefully.

---

## 9. Metrics for Success

### 9.1 Automatic Evaluation
* Ingredient constraint satisfaction rate
* Dietary constraint satisfaction rate
* Non-hallucinated steps

### 9.2 Human Study
Users rate:
* Clarity of the recipe
* Realism
* Appeal
* Correct dietary adherence

---

## 10. Risks & Limitations
* LLM may hallucinate rare ingredients if prompt not strict
* Vegetarian/halal/allergy enforcement may require careful checking
* Nutritional estimates are approximate

--- 

## 11. Future Extensions 
* Full weekly meal plans
* Shopping list generator
* Price estimation
* Voice input
* Multi-step refinement, for example: "make it spicier", "less calories", etc.