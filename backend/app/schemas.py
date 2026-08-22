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
    image_filename: str | None = Field(default=None, max_length=255)
    heart_rate: float | None = Field(default=None, ge=20, le=255)
    average_heart_rate: float | None = Field(default=None, ge=20, le=255)


class DietPlan(BaseModel):
    recommended: list[str]
    avoid: list[str]


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
    disclaimer: str
    created_at: str
    heart_rate: float | None = None
    vital_summary: str | None = None
    vital_triage_level: str | None = None
    vital_triage_title: str | None = None
    vital_triage_message: str | None = None
    primary_assessment: str | None = None
    care_action: str | None = None
    symptom_result_is_secondary: bool = False


class VitalsResponse(BaseModel):
    state: str
    message: str
    heart_rate: float | None = None
    average_heart_rate: int | None = None
    updated_at: str | None = None
    vital_triage_level: str | None = None
    vital_triage_title: str | None = None
    vital_triage_message: str | None = None


class StatsResponse(BaseModel):
    accuracy: float
    total_records: int
    total_diseases: int
    top_diseases: list[dict[str, int | str]]
    recent_predictions: list[PredictionResponse]
    training_sources: list[str] = []
    duplicate_rows_removed: int = 0
