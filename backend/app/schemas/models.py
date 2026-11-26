from typing import Literal
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    ocr_engine: str
    classifier_status: str


class CreateSessionRequest(BaseModel):
    application_type: str = Field(default="General Application", min_length=1, max_length=100)


class SessionSummary(BaseModel):
    id: str
    application_type: str
    created_at: str
    document_count: int = 0
    report_count: int = 0
    readiness_score: float | None = None


class DashboardStatsResponse(BaseModel):
    total_sessions: int
    total_documents: int
    total_reports: int
    sessions: list[SessionSummary]


class QualityMetric(BaseModel):
    width: int
    height: int
    blur_score: float
    brightness: float
    contrast: float
    warnings: list[str]
    is_readable: bool
    explanation: str


class ExtractedFieldSchema(BaseModel):
    field_name: str
    value: str
    confidence: float | None = None
    status: Literal["extracted", "Needs review", "corrected", "not_detected"]


class ClassificationResult(BaseModel):
    status: Literal["trained", "demo_mode"]
    predicted_category: str | None = None
    confidence: float | None = None
    model_version: str | None = None
    message: str
    selected_category: str


class AnomalyResult(BaseModel):
    status: Literal["not_configured", "evaluated"]
    label: str
    score: float | None = None
    explanation: str
    heatmap_base64: str | None = None


class DocumentResponse(BaseModel):
    id: str
    session_id: str
    original_filename: str
    mime_type: str
    size_bytes: int
    uploaded_at: str
    preview_url: str | None = None
    classification: ClassificationResult
    ocr_text: str
    ocr_error: str | None = None
    ocr_engine: str | None = None
    fields: list[ExtractedFieldSchema]
    quality: QualityMetric | None = None
    anomaly: AnomalyResult
    analyzed: bool


class FieldCorrectionItem(BaseModel):
    field_name: str = Field(min_length=1, max_length=64)
    value: str = Field(max_length=500)


class UpdateDocumentRequest(BaseModel):
    selected_category: str = Field(min_length=1, max_length=80)
    fields: list[FieldCorrectionItem] = Field(default_factory=list)


class CompareRequest(BaseModel):
    field_names: list[str] = Field(min_length=1)
    fuzzy_threshold: float = Field(default=0.85, ge=0.5, le=1.0)


class ComparedDocValue(BaseModel):
    document_id: str
    document_name: str
    original_value: str
    normalized_value: str


class FieldComparisonRow(BaseModel):
    field_name: str
    values: list[ComparedDocValue]
    status: Literal["Match", "Mismatch", "Near-match", "Missing", "Not detected"]
    similarity: float | None = None
    explanation: str


class CompareResponse(BaseModel):
    comparisons: list[FieldComparisonRow]


class ChecklistItem(BaseModel):
    category: str
    label: str
    required: bool
    status: Literal["Present", "Missing", "Needs review"]
    matched_documents: list[str]


class ScoreCriterion(BaseModel):
    name: str
    weight: float
    earned: float | None = None
    status: Literal["assessed", "Not assessed"]
    explanation: str


class ReadinessResponse(BaseModel):
    score_label: str
    total_score: float | None = None
    max_assessed_score: float
    percentage: float | None = None
    criteria: list[ScoreCriterion]
    checklist: list[ChecklistItem]
    disclaimer: str


class AssistantRequest(BaseModel):
    session_id: str | None = None
    question: str = Field(min_length=1, max_length=500)
    language: Literal["en", "ur", "roman_ur"] = "en"


class AssistantResponse(BaseModel):
    language: Literal["en", "ur", "roman_ur"]
    intent: str
    answer: str
    grounded_facts: list[str]
    uncertain: bool
    disclaimer: str
