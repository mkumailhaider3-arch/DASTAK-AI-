"""Evaluate the trained document classifier on the held-out test split and write reports."""

import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "data" / "sample_synthetic" / "dataset_manifest.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "doc_classifier.joblib"
DOCS_DIR = PROJECT_ROOT / "docs"


def main() -> None:
    if not MANIFEST_PATH.exists() or not MODEL_PATH.exists():
        raise FileNotFoundError("Run prepare_data.py and train_classifier.py first.")

    df = pd.read_csv(MANIFEST_PATH)
    test_df = df[df["split"] == "test"].copy()
    pipeline = joblib.load(MODEL_PATH)

    y_true = test_df["category"].tolist()
    y_pred = pipeline.predict(test_df["synthetic_text"].fillna("")).tolist()
    labels = sorted(df["category"].unique().tolist())

    acc = accuracy_score(y_true, y_pred)
    report_dict = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    print(f"Test Accuracy: {acc:.4f} ({len(test_df)} test samples)")
    print(classification_report(y_true, y_pred, labels=labels, zero_division=0))

    # Write docs/dataset_report.md
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    dist = df.groupby(["category", "split"]).size().unstack(fill_value=0)
    dataset_md = [
        "# Dataset Report (Synthetic Baseline)",
        "",
        "Generated from `data/sample_synthetic/dataset_manifest.csv` (seed=42).",
        "",
        "## Class Distribution by Split",
        "",
        dist.to_markdown(),
        "",
        f"Total samples: {len(df)} (100% synthetic fictional documents; no real CNICs or personal data).",
    ]
    (DOCS_DIR / "dataset_report.md").write_text("\n".join(dataset_md), encoding="utf-8")

    # Write docs/model_evaluation.md
    eval_md = [
        "# Model Evaluation Report",
        "",
        f"- **Model:** TF-IDF + LogisticRegression (`models/doc_classifier.joblib`)",
        f"- **Test Split Size:** {len(test_df)} synthetic samples",
        f"- **Accuracy:** {acc:.4f}",
        f"- **Macro F1:** {report_dict['macro avg']['f1-score']:.4f}",
        f"- **Weighted F1:** {report_dict['weighted avg']['f1-score']:.4f}",
        "",
        "## Per-Class Metrics",
        "",
        "| Category | Precision | Recall | F1-Score | Support |",
        "| :--- | :---: | :---: | :---: | :---: |",
    ]
    for lbl in labels:
        m = report_dict[lbl]
        eval_md.append(
            f"| {lbl} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1-score']:.3f} | {int(m['support'])} |"
        )
    eval_md.extend(
        [
            "",
            "## Confusion Matrix",
            "",
            "Labels order: " + ", ".join(labels),
            "",
            "```",
            str(cm),
            "```",
            "",
            "## Limitations",
            "- Evaluated on synthetic fictional templates only; not a substitute for real-world document benchmarks (e.g. RVL-CDIP, FUNSD).",
            "- Visual anomaly screening is **Not configured** (no labelled tampering dataset).",
        ]
    )
    (DOCS_DIR / "model_evaluation.md").write_text("\n".join(eval_md), encoding="utf-8")
    print(f"Wrote {DOCS_DIR / 'dataset_report.md'} and {DOCS_DIR / 'model_evaluation.md'}")


if __name__ == "__main__":
    main()
