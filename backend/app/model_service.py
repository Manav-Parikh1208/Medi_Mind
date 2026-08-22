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
    heart_rate: float | None
    vital_summary: str | None
    vital_triage_level: str | None
    vital_triage_title: str | None
    vital_triage_message: str | None
    primary_assessment: str | None
    care_action: str | None
    symptom_result_is_secondary: bool


class DiseaseModelService:
    def __init__(self, dataset_path: Path, supplemental_dataset_path: Path | None = None) -> None:
        self.dataset_path = dataset_path
        self.supplemental_dataset_path = supplemental_dataset_path
        self.history: list[Prediction] = []
        self._load_and_train()

    def _load_and_train(self) -> None:
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")

        primary_df = pd.read_csv(self.dataset_path)
        primary_df.columns = primary_df.columns.str.lower().str.strip()

        required_columns = {"patient_concern", "diagnosis"}
        missing_columns = required_columns.difference(primary_df.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Dataset is missing required column(s): {missing}")

        primary_df = primary_df.dropna(subset=["patient_concern", "diagnosis"])[["patient_concern", "diagnosis"]].copy()
        primary_df["source"] = "project dataset"
        self.duplicate_rows_removed = int(
            len(primary_df) - len(primary_df.drop_duplicates(subset=["patient_concern", "diagnosis"]))
        )

        frames = [primary_df]
        if self.supplemental_dataset_path and self.supplemental_dataset_path.exists():
            supplemental_df = pd.read_csv(self.supplemental_dataset_path)
            supplemental_df.columns = supplemental_df.columns.str.lower().str.strip()
            if {"text", "label"}.issubset(supplemental_df.columns):
                supplemental_df = supplemental_df[["text", "label"]].rename(
                    columns={"text": "patient_concern", "label": "diagnosis"}
                )
                supplemental_df["source"] = "Symptom2Disease (Apache-2.0)"
                frames.append(supplemental_df)

        df = pd.concat(frames, ignore_index=True)
        df = df.dropna(subset=["patient_concern", "diagnosis"]).copy()
        df["patient_concern"] = df["patient_concern"].astype(str).str.lower().str.strip()
        df["diagnosis"] = df["diagnosis"].astype(str).str.strip()
        df = df.drop_duplicates(subset=["patient_concern", "diagnosis"]).reset_index(drop=True)

        self.df = df
        self.model = Pipeline(
            [
                ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
                ("clf", MultinomialNB(alpha=0.35)),
            ]
        )

        x_train, x_test, y_train, y_test = train_test_split(
            df["patient_concern"],
            df["diagnosis"],
            test_size=0.20,
            random_state=42,
            stratify=df["diagnosis"],
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

    @staticmethod
    def heart_rate_summary(heart_rate: float | None, average_heart_rate: float | None) -> str | None:
        if heart_rate is None:
            return "Heart rate was unavailable; the prediction uses symptom text only."
        average_text = f" (rolling average {average_heart_rate:.0f} BPM)" if average_heart_rate else ""
        return f"Live reading: {heart_rate:.0f} BPM{average_text}."

    @staticmethod
    def vital_triage(heart_rate: float | None, average_heart_rate: float | None, symptoms: str) -> tuple[str, str, str]:
        if heart_rate is None:
            return ("UNAVAILABLE", "Live vital required", "Connect the ESP32/MAX30102 and obtain a stable reading before continuing.")

        assessed_rate = average_heart_rate or heart_rate
        red_flags = ("chest pain", "shortness of breath", "breathing difficulty", "faint", "fainted", "passing out")
        if any(flag in symptoms for flag in red_flags):
            return ("EMERGENCY", "Urgent symptoms reported", "Seek emergency care now for these symptoms; do not rely on this sensor or website to rule out a serious condition.")
        if assessed_rate < 50 or assessed_rate > 120:
            return ("CLINICIAN_REVIEW", "Outside a typical resting range", "Sit quietly and repeat the measurement. If this persists, or you feel unwell, contact a clinician promptly. Athletes and some medicines can affect resting heart rate.")
        if assessed_rate < 60 or assessed_rate > 100:
            return ("RECHECK", "Recheck while resting", "This is outside the common 60–100 BPM adult resting range. Rest for five minutes, keep your finger still, then measure again.")
        return ("NORMAL", "Within a common resting range", "This reading is within the common 60–100 BPM adult resting range when you are calm and at rest. It does not diagnose or exclude any condition.")

    @staticmethod
    def vital_first_plan(triage_level: str) -> tuple[str, str, bool, str, str]:
        """Make the physiological measurement control the primary care outcome."""
        if triage_level == "EMERGENCY":
            return (
                "Urgent symptom and vital assessment",
                "Seek emergency care now. Do not wait for an online prediction or repeat sensor readings.",
                True,
                "HIGH",
                "Emergency services / emergency department",
            )
        if triage_level == "CLINICIAN_REVIEW":
            return (
                "Heart-rate review is the primary outcome",
                "Rest for five minutes and repeat the reading. If it remains outside range, or you feel unwell, arrange prompt clinical assessment.",
                True,
                "HIGH",
                "General Physician / Cardiology assessment",
            )
        if triage_level == "RECHECK":
            return (
                "Repeat the vital measurement before relying on the symptom result",
                "Sit quietly for five minutes, keep the finger still, and take another stable reading. Use the symptom result only as secondary educational context.",
                True,
                "MEDIUM",
                "General Physician if the reading remains outside range or symptoms continue",
            )
        return (
            "Heart rate supports routine symptom assessment",
            "The stable vital does not add an urgent heart-rate action. Continue with symptom-based educational guidance.",
            False,
            "LOW",
            "",
        )

    def predict(
        self,
        symptoms: str,
        heart_rate: float | None = None,
        average_heart_rate: float | None = None,
    ) -> Prediction:
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
        triage_level, triage_title, triage_message = self.vital_triage(
            heart_rate,
            average_heart_rate,
            clean_symptoms,
        )
        primary_assessment, care_action, symptom_secondary, vital_emergency_level, vital_doctor = self.vital_first_plan(
            triage_level
        )
        symptom_emergency_level = self.detect_emergency(clean_symptoms)
        emergency_level = "HIGH" if "HIGH" in (symptom_emergency_level, vital_emergency_level) else (
            "MEDIUM" if "MEDIUM" in (symptom_emergency_level, vital_emergency_level) else "LOW"
        )
        result = Prediction(
            id=len(self.history) + 1,
            symptoms=symptoms.strip(),
            predicted_disease=predicted_disease,
            confidence=confidence,
            emergency_level=emergency_level,
            doctor_recommendation=vital_doctor or str(self._lookup(doctor_map, predicted_disease, "General Physician")),
            explanation=(
                f"The model compared your symptom description with learned symptom patterns "
                f"and found the closest match to {predicted_disease}."
            ),
            remedies=list(self._lookup(remedies, predicted_disease, [])),
            diet_plan=diet_plan.get(disease_key),
            general_advice=list(self._lookup(general_advice, predicted_disease, [])),
            disclaimer=DISCLAIMER,
            created_at=datetime.now(timezone.utc).isoformat(),
            heart_rate=heart_rate,
            vital_summary=self.heart_rate_summary(heart_rate, average_heart_rate),
            vital_triage_level=triage_level,
            vital_triage_title=triage_title,
            vital_triage_message=triage_message,
            primary_assessment=primary_assessment,
            care_action=care_action,
            symptom_result_is_secondary=symptom_secondary,
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
            "training_sources": sorted(self.df["source"].unique().tolist()),
            "duplicate_rows_removed": self.duplicate_rows_removed,
        }
