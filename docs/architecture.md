# DASTAK AI — Architecture Overview

## System Components

1. **Frontend (`frontend/`)**
   - Built with **React + TypeScript + Vite + Tailwind CSS v4**.
   - Communicates with FastAPI via REST (`/api/*`), proxied in development through `vite.config.ts`.
   - Implements all 9 screens: Landing, Dashboard, New Analysis/Upload, Document Analysis, Compare Documents, Readiness Checklist, AI Guidance (EN / UR / Roman UR), Reports, and About/Privacy.

2. **Backend (`backend/app/`)**
   - **FastAPI** application with Pydantic request/response schemas and OpenAPI docs (`/docs`).
   - **SQLite** (`dastak_local.db`) for local academic session metadata (`sessions`, `documents`, `document_fields`, `reports_log`).
   - **Upload Security (`core/security.py`)**: validates file extensions, MIME types, 10 MB size limit, and actual magic bytes/image-or-PDF parsing; saves files under UUID filenames outside static directories.

3. **Modular AI/ML Pipeline (`backend/app/ml/`)**
   - `classification/`: scikit-learn TF-IDF + LogisticRegression baseline (`models/doc_classifier.joblib`), with explicit `"Model not trained — demo mode"` fallback when absent.
   - `ocr/`: `rapidocr-onnxruntime` + PyMuPDF PDF-to-image rendering + rule/regex field extraction (`Needs review` for uncertain fields).
   - `quality/`: OpenCV/Pillow heuristic checks (dimensions, Laplacian blur variance, mean brightness, contrast std).
   - `matching/`: whitespace/case normalization, exact matching, and `SequenceMatcher` fuzzy near-match detection.
   - `readiness/`: transparent 40/25/20/15 rule-based Prototype Readiness Score with `"Not assessed"` denominator adjustment.
   - `anomaly/`: experimental visual anomaly screening interface returning `"Not configured"` safely until a labelled tampering dataset is available.
   - `assistant/`: intent-based retrieval grounded in current session analysis across English, Urdu, and Roman Urdu.

4. **PDF Reporting (`backend/app/reports/pdf_generator.py`)**
   - Uses **ReportLab** to generate downloadable PDF reports with prominent academic prototype disclaimers and opt-in raw OCR text.
