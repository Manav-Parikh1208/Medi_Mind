from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


DISCLAIMER = (
    "This educational AI assistant is not a certified diagnostic tool and does not "
    "replace care from a licensed medical professional."
)


@dataclass
class Prediction:
    id: int
    symptoms: str
    predicted_disease: str
    confidence: float
    emergency_level: str
    doctor_recommendation: str
    explanation: str
    remedies: list[str]
    diet_plan: dict[str, list[str]] | None
    general_advice: list[str]
    disclaimer: str
    created_at: str


class DiseaseModelService:
    def __init__(self, dataset_path: Path) -> None:
        self.dataset_path = dataset_path
        self.history: list[Prediction] = []
        self._load_and_train()

    def _load_and_train(self) -> None:
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")

        df = pd.read_csv(self.dataset_path)
        df.columns = df.columns.str.lower().str.strip()

        required_columns = {"patient_concern", "diagnosis"}
        missing_columns = required_columns.difference(df.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Dataset is missing required column(s): {missing}")

        df = df.dropna(subset=["patient_concern", "diagnosis"]).copy()
        df["patient_concern"] = df["patient_concern"].astype(str).str.lower().str.strip()
        df["diagnosis"] = df["diagnosis"].astype(str).str.strip()

        self.df = df
        self.model = Pipeline(
            [
                ("tfidf", TfidfVectorizer()),
                ("clf", MultinomialNB()),
            ]
        )

        x_train, x_test, y_train, y_test = train_test_split(
            df["patient_concern"],
            df["diagnosis"],
            test_size=0.20,
            random_state=42,
        )
        self.model.fit(x_train, y_train)
        self.accuracy = float(accuracy_score(y_test, self.model.predict(x_test)))

    @staticmethod
    def clean_input(symptoms: str) -> str:
        return symptoms.lower().replace(",", " ").strip()

    @staticmethod
    def detect_emergency(symptoms: str) -> str:
        emergency_keywords = {
            "chest pain": "HIGH",
            "breathing difficulty": "HIGH",
            "shortness of breath": "HIGH",
            "severe headache": "MEDIUM",
            "vomiting": "MEDIUM",
            "high fever": "MEDIUM",
            "fever": "LOW",
            "cold": "LOW",
        }

        for keyword, level in emergency_keywords.items():
            if keyword in symptoms:
                return level
        return "LOW"

    @staticmethod
    def _lookup(mapping: dict[str, object], disease: str, default: object) -> object:
        return mapping.get(disease.lower(), default)

    def predict(self, symptoms: str) -> Prediction:
        clean_symptoms = self.clean_input(symptoms)
        predicted_disease = str(self.model.predict([clean_symptoms])[0])
        probabilities = self.model.predict_proba([clean_symptoms])[0]
        confidence = round(float(max(probabilities) * 100), 2)

        remedies = {
            "migraine": ["Drink water regularly", "Rest in a quiet, dim room", "Reduce screen exposure"],
            "viral fever": ["Rest and hydrate", "Use doctor-advised fever care", "Monitor temperature"],
            "gastritis": ["Choose bland foods", "Avoid spicy meals", "Eat smaller portions"],
            "food poisoning": ["Use ORS for hydration", "Eat light food", "Avoid oily food"],
            "common cold": ["Hydrate well", "Use steam inhalation if comfortable", "Rest"],
            "flu": ["Rest", "Drink warm fluids", "Track fever and breathing symptoms"],
            "asthma": ["Avoid known triggers", "Use prescribed inhaler plan", "Seek help if breathing worsens"],
        }
        doctor_map = {
            "dengue": "General Physician / Internal Medicine",
            "migraine": "Neurologist",
            "asthma": "Pulmonologist",
            "food poisoning": "Gastroenterologist",
            "gastritis": "Gastroenterologist",
            "cardiac issue": "Cardiologist",
            "diabetes": "Endocrinologist",
            "uti": "Urologist / General Physician",
            "arthritis": "Rheumatologist / Orthopedist",
        }
        diet_plan = {
            "gastritis": {"recommended": ["Curd rice", "Boiled vegetables"], "avoid": ["Spicy food", "Coffee"]},
            "viral fever": {"recommended": ["Warm soup", "Khichdi"], "avoid": ["Cold drinks"]},
            "food poisoning": {"recommended": ["ORS", "Boiled potatoes"], "avoid": ["Street food", "Milk"]},
            "diabetes": {"recommended": ["High-fiber meals", "Balanced protein"], "avoid": ["Sugary drinks"]},
        }
        general_advice = {
            "viral fever": ["Consult a clinician if fever persists", "Stay hydrated"],
            "gastritis": ["Avoid late heavy meals", "Ask a doctor before taking antacids frequently"],
            "migraine": ["Track triggers", "Seek care for sudden or unusual headache"],
            "cardiac issue": ["Seek urgent care for chest pain or breathlessness"],
        }

        disease_key = predicted_disease.lower()
        result = Prediction(
            id=len(self.history) + 1,
            symptoms=symptoms.strip(),
            predicted_disease=predicted_disease,
            confidence=confidence,
            emergency_level=self.detect_emergency(clean_symptoms),
            doctor_recommendation=str(self._lookup(doctor_map, predicted_disease, "General Physician")),
            explanation=(
                f"The model compared your symptom description with learned symptom patterns "
                f"and found the closest match to {predicted_disease}."
            ),
            remedies=list(self._lookup(remedies, predicted_disease, [])),
            diet_plan=diet_plan.get(disease_key),
            general_advice=list(self._lookup(general_advice, predicted_disease, [])),
            disclaimer=DISCLAIMER,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.history.insert(0, result)
        self.history = self.history[:25]
        return result

    def stats(self) -> dict[str, object]:
        top_diseases = [
            {"name": str(name), "count": int(count)}
            for name, count in self.df["diagnosis"].value_counts().head(8).items()
        ]
        return {
            "accuracy": round(self.accuracy * 100, 2),
            "total_records": int(len(self.df)),
            "total_diseases": int(self.df["diagnosis"].nunique()),
            "top_diseases": top_diseases,
            "recent_predictions": [prediction.__dict__ for prediction in self.history[:8]],
        }
