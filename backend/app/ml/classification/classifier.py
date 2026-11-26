import json
from pathlib import Path
import joblib
import numpy as np
from app.core.config import settings

SUPPORTED_CATEGORIES = [
    "identity-card-style sample",
    "passport-style sample",
    "educational certificate",
    "application form",
    "receipt/other",
]


def _model_paths(model_dir: str | None = None) -> tuple[Path, Path]:
    base = Path(model_dir or settings.model_dir)
    return base / "doc_classifier.joblib", base / "doc_classifier_meta.json"


def get_classifier_status(model_dir: str | None = None) -> str:
    model_file, meta_file = _model_paths(model_dir)
    if model_file.exists() and meta_file.exists():
        return "trained"
    return "demo_mode"


def classify_document(ocr_text: str, model_dir: str | None = None) -> dict:
    """Classify document using trained scikit-learn baseline if available.

    If no trained model is present, returns explicit 'Model not trained — demo mode'
    and never fabricates confidence or accuracy.
    """
    model_file, meta_file = _model_paths(model_dir)
    if not model_file.exists() or not meta_file.exists():
        return {
            "status": "demo_mode",
            "predicted_category": None,
            "confidence": None,
            "model_version": None,
            "message": "Model not trained — demo mode. Please select document category manually.",
        }

    try:
        pipeline = joblib.load(model_file)
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        text_input = [ocr_text.strip() or "empty"]
        pred = str(pipeline.predict(text_input)[0])

        confidence: float | None = None
        if hasattr(pipeline, "predict_proba"):
            probs = pipeline.predict_proba(text_input)[0]
            confidence = round(float(np.max(probs)), 4)

        return {
            "status": "trained",
            "predicted_category": pred,
            "confidence": confidence,
            "model_version": meta.get("model_version", "v1.0-baseline"),
            "message": f"Classified using trained baseline ({meta.get('dataset_note', 'synthetic/research baseline')}).",
        }
    except Exception:
        return {
            "status": "demo_mode",
            "predicted_category": None,
            "confidence": None,
            "model_version": None,
            "message": "Model not trained — demo mode. Trained artifact could not be loaded.",
        }
