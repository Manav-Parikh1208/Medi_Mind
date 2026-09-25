from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .model_service import DiseaseModelService
from .schemas import (
    FeedbackRequest,
    FeedbackResponse,
    PredictionRequest,
    PredictionResponse,
    StatsResponse,
    VitalsResponse,
)
from .sensor_service import Esp32VitalsService

ROOT_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT_DIR / "patient_symptoms_textual.csv"

app = FastAPI(
    title="Medi Mind Advanced AI & Vitals API",
    description="Symptom-based disease prediction API with live MAX30102 heart rate tracking, vital triage, nearest hospital recommendations, and dynamic survey retraining.",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):517\d",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_service = DiseaseModelService(DATASET_PATH)
vitals_service = Esp32VitalsService()


@app.on_event("startup")
def start_vitals() -> None:
    vitals_service.start()


@app.on_event("shutdown")
def stop_vitals() -> None:
    vitals_service.stop()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "accuracy": f"{model_service.accuracy * 100:.2f}%"}


@app.get("/api/vitals", response_model=VitalsResponse)
def get_vitals() -> VitalsResponse:
    snapshot = vitals_service.snapshot()
    triage_level, triage_title, triage_message = model_service.vital_triage(
        snapshot.heart_rate,
        snapshot.average_heart_rate,
        "",
    )
    return VitalsResponse(
        **snapshot.__dict__,
        vital_triage_level=triage_level,
        vital_triage_title=triage_title,
        vital_triage_message=triage_message,
    )


@app.post("/api/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    symptoms = payload.symptoms.strip()
    if len(symptoms.split()) < 3:
        raise HTTPException(
            status_code=422,
            detail="Please describe at least three symptom words for a meaningful diagnostic prediction.",
        )

    model_input = " ".join(
        part
        for part in [
            payload.symptom_group,
            symptoms,
            payload.symptom_duration,
            payload.severity,
            " ".join(payload.pre_existing_conditions) if payload.pre_existing_conditions else None,
        ]
        if part
    )
    prediction = model_service.predict(
        model_input,
        heart_rate=payload.heart_rate,
        average_heart_rate=payload.average_heart_rate,
    )
    return PredictionResponse(**prediction.__dict__)


@app.post("/api/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    if not payload.symptoms or not payload.user_corrected_disease:
        raise HTTPException(status_code=422, detail="Symptoms and corrected disease label are required.")

    result = model_service.add_feedback(
        symptoms=payload.symptoms,
        user_corrected_disease=payload.user_corrected_disease,
    )
    return FeedbackResponse(**result)


@app.get("/api/stats", response_model=StatsResponse)
def stats() -> StatsResponse:
    return StatsResponse(**model_service.stats())
