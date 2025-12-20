
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# Load dataset
df = pd.read_csv("patient_symptoms_textual.csv")

# Normalize column names
df.columns = df.columns.str.lower().str.strip()

# FIXED: Use your real column names
df = df.dropna(subset=["patient_concern", "diagnosis"])
df["patient_concern"] = df["patient_concern"].str.lower().str.strip()

# ML Pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", MultinomialNB())
])

X = df["patient_concern"]
y = df["diagnosis"]

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)
model.fit(X_train, y_train)

print("Model Accuracy:", accuracy_score(y_test, model.predict(X_test)))
print("\n===== ADVANCED AI SYMPTOM CHECKER =====\n")

# ----------------------------------------
# Example 1 — Emergency Level Detection
# ----------------------------------------
def detect_emergency(sym):
    emergency_keywords = {
        "chest pain": "HIGH",
        "breathing difficulty": "HIGH",
        "severe headache": "MEDIUM",
        "vomiting": "MEDIUM",
        "fever": "LOW",
        "cold": "LOW"
    }

    for i,j in emergency_keywords.items():
        if i in sym:
            return j
    
    return "LOW"

# ----------------------------------------
# Example 2 — Multi symptom cleaner
# ----------------------------------------
def clean_input(sym):
    return sym.lower().replace(",", " ").strip()

# ----------------------------------------
# Example 3 — Remedies
# ----------------------------------------
remedies = {
    "migraine": ["drink 2L water", "reduce screen time", "sleep 8 hours"],
    "viral fever": ["take paracetamol 500mg (doctor-advised)", "drink warm water", "rest"],
    "gastritis": ["eat curd rice", "avoid spicy food", "drink ORS"],
    "food poisoning": ["ORS solution", "light khichdi", "avoid oily food"]
}

# ----------------------------------------
# Example 4 — Doctor Suggestion
# ----------------------------------------
doctor_map = {
    "dengue": "General Physician / Internal Medicine",
    "migraine": "Neurologist",
    "asthma": "Pulmonologist",
    "food poisoning": "Gastroenterologist",
    "gastritis": "Gastroenterologist",
}

def suggest_doctor(disease):
    return doctor_map.get(disease, "General Physician")

# ----------------------------------------
# Example 5 — Diet Plan
# ----------------------------------------
diet_plan = {
    "gastritis": {
        "recommended": ["curd rice", "boiled vegetables"],
        "avoid": ["spicy food", "coffee"]
    },
    "fever": {
        "recommended": ["warm soup", "khichdi"],
        "avoid": ["cold drinks"]
    },
    "food poisoning": {
        "recommended": ["ORS", "boiled potatoes"],
        "avoid": ["street food", "milk"]
    }
}

# ----------------------------------------
# Example 6 — Safe Prescription Template
# ----------------------------------------
prescription_template = {
    "viral fever": ["Paracetamol 500mg (doctor advised)", "drink warm water"],
    "gastritis": ["Gelusil (doctor advised)", "eat soft food"],
    "migraine": ["Take rest", "reduce light/sound"]
}

# ----------------------------------------
# CHAT LOOP
# ----------------------------------------
while True:
    user = input("\nDescribe your symptoms (or type exit): ").lower()
    
    if user in ["exit", "quit", "bye"]:
        print("\nTake care! Goodbye.")
        break

    user = clean_input(user)

    predicted_disease = model.predict([user])[0]
    
    print("\n Predicted Diagnosis:", predicted_disease)

    # Example 1: Emergency Level
    level = detect_emergency(user)
    print("\n Emergency Level:", level)

    # Example 3: Remedies
    if predicted_disease in remedies:
        print("\n Home Remedies:")
        for r in remedies[predicted_disease]:
            print(" -", r)

    # Example 4: Doctor Suggestion
    print("\n Doctor to Visit:", suggest_doctor(predicted_disease))

    # Example 5: Diet Plan
    if predicted_disease in diet_plan:
        print("\n Diet Recommendations:")
        print(" Recommended:", ", ".join(diet_plan[predicted_disease]["recommended"]))
        print(" Avoid:", ", ".join(diet_plan[predicted_disease]["avoid"]))

    # Example 6: Prescription Template
    if predicted_disease in prescription_template:
        print("\n General Advice:")
        for p in prescription_template[predicted_disease]:
            print(" -", p)

    print("\n----------------------------------------")
