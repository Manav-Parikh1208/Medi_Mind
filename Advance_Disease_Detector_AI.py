# ====================================================
#      ADVANCED AI MEDICAL CHATBOT + DASHBOARD
# ====================================================

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score


def load_model():
    df = pd.read_csv("patient_symptoms_textual.csv")
    df.columns = df.columns.str.lower().str.strip()
    df = df.dropna(subset=["patient_concern", "diagnosis"])
    df["patient_concern"] = df["patient_concern"].astype(str).str.lower().str.strip()

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True)),
        ("clf", LogisticRegression(C=5.0, max_iter=1000, random_state=42))
    ])

    X = df["patient_concern"]
    y = df["diagnosis"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    return df, model, acc


df, model, accuracy = load_model()

print("\n====================================================")
print(" MEDI MIND MODEL TRAINED SUCCESSFULLY")
print(f" Accuracy: {accuracy * 100:.2f}% | Total Dataset Records: {len(df)}")
print("====================================================\n")

# Emergency Level
def detect_emergency(sym):
    sym_lower = sym.lower()
    high_kws = ["chest pain", "breathing difficulty", "shortness of breath", "unconscious"]
    med_kws = ["severe headache", "vomiting", "high fever", "blood in urine", "flank pain"]
    for kw in high_kws:
        if kw in sym_lower:
            return "HIGH"
    for kw in med_kws:
        if kw in sym_lower:
            return "MEDIUM"
    return "LOW"

# Doctor Map
doctor_map = {
    "dengue": "General Physician / Infectious Disease Specialist",
    "malaria": "General Physician / Internal Medicine",
    "migraine": "Neurologist",
    "asthma": "Pulmonologist",
    "pneumonia": "Pulmonologist",
    "food poisoning": "Gastroenterologist",
    "acidity": "Gastroenterologist",
    "cardiac issue": "Cardiologist",
    "uti": "Urologist",
    "kidney stone": "Urologist",
    "arthritis": "Rheumatologist",
    "allergy": "Dermatologist",
}

# Hospital Recommendations
hospitals_db = {
    "cardiac issue": ["Apollo Heart Institute (1.8 km • 24/7 ER)", "Fortis Cardiac Care (3.2 km • ICU)", "Max Speciality Heart Center (4.5 km)"],
    "migraine": ["City Neuro Care Institute (2.1 km • MRI)", "Medanta Neuro Center (3.8 km)", "Manipal Brain Clinic (4.2 km)"],
    "food poisoning": ["Global Gastroenterology Institute (1.5 km)", "Apollo Digestive Care (2.9 km)", "Sunshine Gastro Hospital (4.0 km)"],
    "acidity": ["Global Gastroenterology Institute (1.5 km)", "Apollo Digestive Care (2.9 km)", "Sunshine Gastro Hospital (4.0 km)"],
    "asthma": ["National Chest & Lung Institute (2.3 km)", "Fortis Pulmonary Care (3.5 km)", "City Respiratory Care (4.8 km)"],
    "pneumonia": ["National Chest & Lung Institute (2.3 km)", "Fortis Pulmonary Care (3.5 km)", "City Respiratory Care (4.8 km)"],
    "uti": ["Specialty Urology & Kidney Center (2.0 km)", "Apex Nephrology Hospital (3.4 km)", "Sunrise Urology Clinic (5.0 km)"],
    "kidney stone": ["Specialty Urology & Kidney Center (2.0 km)", "Apex Nephrology Hospital (3.4 km)", "Sunrise Urology Clinic (5.0 km)"],
    "dengue": ["St. Jude Multi-Specialty Fever Hospital (1.9 km)", "Care Infectious Disease Hospital (3.1 km)", "Lifeline Emergency Hospital (4.4 km)"],
    "malaria": ["St. Jude Multi-Specialty Fever Hospital (1.9 km)", "Care Infectious Disease Hospital (3.1 km)", "Lifeline Emergency Hospital (4.4 km)"],
    "arthritis": ["Bone & Joint Specialty Institute (2.4 km)", "Apollo Orthopedic Center (3.7 km)", "City Joint Care Clinic (4.6 km)"],
    "allergy": ["Skin & Allergy Specialty Institute (1.6 km)", "Fortis Dermatology Care (3.0 km)", "Apex Medical Center (4.1 km)"],
}

print("====================================================")
print("          ADVANCED AI MEDICAL CHATBOT")
print("====================================================")

while True:
    user = input("\nDescribe your symptoms (or type 'exit' to quit): ").strip()
    if user.lower() in ["exit", "quit", "bye"]:
        print("\nThank you for using Medi Mind! Stay healthy and goodbye.")
        break

    if len(user.split()) < 2:
        print("Please describe your symptoms in more detail.")
        continue

    # Predict main disease and probabilities
    probs = model.predict_proba([user.lower()])[0]
    classes = model.classes_
    top_idxs = probs.argsort()[::-1]

    main_disease = classes[top_idxs[0]]
    main_conf = probs[top_idxs[0]] * 100

    print(f"\n Primary Predicted Diagnosis: {main_disease}")
    print(f" Confidence Score: {main_conf:.2f}%")
    print(f" Emergency Level: {detect_emergency(user)}")
    print(f" Recommended Specialist: {doctor_map.get(main_disease.lower(), 'General Physician')}")

    # Top 3 Alternative Differential Diagnoses
    print("\n Top Alternative Differential Diagnoses (Survey):")
    for i in range(1, min(4, len(top_idxs))):
        alt = classes[top_idxs[i]]
        alt_p = probs[top_idxs[i]] * 100
        print(f"   {i}. {alt} ({alt_p:.2f}%)")

    # Recommended Nearest Hospitals
    rec_hospitals = hospitals_db.get(main_disease.lower(), ["St. Jude Multi-Specialty Fever Hospital (1.9 km)", "Care Infectious Hospital (3.1 km)", "Lifeline Emergency Hospital (4.4 km)"])
    print("\n Recommended Nearest Specialty Hospitals:")
    for h in rec_hospitals:
        print(f"   • {h}")

    # Feedback / Accuracy Survey
    print("\n Is this diagnosis correct?")
    feedback = input(" Type 'yes' or enter correct disease name to train model: ").strip()
    if feedback and feedback.lower() != "yes":
        new_row = pd.DataFrame([{"patient_concern": user.lower(), "diagnosis": feedback.strip()}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv("patient_symptoms_textual.csv", index=False)
        df, model, accuracy = load_model()
        print(f" Thank you! Model retrained with feedback. New dataset count: {len(df)} | Updated Accuracy: {accuracy*100:.2f}%")
    else:
        print(" Thank you for confirming!")

    print("\n----------------------------------------------------")
