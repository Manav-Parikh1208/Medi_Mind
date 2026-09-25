from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .hospitals import get_hospital_recommendations

DISCLAIMER = (
    "This educational AI assistant provides symptom-based suggestions and differential diagnoses. "
    "It is not a certified diagnostic tool and does not replace evaluation by a licensed medical professional."
)


@dataclass
class AlternativeDiseaseData:
    name: str
    confidence: float


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
    alternative_diseases: list[dict[str, object]]
    hospital_recommendations: list[dict[str, object]]
    disclaimer: str
    created_at: str
    heart_rate: float | None = None
    average_heart_rate: int | None = None
    vital_summary: str | None = None
    vital_triage_level: str = "NORMAL"
    vital_triage_title: str = "Normal Resting Vital"
    vital_triage_message: str = "Heart rate within common resting range."
    primary_assessment: str = "Routine Symptom Assessment"
    care_action: str = "Continue with symptom guidance."
    symptom_result_is_secondary: bool = False


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
            raise ValueError(f"Dataset missing required column(s): {missing}")

        df = df.dropna(subset=["patient_concern", "diagnosis"]).copy()
        df["patient_concern"] = df["patient_concern"].astype(str).str.lower().str.strip()
        df["diagnosis"] = df["diagnosis"].astype(str).str.strip()

        self.df = df
        self.model = Pipeline(
            [
                ("tfidf", TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True, min_df=1)),
                ("clf", LogisticRegression(C=5.0, max_iter=1000, random_state=42)),
            ]
        )

        x_train, x_test, y_train, y_test = train_test_split(
            df["patient_concern"],
            df["diagnosis"],
            test_size=0.20,
            random_state=42,
            stratify=df["diagnosis"] if df["diagnosis"].nunique() > 1 else None,
        )
        self.model.fit(x_train, y_train)
        self.accuracy = float(accuracy_score(y_test, self.model.predict(x_test)))

    @staticmethod
    def clean_input(symptoms: str) -> str:
        return symptoms.lower().replace(",", " ").strip()

    @staticmethod
    def detect_emergency(symptoms: str, heart_rate: float | None = None, average_heart_rate: int | None = None) -> str:
        symptoms_lower = symptoms.lower()

        # Physiological heart rate red flags
        assessed_hr = average_heart_rate or heart_rate
        if assessed_hr is not None:
            if assessed_hr >= 120 or assessed_hr <= 45:
                return "HIGH"
            if (assessed_hr >= 100 or assessed_hr <= 55) and any(k in symptoms_lower for k in ["chest", "breath", "dizzy", "faint"]):
                return "HIGH"

        high_keywords = [
            "chest pain",
            "breathing difficulty",
            "shortness of breath",
            "heaviness in chest",
            "radiating to left arm",
            "blue lips",
            "unconscious",
            "stroke",
        ]
        medium_keywords = [
            "severe headache",
            "vomiting",
            "high fever",
            "blood in urine",
            "sharp flank pain",
            "spitting blood",
            "dizziness",
        ]

        for kw in high_keywords:
            if kw in symptoms_lower:
                return "HIGH"
        for kw in medium_keywords:
            if kw in symptoms_lower:
                return "MEDIUM"

        if assessed_hr is not None and (assessed_hr > 100 or assessed_hr < 60):
            return "MEDIUM"

        return "LOW"

    @staticmethod
    def heart_rate_summary(heart_rate: float | None, average_heart_rate: int | None) -> str:
        if heart_rate is None and average_heart_rate is None:
            return "No live heart rate feed active."
        avg_str = f" (Average: {average_heart_rate} BPM)" if average_heart_rate else ""
        hr_str = f"{heart_rate:.1f} BPM" if heart_rate else f"{average_heart_rate} BPM"
        return f"Live Heart Rate: {hr_str}{avg_str}"

    @staticmethod
    def vital_triage(
        heart_rate: float | None,
        average_heart_rate: int | None,
        symptoms: str,
    ) -> tuple[str, str, str]:
        if heart_rate is None and average_heart_rate is None:
            return (
                "UNAVAILABLE",
                "Heart-Rate Feed Inactive",
                "Connect the MAX30102 sensor feed to enable live physiological monitoring.",
            )

        assessed_rate = average_heart_rate or (int(heart_rate) if heart_rate else None)
        if assessed_rate is None:
            return ("UNAVAILABLE", "Reading Incomplete", "Awaiting stable pulse reading.")

        symptoms_lower = symptoms.lower()
        red_flags = ("chest pain", "shortness of breath", "breathing difficulty", "faint", "dizzy")
        if any(flag in symptoms_lower for flag in red_flags) and (assessed_rate > 100 or assessed_rate < 55):
            return (
                "EMERGENCY",
                "Critical Vital & Symptom Alert",
                f"Heart rate of {assessed_rate} BPM combined with acute symptoms warrants urgent emergency clinical review.",
            )

        if assessed_rate < 50 or assessed_rate > 120:
            return (
                "CLINICIAN_REVIEW",
                "Outside Typical Resting Range",
                f"Heart rate of {assessed_rate} BPM is outside the 60-100 BPM resting range. Rest quietly and arrange clinical assessment if this persists.",
            )

        if assessed_rate < 60 or assessed_rate > 100:
            return (
                "RECHECK",
                "Slightly Elevated / Low Resting Pulse",
                f"Heart rate of {assessed_rate} BPM is slightly elevated or low compared to average 60-100 BPM. Recheck after 5 minutes rest.",
            )

        return (
            "NORMAL",
            "Healthy Resting Vital Range",
            f"Heart rate of {assessed_rate} BPM is within the standard 60-100 BPM adult resting range.",
        )

    @staticmethod
    def vital_first_plan(triage_level: str) -> tuple[str, str, bool, str, str]:
        if triage_level == "EMERGENCY":
            return (
                "Urgent Vital & Symptom Assessment",
                "Seek immediate emergency medical care. Do not wait for online analysis.",
                True,
                "HIGH",
                "Emergency Department / Cardiology Center",
            )
        if triage_level == "CLINICIAN_REVIEW":
            return (
                "Physiological Vital Review Recommended",
                "Rest for 5 minutes and repeat reading. Arrange prompt clinical evaluation if heart rate stays abnormal.",
                True,
                "HIGH",
                "General Physician / Cardiology Specialist",
            )
        if triage_level == "RECHECK":
            return (
                "Recheck Vital While Resting",
                "Sit quietly for 5 minutes and take another reading to confirm resting average.",
                True,
                "MEDIUM",
                "General Physician",
            )
        return (
            "Heart Rate Supports Symptom Assessment",
            "Live heart rate is stable. Proceed with symptom diagnostic guidance.",
            False,
            "LOW",
            "",
        )

    @staticmethod
    def _lookup(mapping: dict[str, object], disease: str, default: object) -> object:
        return mapping.get(disease.lower(), default)

    def predict(
        self,
        symptoms: str,
        heart_rate: float | None = None,
        average_heart_rate: int | None = None,
    ) -> Prediction:
        clean_symptoms = self.clean_input(symptoms)

        # Include heart rate context in model input if available
        model_input = clean_symptoms
        if average_heart_rate or heart_rate:
            hr_val = average_heart_rate or int(heart_rate)
            if hr_val > 100:
                model_input += " high heart rate tachycardia pulse"
            elif hr_val < 60:
                model_input += " low heart rate bradycardia pulse"

        probabilities = self.model.predict_proba([model_input])[0]
        classes = self.model.classes_
        sorted_indices = probabilities.argsort()[::-1]

        predicted_disease = str(classes[sorted_indices[0]])
        confidence = round(float(probabilities[sorted_indices[0]] * 100), 2)

        alternative_diseases = []
        for idx in sorted_indices[1:4]:
            alt_name = str(classes[idx])
            alt_conf = round(float(probabilities[idx] * 100), 2)
            alternative_diseases.append({"name": alt_name, "confidence": alt_conf})

        remedies = {
            "migraine": ["Drink 2L water daily", "Rest in a quiet, dark room", "Apply cold compress to forehead", "Reduce screen exposure"],
            "uti": ["Drink plenty of water", "Drink unsweetened cranberry juice", "Maintain hygienic care", "Avoid caffeine and alcohol"],
            "flu": ["Rest adequately", "Drink warm broths and tea", "Take doctor-advised fever medication", "Use a humidifier"],
            "common cold": ["Hydrate frequently", "Steam inhalation", "Gargle with warm salt water", "Rest"],
            "throat infection": ["Gargle with warm salt water", "Drink honey tea", "Avoid cold liquids", "Rest voice"],
            "cardiac issue": ["Seek immediate emergency medical care", "Rest in elevated head position", "Avoid exertion"],
            "food poisoning": ["Drink ORS solution", "Follow BRAT diet", "Stay hydrated"],
            "acidity": ["Avoid spicy and fatty foods", "Eat smaller frequent meals", "Do not lie down immediately after eating"],
            "asthma": ["Use prescribed rescue inhaler", "Sit upright during breathing difficulty", "Avoid smoke triggers"],
            "diabetes": ["Monitor blood glucose", "Eat low glycemic high-fiber foods", "Stay active with routine exercise"],
            "viral fever": ["Stay hydrated", "Take paracetamol (doctor-advised)", "Cold sponging for high fever"],
            "infection": ["Rest and stay hydrated", "Monitor temperature", "Consult doctor for antibiotics"],
            "malaria": ["Consult doctor immediately for antimalarials", "Stay hydrated", "Rest"],
            "allergy": ["Identify and avoid allergen trigger", "Take prescribed antihistamines", "Apply calming lotion"],
            "blood pressure issue": ["Limit sodium intake", "Practice deep breathing", "Consult physician for medication adjustment"],
            "arthritis": ["Gentle joint exercises", "Apply warm/cold therapy", "Maintain healthy weight"],
            "dengue": ["Drink abundant fluids (ORS, coconut water)", "Monitor platelet count", "Avoid NSAIDs like ibuprofen"],
            "typhoid": ["Drink boiled/filtered water", "Eat easily digestible soft foods", "Complete antibiotic course"],
            "pneumonia": ["Consult doctor immediately", "Use steam inhalation", "Get adequate rest and oxygen care"],
            "kidney stone": ["Drink 3-4 liters of water daily", "Take doctor-advised pain reliever", "Avoid excessive sodium"],
            "gastroenteritis": ["Sip ORS fluid continuously", "Eat bland soft diet", "Avoid dairy and oily foods"],
        }

        doctor_map = {
            "dengue": "General Physician / Infectious Disease Specialist",
            "malaria": "General Physician / Internal Medicine Specialist",
            "typhoid": "General Physician / Gastroenterologist",
            "migraine": "Neurologist / Pain Specialist",
            "asthma": "Pulmonologist / Chest Specialist",
            "pneumonia": "Pulmonologist / Critical Care Specialist",
            "food poisoning": "Gastroenterologist",
            "acidity": "Gastroenterologist",
            "gastroenteritis": "Gastroenterologist",
            "cardiac issue": "Cardiologist / Emergency Physician",
            "blood pressure issue": "Cardiologist / Internal Medicine Specialist",
            "diabetes": "Endocrinologist / Diabetologist",
            "uti": "Urologist / Nephrologist",
            "kidney stone": "Urologist",
            "arthritis": "Rheumatologist / Orthopedic Specialist",
            "allergy": "Dermatologist / Allergist",
            "common cold": "General Physician / ENT Specialist",
            "throat infection": "ENT Specialist / General Physician",
            "flu": "General Physician",
            "infection": "General Physician / Infectious Disease Specialist",
        }

        diet_plan = {
            "gastritis": {"recommended": ["Curd rice", "Boiled oats", "Bananas"], "avoid": ["Spicy food", "Coffee", "Alcohol"]},
            "acidity": {"recommended": ["Cold milk", "Oatmeal", "Melons"], "avoid": ["Citrus fruits", "Fried snacks", "Soft drinks"]},
            "viral fever": {"recommended": ["Warm vegetable soup", "Khichdi", "Coconut water"], "avoid": ["Cold beverages", "Oily food"]},
            "food poisoning": {"recommended": ["ORS", "Boiled potatoes", "Clear broth"], "avoid": ["Dairy", "Raw vegetables", "Fatty meals"]},
            "diabetes": {"recommended": ["Leafy greens", "Whole grains", "Lean protein"], "avoid": ["Refined sugar", "Processed carbs", "Soda"]},
            "dengue": {"recommended": ["Papaya leaf extract", "Coconut water", "Fresh fruit juices"], "avoid": ["Heavy oily meals", "Dark colored foods"]},
            "kidney stone": {"recommended": ["Water", "Lemonade", "Watermelon"], "avoid": ["Spinach", "Excess salt", "Nuts"]},
        }

        general_advice = {
            "viral fever": ["Consult a doctor if fever exceeds 102F or lasts over 3 days.", "Monitor hydration."],
            "dengue": ["Get complete blood count (CBC) to monitor platelet levels.", "Watch for bleeding signs."],
            "pneumonia": ["Seek urgent emergency care if breathlessness worsens."],
            "cardiac issue": ["Call emergency medical services immediately for acute chest compression."],
            "kidney stone": ["Filter urine to capture stone if instructed by urologist."],
            "gastritis": ["Eat smaller meals more frequently throughout the day."],
        }

        triage_level, triage_title, triage_message = self.vital_triage(
            heart_rate, average_heart_rate, clean_symptoms
        )
        primary_assessment, care_action, symptom_secondary, vital_emergency_level, vital_doctor = self.vital_first_plan(
            triage_level
        )
        symptom_emergency_level = self.detect_emergency(clean_symptoms, heart_rate, average_heart_rate)

        emergency_level = "HIGH" if "HIGH" in (symptom_emergency_level, vital_emergency_level) else (
            "MEDIUM" if "MEDIUM" in (symptom_emergency_level, vital_emergency_level) else "LOW"
        )

        hospitals = get_hospital_recommendations(predicted_disease)

        result = Prediction(
            id=len(self.history) + 1,
            symptoms=symptoms.strip(),
            predicted_disease=predicted_disease,
            confidence=confidence,
            emergency_level=emergency_level,
            doctor_recommendation=vital_doctor or str(self._lookup(doctor_map, predicted_disease, "General Physician")),
            explanation=(
                f"The AI model analyzed your symptom description and vital metrics against diagnostic feature matrices "
                f"and identified '{predicted_disease}' as the primary match with {confidence}% probability."
            ),
            remedies=list(self._lookup(remedies, predicted_disease, ["Consult a qualified medical specialist."])),
            diet_plan=diet_plan.get(predicted_disease.lower()),
            general_advice=list(self._lookup(general_advice, predicted_disease, ["Follow doctor's instructions closely."])),
            alternative_diseases=alternative_diseases,
            hospital_recommendations=hospitals,
            disclaimer=DISCLAIMER,
            created_at=datetime.now(timezone.utc).isoformat(),
            heart_rate=heart_rate,
            average_heart_rate=average_heart_rate,
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

    def add_feedback(self, symptoms: str, user_corrected_disease: str) -> dict[str, object]:
        clean_symptoms = self.clean_input(symptoms)
        corrected = user_corrected_disease.strip()

        new_row = pd.DataFrame([{"patient_concern": clean_symptoms, "diagnosis": corrected}])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.df.to_csv(self.dataset_path, index=False)

        self.model.fit(self.df["patient_concern"], self.df["diagnosis"])

        x_train, x_test, y_train, y_test = train_test_split(
            self.df["patient_concern"],
            self.df["diagnosis"],
            test_size=0.20,
            random_state=42,
        )
        self.accuracy = float(accuracy_score(y_test, self.model.predict(x_test)))

        return {
            "message": f"Thank you! Your feedback for '{corrected}' was saved and the model was retrained.",
            "updated_accuracy": round(self.accuracy * 100, 2),
            "total_records": int(len(self.df)),
            "total_diseases": int(self.df["diagnosis"].nunique()),
        }

    def stats(self) -> dict[str, object]:
        top_diseases = [
            {"name": str(name), "count": int(count)}
            for name, count in self.df["diagnosis"].value_counts().head(10).items()
        ]
        available_diseases = sorted([str(d) for d in self.df["diagnosis"].unique()])

        return {
            "accuracy": round(self.accuracy * 100, 2),
            "total_records": int(len(self.df)),
            "total_diseases": int(self.df["diagnosis"].nunique()),
            "available_diseases": available_diseases,
            "top_diseases": top_diseases,
            "recent_predictions": [prediction.__dict__ for prediction in self.history[:8]],
        }
