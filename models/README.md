# DASTAK AI — Models Directory

This directory stores trained local baseline model artifacts and metadata:
- `doc_classifier.joblib`: scikit-learn TF-IDF + LogisticRegression baseline pipeline (created by `scripts/train_classifier.py`).
- `doc_classifier_meta.json`: Model version, class labels, and training dataset note.

If these files are absent, the backend automatically enters **Demo Mode** (`"Model not trained — demo mode"`) and allows manual category selection without fabricating confidence or accuracy.

Visual anomaly screening (`anomaly_detector.joblib`) is **Not configured** by default because no labelled tampering dataset is bundled.
