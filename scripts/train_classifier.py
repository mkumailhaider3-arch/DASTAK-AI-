"""Train a reproducible scikit-learn TF-IDF + LogisticRegression document classifier baseline.

Reads data/sample_synthetic/dataset_manifest.csv (train split) and saves
models/doc_classifier.joblib and models/doc_classifier_meta.json.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "data" / "sample_synthetic" / "dataset_manifest.csv"
MODELS_DIR = PROJECT_ROOT / "models"


def main() -> None:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Manifest not found at {MANIFEST_PATH}. Run scripts/prepare_data.py first."
        )

    df = pd.read_csv(MANIFEST_PATH)
    train_df = df[df["split"] == "train"].copy()

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
            ("clf", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )

    pipeline.fit(train_df["synthetic_text"].fillna(""), train_df["category"])

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / "doc_classifier.joblib"
    meta_path = MODELS_DIR / "doc_classifier_meta.json"

    joblib.dump(pipeline, model_path)
    meta = {
        "model_version": "v1.0-tfidf-logreg",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "classes": sorted(train_df["category"].unique().tolist()),
        "train_samples": int(len(train_df)),
        "dataset_note": "Synthetic fictional baseline dataset (seed=42)",
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Saved trained classifier to {model_path}")
    print(f"Saved metadata to {meta_path}")


if __name__ == "__main__":
    main()
