from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .model_service import DiseaseModelService
from .schemas import PredictionRequest, PredictionResponse, StatsResponse


ROOT_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT_DIR / "patient_symptoms_textual.csv"

app = FastAPI(
    title="Medi Mind API",
    description="Disease prediction API powered by TF-IDF and Multinomial Naive Bayes.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):517\d",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_service = DiseaseModelService(DATASET_PATH)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    symptoms = payload.symptoms.strip()
    if len(symptoms.split()) < 3:
        raise HTTPException(
            status_code=422,
            detail="Please describe at least three symptom words for a meaningful prediction.",
        )

    model_input = " ".join(
        part
        for part in [
            payload.symptom_group,
            symptoms,
            payload.symptom_duration,
            payload.severity,
        ]
        if part
    )
    prediction = model_service.predict(model_input)
    return PredictionResponse(**prediction.__dict__)


@app.get("/api/stats", response_model=StatsResponse)
def stats() -> StatsResponse:
    return StatsResponse(**model_service.stats())
