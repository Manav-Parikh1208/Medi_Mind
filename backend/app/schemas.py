from __future__ import annotations
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    symptoms: str = Field(..., min_length=8, max_length=1200)
    patient_name: str | None = Field(default=None, max_length=80)
    age: int | None = Field(default=None, ge=1, le=120)
    sex: str | None = Field(default=None, max_length=40)
    symptom_group: str | None = Field(default=None, max_length=120)
    symptom_duration: str | None = Field(default=None, max_length=80)
    severity: str | None = Field(default=None, max_length=40)
    pre_existing_conditions: list[str] = Field(default_factory=list, max_length=10)
    heart_rate: float | None = Field(default=None, ge=30, le=220)
    average_heart_rate: int | None = Field(default=None, ge=30, le=220)
    image_filename: str | None = Field(default=None, max_length=255)


class DietPlan(BaseModel):
    recommended: list[str]
    avoid: list[str]


class AlternativeDisease(BaseModel):
    name: str
    confidence: float


class HospitalRecommendation(BaseModel):
    name: str
    specialty: str
    distance: str
    rating: float
    emergency_24x7: bool
    phone: str
    address: str
    map_url: str
    services: list[str]


class PredictionResponse(BaseModel):
    id: int
    symptoms: str
    predicted_disease: str
    confidence: float
    emergency_level: str
    doctor_recommendation: str
    explanation: str
    remedies: list[str]
    diet_plan: DietPlan | None
    general_advice: list[str]
    alternative_diseases: list[AlternativeDisease]
    hospital_recommendations: list[HospitalRecommendation]
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


class VitalsResponse(BaseModel):
    state: str
    message: str
    heart_rate: float | None = None
    average_heart_rate: int | None = None
    active_port: str = "COM3"
    available_ports: list[str] = Field(default_factory=list)
    vital_triage_level: str = "NORMAL"
    vital_triage_title: str = "Normal Resting Vital"
    vital_triage_message: str = "Heart rate within normal range."
    updated_at: str | None = None


class FeedbackRequest(BaseModel):
    prediction_id: int | None = None
    symptoms: str = Field(..., min_length=5)
    predicted_disease: str
    user_corrected_disease: str
    is_correct: bool = True
    comments: str | None = None


class FeedbackResponse(BaseModel):
    message: str
    updated_accuracy: float
    total_records: int
    total_diseases: int


class StatsResponse(BaseModel):
    accuracy: float
    total_records: int
    total_diseases: int
    available_diseases: list[str]
    top_diseases: list[dict[str, int | str]]
    recent_predictions: list[PredictionResponse]
