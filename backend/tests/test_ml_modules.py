from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from app.ml.anomaly.screener import screen_visual_anomalies
from app.ml.assistant.guidance import answer_question
from app.ml.classification.classifier import classify_document
from app.ml.matching.comparator import compare_field_across_documents, normalize_value
from app.ml.quality.assessor import assess_image_quality
from app.ml.readiness.scorer import evaluate_readiness


def test_matching_exact_mismatch_missing_nearmatch():
    assert normalize_value("  Ayesha   KHAN ") == "ayesha khan"

    # Exact match
    res_exact = compare_field_across_documents(
        "full_name",
        [
            {"document_id": "1", "document_name": "a.png", "value": "Ayesha Khan"},
            {"document_id": "2", "document_name": "b.png", "value": "  ayesha   khan "},
        ],
    )
    assert res_exact["status"] == "Match"

    # Near-match
    res_near = compare_field_across_documents(
        "full_name",
        [
            {"document_id": "1", "document_name": "a.png", "value": "Ayesha Khan"},
            {"document_id": "2", "document_name": "b.png", "value": "Ayesha Khaan"},
        ],
        fuzzy_threshold=0.85,
    )
    assert res_near["status"] == "Near-match"

    # Mismatch
    res_mis = compare_field_across_documents(
        "full_name",
        [
            {"document_id": "1", "document_name": "a.png", "value": "Ayesha Khan"},
            {"document_id": "2", "document_name": "b.png", "value": "Bilal Ahmed"},
        ],
    )
    assert res_mis["status"] == "Mismatch"

    # Missing
    res_miss = compare_field_across_documents(
        "full_name",
        [
            {"document_id": "1", "document_name": "a.png", "value": "Ayesha Khan"},
            {"document_id": "2", "document_name": "b.png", "value": ""},
        ],
    )
    assert res_miss["status"] == "Missing"

    # Not detected
    res_none = compare_field_across_documents(
        "full_name",
        [
            {"document_id": "1", "document_name": "a.png", "value": ""},
            {"document_id": "2", "document_name": "b.png", "value": ""},
        ],
    )
    assert res_none["status"] == "Not detected"


def test_image_quality_sharp_vs_blurry(tmp_path: Path):
    sharp_path = tmp_path / "sharp.png"
    img = Image.new("RGB", (800, 600), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 750, 550], outline=(10, 10, 10), width=6)
    draw.text((100, 150), "SYNTHETIC SHARP TEST 12345", fill=(0, 0, 0))
    img.save(sharp_path)

    blur_path = tmp_path / "blurry.png"
    img.filter(ImageFilter.GaussianBlur(radius=6)).save(blur_path)

    q_sharp = assess_image_quality(sharp_path, "image/png")
    q_blur = assess_image_quality(blur_path, "image/png")

    assert q_sharp["width"] == 800
    assert q_blur["blur_score"] < q_sharp["blur_score"]
    assert any("blur" in w.lower() for w in q_blur["warnings"])


def test_classifier_demo_mode_when_missing(tmp_path: Path):
    res = classify_document("SYNTHETIC IDENTITY CARD", model_dir=str(tmp_path))
    assert res["status"] == "demo_mode"
    assert res["predicted_category"] is None
    assert res["confidence"] is None
    assert "demo mode" in res["message"].lower()


def test_readiness_score_and_not_assessed_denominator():
    docs = [
        {
            "id": "d1",
            "original_filename": "id.png",
            "selected_category": "identity-card-style sample",
            "quality": {"is_readable": True},
            "fields": [
                {"field_name": "full_name", "value": "Ayesha Khan"},
                {"field_name": "date_of_birth", "value": "12/04/1998"},
                {"field_name": "id_number", "value": "DEMO-12345-1"},
            ],
            "analyzed": True,
        }
    ]
    res = evaluate_readiness("General Application", docs, comparisons=[])
    assert res["score_label"] == "Prototype readiness score"
    # Consistency criterion should be Not assessed (max_assessed = 40 + 25 + 20 = 85)
    assert res["max_assessed_score"] == 85.0
    missing_cats = [c["category"] for c in res["checklist"] if c["status"] == "Missing"]
    assert "educational certificate" in missing_cats


def test_multilingual_assistant_intents():
    for lang in ("en", "ur", "roman_ur"):
        r = answer_question("Why is a document missing?", lang)  # type: ignore[arg-type]
        assert r["intent"] == "missing_document"
        assert r["uncertain"] is False
        assert len(r["answer"]) > 10

    r_uncertain = answer_question("Tell me about Mars weather", "en")
    assert r_uncertain["intent"] == "uncertain"
    assert r_uncertain["uncertain"] is True


def test_anomaly_screener_not_configured(tmp_path: Path):
    res = screen_visual_anomalies(tmp_path / "dummy.png", model_dir=str(tmp_path))
    assert res["status"] == "not_configured"
    assert res["label"] == "Not configured"
