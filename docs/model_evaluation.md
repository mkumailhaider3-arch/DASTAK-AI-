# Model Evaluation Report

- **Model:** TF-IDF + LogisticRegression (`models/doc_classifier.joblib`)
- **Test Split Size:** 15 synthetic samples
- **Accuracy:** 1.0000
- **Macro F1:** 1.0000
- **Weighted F1:** 1.0000

## Per-Class Metrics

| Category | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| application form | 1.000 | 1.000 | 1.000 | 3 |
| educational certificate | 1.000 | 1.000 | 1.000 | 3 |
| identity-card-style sample | 1.000 | 1.000 | 1.000 | 3 |
| passport-style sample | 1.000 | 1.000 | 1.000 | 3 |
| receipt/other | 1.000 | 1.000 | 1.000 | 3 |

## Confusion Matrix

Labels order: application form, educational certificate, identity-card-style sample, passport-style sample, receipt/other

```
[[3 0 0 0 0]
 [0 3 0 0 0]
 [0 0 3 0 0]
 [0 0 0 3 0]
 [0 0 0 0 3]]
```

## Limitations
- Evaluated on synthetic fictional templates only; not a substitute for real-world document benchmarks (e.g. RVL-CDIP, FUNSD).
- Visual anomaly screening is **Not configured** (no labelled tampering dataset).