import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

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

print(f"Model Accuracy: {accuracy_score(y_test, model.predict(X_test)) * 100:.2f}%")
print("\n===== ADVANCED AI SYMPTOM CHECKER =====\n")

while True:
    user = input("\nDescribe symptoms (or type exit): ").strip()
    if user.lower() in ["exit", "quit", "bye"]:
        break
    probs = model.predict_proba([user.lower()])[0]
    classes = model.classes_
    top_idxs = probs.argsort()[::-1]

    print("\n Primary Predicted Diagnosis:", classes[top_idxs[0]], f"({probs[top_idxs[0]]*100:.1f}%)")
    print(" Alternative Differential Diagnoses:")
    for i in range(1, min(4, len(top_idxs))):
        print(f"   {i}. {classes[top_idxs[i]]} ({probs[top_idxs[i]]*100:.1f}%)")
