from pathlib import Path
from app.core.config import settings


def screen_visual_anomalies(file_path: Path, model_dir: str | None = None) -> dict:
    """Experimental visual anomaly screening interface.

    Safely reports 'Not configured' until a suitable labelled research dataset/model
    is configured and evaluated. Never claims to detect all edits or prove fraud.
    """
    base = Path(model_dir or settings.model_dir)
    anomaly_model = base / "anomaly_detector.joblib"

    if not anomaly_model.exists():
        return {
            "status": "not_configured",
            "label": "Not configured",
            "score": None,
            "explanation": (
                "Experimental visual anomaly screening is not configured because no "
                "labelled tampering dataset/model is loaded. Human review is required."
            ),
            "heatmap_base64": None,
        }

    # If a future evaluated model is placed here, it would run here.
    return {
        "status": "not_configured",
        "label": "Not configured",
        "score": None,
        "explanation": "Anomaly screening model placeholder; please review document visually.",
        "heatmap_base64": None,
    }
