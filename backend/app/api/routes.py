import io
import cv2
from fastapi import APIRouter, File, Query, UploadFile
from fastapi.responses import Response
from app.core.config import settings
from app.core.security import validate_upload
from app.ml.anomaly.screener import screen_visual_anomalies
from app.ml.assistant.guidance import answer_question
from app.ml.classification.classifier import classify_document, get_classifier_status
from app.ml.matching.comparator import compare_field_across_documents
from app.ml.ocr.extractor import (
    DEFAULT_FIELDS,
    extract_fields_from_ocr,
    extract_text_from_document,
    get_ocr_engine_name,
)
from app.ml.quality.assessor import assess_image_quality, load_image_for_cv
from app.ml.readiness.scorer import evaluate_readiness
from app.reports.pdf_generator import generate_session_pdf
from app.schemas.models import (
    AssistantRequest,
    AssistantResponse,
    CompareRequest,
    CompareResponse,
    CreateSessionRequest,
    DashboardStatsResponse,
    DocumentResponse,
    HealthResponse,
    ReadinessResponse,
    SessionSummary,
    UpdateDocumentRequest,
)
from app.services import storage_service

router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    return {
        "status": "ok",
        "ocr_engine": get_ocr_engine_name(),
        "classifier_status": get_classifier_status(),
    }


@router.get("/sessions", response_model=DashboardStatsResponse, tags=["Sessions"])
def list_sessions():
    return storage_service.get_dashboard_stats()


@router.post("/sessions", response_model=SessionSummary, tags=["Sessions"])
def create_session(payload: CreateSessionRequest):
    return storage_service.create_session(payload.application_type)


@router.delete("/sessions/{session_id}", tags=["Sessions"])
def delete_session(session_id: str):
    return storage_service.delete_session(session_id)


@router.post("/sessions/{session_id}/documents", response_model=list[DocumentResponse], tags=["Documents"])
async def upload_documents(session_id: str, files: list[UploadFile] = File(...)):
    saved_docs = []
    for file in files:
        data = await file.read()
        ext, validated_mime = validate_upload(
            filename=file.filename,
            content_type=file.content_type,
            data=data,
            max_bytes=settings.max_file_size_bytes,
        )
        doc = storage_service.save_uploaded_document(
            session_id=session_id,
            original_filename=file.filename or f"document{ext}",
            ext=ext,
            mime_type=validated_mime,
            data=data,
        )
        saved_docs.append(doc)
    return saved_docs


@router.get("/sessions/{session_id}/documents", response_model=list[DocumentResponse], tags=["Documents"])
def list_documents(session_id: str):
    return storage_service.list_session_documents(session_id)


@router.get("/documents/{document_id}/preview", tags=["Documents"])
def get_document_preview(document_id: str):
    file_path, mime_type = storage_service.get_document_file_path(document_id)
    if mime_type == "application/pdf":
        bgr = load_image_for_cv(file_path, mime_type)
        ok, buf = cv2.imencode(".png", bgr)
        if not ok:
            return Response(status_code=500)
        return Response(content=buf.tobytes(), media_type="image/png")
    return Response(content=file_path.read_bytes(), media_type=mime_type)


@router.post("/documents/{document_id}/analyze", response_model=DocumentResponse, tags=["Analysis"])
def analyze_document(document_id: str):
    file_path, mime_type = storage_service.get_document_file_path(document_id)
    quality = assess_image_quality(file_path, mime_type)
    ocr_res = extract_text_from_document(file_path, mime_type)
    fields = extract_fields_from_ocr(ocr_res.get("ocr_text", ""), ocr_res.get("lines"))
    classification = classify_document(ocr_res.get("ocr_text", ""))
    anomaly = screen_visual_anomalies(file_path)

    return storage_service.save_analysis_results(
        doc_id=document_id,
        classification=classification,
        ocr_res=ocr_res,
        extracted_fields=fields,
        quality=quality,
        anomaly=anomaly,
    )


@router.patch("/documents/{document_id}", response_model=DocumentResponse, tags=["Documents"])
def update_document(document_id: str, payload: UpdateDocumentRequest):
    return storage_service.update_document_corrections(
        doc_id=document_id,
        selected_category=payload.selected_category,
        fields=[f.model_dump() for f in payload.fields],
    )


def _run_comparisons(docs: list[dict], field_names: list[str], fuzzy_threshold: float) -> list[dict]:
    comparisons = []
    for fname in field_names:
        entries = []
        for d in docs:
            field_val = ""
            for f in d.get("fields", []):
                if f["field_name"] == fname:
                    field_val = f["value"]
                    break
            entries.append(
                {
                    "document_id": d["id"],
                    "document_name": d["original_filename"],
                    "value": field_val,
                }
            )
        comparisons.append(compare_field_across_documents(fname, entries, fuzzy_threshold=fuzzy_threshold))
    return comparisons


@router.post("/sessions/{session_id}/compare", response_model=CompareResponse, tags=["Analysis"])
def compare_session_documents(session_id: str, payload: CompareRequest):
    docs = storage_service.list_session_documents(session_id)
    comparisons = _run_comparisons(docs, payload.field_names, payload.fuzzy_threshold)
    return {"comparisons": comparisons}


@router.get("/sessions/{session_id}/readiness", response_model=ReadinessResponse, tags=["Readiness"])
def get_readiness(session_id: str):
    session = storage_service.get_session(session_id)
    docs = storage_service.list_session_documents(session_id)
    docs_flat = [
        {
            "id": d["id"],
            "original_filename": d["original_filename"],
            "selected_category": d["classification"]["selected_category"],
            "quality": d["quality"],
            "fields": d["fields"],
            "analyzed": d["analyzed"],
        }
        for d in docs
    ]
    comparisons = _run_comparisons(docs, ["full_name", "date_of_birth", "id_number"], 0.85) if len(docs) >= 2 else []
    return evaluate_readiness(session["application_type"], docs_flat, comparisons)


@router.post("/assistant/ask", response_model=AssistantResponse, tags=["Assistant"])
def ask_assistant(payload: AssistantRequest):
    session_summary = None
    readiness = None
    if payload.session_id:
        try:
            session_summary = storage_service.get_session(payload.session_id)
            readiness = get_readiness(payload.session_id)
        except Exception:
            session_summary = None
            readiness = None

    return answer_question(
        question=payload.question,
        language=payload.language,
        session_summary=session_summary,
        readiness=readiness,
    )


@router.get("/sessions/{session_id}/report", tags=["Reports"])
def download_report(session_id: str, include_full_ocr: bool = Query(default=False)):
    session = storage_service.get_session(session_id)
    docs = storage_service.list_session_documents(session_id)
    docs_flat = [
        {
            "id": d["id"],
            "original_filename": d["original_filename"],
            "selected_category": d["classification"]["selected_category"],
            "quality": d["quality"],
            "fields": d["fields"],
            "analyzed": d["analyzed"],
            "ocr_text": d["ocr_text"],
        }
        for d in docs
    ]
    comparisons = _run_comparisons(docs, DEFAULT_FIELDS[:3], 0.85) if len(docs) >= 2 else []
    readiness = evaluate_readiness(session["application_type"], docs_flat, comparisons)

    pdf_bytes = generate_session_pdf(
        session=session,
        documents=docs_flat,
        readiness=readiness,
        comparisons=comparisons,
        include_full_ocr=include_full_ocr,
    )
    storage_service.log_report_created(session_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="dastak-report-{session_id[:8]}.pdf"'
        },
    )
