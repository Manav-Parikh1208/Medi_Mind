# ====================================================
#      ADVANCED AI MEDICAL CHATBOT + DASHBOARD
# ====================================================

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score


# ====================================================
# 1. LOAD & CLEAN DATASET
# ====================================================
df = pd.read_csv("patient_symptoms_textual.csv")

# Normalize column names
df.columns = df.columns.str.lower().str.strip()

# Based on your dataset
df = df.dropna(subset=["patient_concern", "diagnosis"])
df["patient_concern"] = df["patient_concern"].str.lower().str.strip()

print("Dataset Loaded Successfully!")
print("Shape:", df.shape)
print(df.head())


# ====================================================
# 2. MODEL TRAINING (TF-IDF + Naive Bayes)
# ====================================================
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", MultinomialNB())
])

X = df["patient_concern"]
y = df["diagnosis"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)

model.fit(X_train, y_train)
accuracy = accuracy_score(y_test, model.predict(X_test))

print("\n====================================================")
print(" MODEL TRAINED SUCCESSFULLY")
print(" Accuracy:", accuracy)
print("====================================================\n")


# ====================================================
# 3. DATA VISUALISATIONS
# ====================================================

print("\nGenerating Visualisations...")

# A) Disease Frequency Bar Chart
disease_counts = df["diagnosis"].value_counts()
plt.figure(figsize=(10,6))
plt.bar(disease_counts.index, disease_counts.values)
plt.xticks(rotation=45)
plt.title("Disease Frequency in Dataset")
plt.xlabel("Disease")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# B) Pie Chart
plt.figure(figsize=(8,8))
plt.pie(disease_counts.values, labels=disease_counts.index, autopct='%1.1f%%')
plt.title("Disease Distribution")
plt.show()

# C) WordCloud of Symptoms
text = " ".join(df["patient_concern"].astype(str))
wc = WordCloud(width=800, height=400, background_color="white").generate(text)
plt.figure(figsize=(12,6))
plt.imshow(wc, interpolation="bilinear")
plt.axis("off")
plt.title("Common Patient Concerns WordCloud")
plt.show()

print("\nVisualisation Completed.")


# ====================================================
# 4. INTELLIGENCE MODULES
# ====================================================

# Example 1 — Emergency Level
def detect_emergency(sym):
    emergency_keywords = {
        "chest pain": "HIGH",
        "breathing difficulty": "HIGH",
        "severe headache": "MEDIUM",
        "vomiting": "MEDIUM",
        "fever": "LOW",
        "cold": "LOW"
    }
    for keyword, level in emergency_keywords.items():
        if keyword in sym:
            return level
    return "LOW"


# Example 2 — Clean multi-symptom text
def clean_input(sym):
    return sym.lower().replace(",", " ").strip()


# Example 3 — Remedies
remedies = {
    "migraine": ["drink 2L water", "reduce screen time", "sleep 8 hours"],
    "viral fever": ["take paracetamol 500mg (doctor-advised)", "drink warm water", "rest"],
    "gastritis": ["eat curd rice", "avoid spicy food", "drink ORS"],
    "food poisoning": ["ORS solution", "light khichdi", "avoid oily food"]
}


# Example 4 — Doctor Suggestion
doctor_map = {
    "dengue": "General Physician / Internal Medicine",
    "migraine": "Neurologist",
    "asthma": "Pulmonologist",
    "food poisoning": "Gastroenterologist",
    "gastritis": "Gastroenterologist",
}
def suggest_doctor(disease):
    return doctor_map.get(disease, "General Physician")


# Example 5 — Diet Plan
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


# Example 6 — Safe Prescription Template
prescription_template = {
    "viral fever": ["Paracetamol 500mg (doctor advised)", "drink warm water"],
    "gastritis": ["Gelusil (doctor advised)", "eat soft food"],
    "migraine": ["Take rest", "reduce light/sound"]
}


# ====================================================
# 5. ADVANCED CHATBOT LOOP (with CONFIDENCE SCORE)
# ====================================================

print("\n==============================")
print("      AI MEDICAL CHATBOT")
print("==============================")

while True:
    user = input("\nDescribe your symptoms (or type exit): ").lower()

    if user in ["exit", "quit", "bye"]:
        print("\nTake care! Goodbye ️")
        break

    user_clean = clean_input(user)

    # Prediction
    predicted_disease = model.predict([user_clean])[0]

    # Confidence Score
    proba = model.predict_proba([user_clean])[0]
    confidence = max(proba) * 100

    print("\n Predicted Diagnosis:", predicted_disease)
    print(f" Confidence Score: {confidence:.2f}%")


    # Emergency Level
    level = detect_emergency(user_clean)
    print(" Emergency Level:", level)


    # Remedies
    if predicted_disease in remedies:
        print("\n Home Remedies:")
        for r in remedies[predicted_disease]:
            print(" -", r)


    # Doctor Suggestion
    print("\n Doctor to Visit:", suggest_doctor(predicted_disease))


    # Diet Plan
    if predicted_disease in diet_plan:
        print("\n Diet Recommendations:")
        print(" Recommended:", ", ".join(diet_plan[predicted_disease]["recommended"]))
        print(" Avoid:", ", ".join(diet_plan[predicted_disease]["avoid"]))


    # General Advice
    if predicted_disease in prescription_template:
        print("\n General Advice (Educational Only):")
        for p in prescription_template[predicted_disease]:
            print(" -", p)

    print("\n---------------------------------------------")
