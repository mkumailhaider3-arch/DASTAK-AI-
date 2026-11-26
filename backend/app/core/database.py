import sqlite3
from pathlib import Path
from app.core.config import settings


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    target = db_path or settings.db_path
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str | None = None) -> None:
    conn = get_connection(db_path)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                application_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                uploaded_at TEXT NOT NULL,
                selected_category TEXT NOT NULL DEFAULT 'receipt/other',
                predicted_category TEXT,
                prediction_confidence REAL,
                model_version TEXT,
                classification_status TEXT NOT NULL DEFAULT 'demo_mode',
                ocr_text TEXT NOT NULL DEFAULT '',
                ocr_error TEXT,
                ocr_engine TEXT,
                quality_json TEXT,
                anomaly_json TEXT,
                analyzed INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS document_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                field_value TEXT NOT NULL DEFAULT '',
                confidence REAL,
                status TEXT NOT NULL DEFAULT 'not_detected',
                UNIQUE(document_id, field_name),
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS reports_log (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );
            """
        )
        conn.commit()
    finally:
        conn.close()
