import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import HTTPException
from app.core.config import settings
from app.core.database import get_connection
from app.core.security import safe_storage_path
from app.ml.ocr.extractor import DEFAULT_FIELDS


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_session(application_type: str, db_path: str | None = None) -> dict:
    session_id = uuid.uuid4().hex
    created_at = _now_iso()
    conn = get_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO sessions (id, application_type, created_at) VALUES (?, ?, ?)",
            (session_id, application_type, created_at),
        )
        conn.commit()
    finally:
        conn.close()
    return {
        "id": session_id,
        "application_type": application_type,
        "created_at": created_at,
        "document_count": 0,
        "report_count": 0,
        "readiness_score": None,
    }


def get_session(session_id: str, db_path: str | None = None) -> dict:
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found.")
        doc_count = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE session_id = ?", (session_id,)
        ).fetchone()[0]
        rep_count = conn.execute(
            "SELECT COUNT(*) FROM reports_log WHERE session_id = ?", (session_id,)
        ).fetchone()[0]
        return {
            "id": row["id"],
            "application_type": row["application_type"],
            "created_at": row["created_at"],
            "document_count": doc_count,
            "report_count": rep_count,
            "readiness_score": None,
        }
    finally:
        conn.close()


def get_dashboard_stats(db_path: str | None = None) -> dict:
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT s.id, s.application_type, s.created_at,
                   (SELECT COUNT(*) FROM documents d WHERE d.session_id = s.id) AS doc_count,
                   (SELECT COUNT(*) FROM reports_log r WHERE r.session_id = s.id) AS rep_count
            FROM sessions s
            ORDER BY s.created_at DESC
            """
        ).fetchall()
        total_docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        total_reps = conn.execute("SELECT COUNT(*) FROM reports_log").fetchone()[0]
        sessions = [
            {
                "id": r["id"],
                "application_type": r["application_type"],
                "created_at": r["created_at"],
                "document_count": r["doc_count"],
                "report_count": r["rep_count"],
                "readiness_score": None,
            }
            for r in rows
        ]
        return {
            "total_sessions": len(sessions),
            "total_documents": total_docs,
            "total_reports": total_reps,
            "sessions": sessions,
        }
    finally:
        conn.close()


def delete_session(
    session_id: str,
    db_path: str | None = None,
    upload_dir: str | None = None,
) -> dict:
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Session not found.")
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
    finally:
        conn.close()

    # Delete temporary uploaded files for this session
    target_dir = Path(upload_dir or settings.upload_dir).resolve() / session_id
    if target_dir.exists() and target_dir.is_dir():
        shutil.rmtree(target_dir, ignore_errors=True)

    return {"deleted": True, "message": "Session and temporary files deleted."}


def save_uploaded_document(
    session_id: str,
    original_filename: str,
    ext: str,
    mime_type: str,
    data: bytes,
    db_path: str | None = None,
    upload_dir: str | None = None,
) -> dict:
    # Ensure session exists
    get_session(session_id, db_path)

    doc_id = uuid.uuid4().hex
    stored_name, full_path = safe_storage_path(upload_dir or settings.upload_dir, session_id, ext)
    full_path.write_bytes(data)

    uploaded_at = _now_iso()
    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            INSERT INTO documents (
                id, session_id, original_filename, stored_filename, mime_type,
                size_bytes, uploaded_at, selected_category, classification_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc_id,
                session_id,
                Path(original_filename).name,
                stored_name,
                mime_type,
                len(data),
                uploaded_at,
                "receipt/other",
                "demo_mode",
            ),
        )
        for fname in DEFAULT_FIELDS:
            conn.execute(
                """
                INSERT INTO document_fields (document_id, field_name, field_value, confidence, status)
                VALUES (?, ?, '', NULL, 'not_detected')
                """,
                (doc_id, fname),
            )
        conn.commit()
    finally:
        conn.close()

    return get_document(doc_id, db_path)


def _format_doc_row(row, field_rows) -> dict:
    quality = json.loads(row["quality_json"]) if row["quality_json"] else None
    anomaly = (
        json.loads(row["anomaly_json"])
        if row["anomaly_json"]
        else {
            "status": "not_configured",
            "label": "Not configured",
            "score": None,
            "explanation": "Run analysis to check visual anomaly screening status.",
            "heatmap_base64": None,
        }
    )
    status = row["classification_status"]
    msg = (
        "Model not trained — demo mode. Please select document category manually."
        if status == "demo_mode"
        else f"Classified by baseline model ({row['model_version']})."
    )
    return {
        "id": row["id"],
        "session_id": row["session_id"],
        "original_filename": row["original_filename"],
        "mime_type": row["mime_type"],
        "size_bytes": row["size_bytes"],
        "uploaded_at": row["uploaded_at"],
        "preview_url": f"/api/documents/{row['id']}/preview",
        "classification": {
            "status": status,
            "predicted_category": row["predicted_category"],
            "confidence": row["prediction_confidence"],
            "model_version": row["model_version"],
            "message": msg,
            "selected_category": row["selected_category"],
        },
        "ocr_text": row["ocr_text"],
        "ocr_error": row["ocr_error"],
        "ocr_engine": row["ocr_engine"],
        "fields": [
            {
                "field_name": f["field_name"],
                "value": f["field_value"],
                "confidence": f["confidence"],
                "status": f["status"],
            }
            for f in field_rows
        ],
        "quality": quality,
        "anomaly": anomaly,
        "analyzed": bool(row["analyzed"]),
    }


def get_document(doc_id: str, db_path: str | None = None) -> dict:
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")
        fields = conn.execute(
            "SELECT * FROM document_fields WHERE document_id = ? ORDER BY id ASC", (doc_id,)
        ).fetchall()
        return _format_doc_row(row, fields)
    finally:
        conn.close()


def get_document_file_path(
    doc_id: str,
    db_path: str | None = None,
    upload_dir: str | None = None,
) -> tuple[Path, str]:
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT session_id, stored_filename, mime_type FROM documents WHERE id = ?", (doc_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")
        path = Path(upload_dir or settings.upload_dir).resolve() / row["session_id"] / row["stored_filename"]
        if not path.exists():
            raise HTTPException(status_code=404, detail="Stored document file not found.")
        return path, row["mime_type"]
    finally:
        conn.close()


def list_session_documents(session_id: str, db_path: str | None = None) -> list[dict]:
    get_session(session_id, db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM documents WHERE session_id = ? ORDER BY uploaded_at ASC", (session_id,)
        ).fetchall()
        result = []
        for r in rows:
            fields = conn.execute(
                "SELECT * FROM document_fields WHERE document_id = ? ORDER BY id ASC", (r["id"],)
            ).fetchall()
            result.append(_format_doc_row(r, fields))
        return result
    finally:
        conn.close()


def save_analysis_results(
    doc_id: str,
    classification: dict,
    ocr_res: dict,
    extracted_fields: list[dict],
    quality: dict,
    anomaly: dict,
    db_path: str | None = None,
) -> dict:
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT selected_category FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")

        selected_cat = (
            classification["predicted_category"]
            if classification["status"] == "trained" and classification.get("predicted_category")
            else row["selected_category"]
        )

        conn.execute(
            """
            UPDATE documents
            SET selected_category = ?,
                predicted_category = ?,
                prediction_confidence = ?,
                model_version = ?,
                classification_status = ?,
                ocr_text = ?,
                ocr_error = ?,
                ocr_engine = ?,
                quality_json = ?,
                anomaly_json = ?,
                analyzed = 1
            WHERE id = ?
            """,
            (
                selected_cat,
                classification.get("predicted_category"),
                classification.get("confidence"),
                classification.get("model_version"),
                classification["status"],
                ocr_res.get("ocr_text", ""),
                ocr_res.get("ocr_error"),
                ocr_res.get("ocr_engine"),
                json.dumps(quality),
                json.dumps(anomaly),
                doc_id,
            ),
        )
        for f in extracted_fields:
            conn.execute(
                """
                INSERT INTO document_fields (document_id, field_name, field_value, confidence, status)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(document_id, field_name) DO UPDATE SET
                    field_value = excluded.field_value,
                    confidence = excluded.confidence,
                    status = excluded.status
                """,
                (doc_id, f["field_name"], f["value"], f.get("confidence"), f["status"]),
            )
        conn.commit()
    finally:
        conn.close()

    return get_document(doc_id, db_path)


def update_document_corrections(
    doc_id: str,
    selected_category: str,
    fields: list[dict],
    db_path: str | None = None,
) -> dict:
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT id FROM documents WHERE id = ?", (doc_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Document not found.")

        conn.execute(
            "UPDATE documents SET selected_category = ? WHERE id = ?",
            (selected_category, doc_id),
        )
        for f in fields:
            val = str(f["value"]).strip()
            status = "corrected" if val else "not_detected"
            conn.execute(
                """
                INSERT INTO document_fields (document_id, field_name, field_value, confidence, status)
                VALUES (?, ?, ?, NULL, ?)
                ON CONFLICT(document_id, field_name) DO UPDATE SET
                    field_value = excluded.field_value,
                    status = excluded.status
                """,
                (doc_id, f["field_name"], val, status),
            )
        conn.commit()
    finally:
        conn.close()
    return get_document(doc_id, db_path)


def log_report_created(session_id: str, db_path: str | None = None) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO reports_log (id, session_id, created_at) VALUES (?, ?, ?)",
            (uuid.uuid4().hex, session_id, _now_iso()),
        )
        conn.commit()
    finally:
        conn.close()
