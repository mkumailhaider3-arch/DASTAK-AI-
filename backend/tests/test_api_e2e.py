from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont
from app.core.config import settings
from app.core.database import init_db
from app.main import app


def _make_synthetic_png(path: Path, text_lines: list[str]) -> Path:
    img = Image.new("RGB", (900, 560), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 880, 540], outline=(18, 59, 93), width=4)
    try:
        font = ImageFont.truetype("arial.ttf", 26)
    except Exception:
        font = ImageFont.load_default()
    y = 60
    for line in text_lines:
        draw.text((55, y), line, fill=(15, 23, 42), font=font)
        y += 55
    img.save(path)
    return path


def test_full_api_workflow(tmp_path: Path, monkeypatch):
    # Isolate DB and uploads to tmp_path
    db_file = tmp_path / "test_dastak.db"
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(settings, "db_path", str(db_file))
    monkeypatch.setattr(settings, "upload_dir", str(upload_dir))
    init_db(str(db_file))

    client = TestClient(app)

    # 1. Health check
    r_health = client.get("/api/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"

    # 2. Create session
    r_sess = client.post("/api/sessions", json={"application_type": "General Application"})
    assert r_sess.status_code == 200
    session_id = r_sess.json()["id"]

    # 3. Reject invalid spoofed file (.jpg with plain text bytes)
    r_bad = client.post(
        f"/api/sessions/{session_id}/documents",
        files=[("files", ("fake.jpg", b"not a real jpeg", "image/jpeg"))],
    )
    assert r_bad.status_code == 400

    # 4. Reject unsupported extension (.txt)
    r_txt = client.post(
        f"/api/sessions/{session_id}/documents",
        files=[("files", ("notes.txt", b"hello", "text/plain"))],
    )
    assert r_txt.status_code == 400

    # 5. Upload two valid synthetic documents
    doc1_path = _make_synthetic_png(
        tmp_path / "id_sample.png",
        [
            "SYNTHETIC IDENTITY CARD SAMPLE",
            "Full Name: Ayesha Khan",
            "Date of Birth: 12/04/1998",
            "ID Number: DEMO-12345-1",
            "Issue Date: 15/05/2025",
        ],
    )
    doc2_path = _make_synthetic_png(
        tmp_path / "cert_sample.png",
        [
            "SYNTHETIC ACADEMIC TRANSCRIPT",
            "Student Name: Ayesha Khan",
            "Date of Birth: 12/04/1998",
            "Registration No: DEMO-12345-1",
            "Issue Date: 15/05/2025",
        ],
    )

    with doc1_path.open("rb") as f1, doc2_path.open("rb") as f2:
        r_up = client.post(
            f"/api/sessions/{session_id}/documents",
            files=[
                ("files", ("id_sample.png", f1.read(), "image/png")),
                ("files", ("cert_sample.png", f2.read(), "image/png")),
            ],
        )
    assert r_up.status_code == 200
    docs = r_up.json()
    assert len(docs) == 2

    # 6. Analyze both documents (real OCR + quality + classification + anomaly)
    for d in docs:
        r_an = client.post(f"/api/documents/{d['id']}/analyze")
        assert r_an.status_code == 200
        analyzed = r_an.json()
        assert analyzed["analyzed"] is True
        assert analyzed["quality"] is not None
        assert "Ayesha" in analyzed["ocr_text"] or analyzed["ocr_error"] is None

    # 7. Preview endpoint works
    r_prev = client.get(f"/api/documents/{docs[0]['id']}/preview")
    assert r_prev.status_code == 200
    assert r_prev.headers["content-type"].startswith("image/")

    # 8. Correct/confirm fields on doc 1 & doc 2
    r_patch = client.patch(
        f"/api/documents/{docs[0]['id']}",
        json={
            "selected_category": "identity-card-style sample",
            "fields": [{"field_name": "full_name", "value": "Ayesha Khan"}],
        },
    )
    assert r_patch.status_code == 200

    # 9. Compare documents
    r_cmp = client.post(
        f"/api/sessions/{session_id}/compare",
        json={"field_names": ["full_name", "date_of_birth", "id_number"]},
    )
    assert r_cmp.status_code == 200
    assert len(r_cmp.json()["comparisons"]) == 3

    # 10. Readiness score
    r_ready = client.get(f"/api/sessions/{session_id}/readiness")
    assert r_ready.status_code == 200
    assert r_ready.json()["score_label"] == "Prototype readiness score"

    # 11. Assistant
    r_ask = client.post(
        "/api/assistant/ask",
        json={"session_id": session_id, "question": "What is my readiness score?", "language": "roman_ur"},
    )
    assert r_ask.status_code == 200
    assert r_ask.json()["language"] == "roman_ur"

    # 12. PDF Report download
    r_pdf = client.get(f"/api/sessions/{session_id}/report")
    assert r_pdf.status_code == 200
    assert r_pdf.headers["content-type"] == "application/pdf"
    assert r_pdf.content.startswith(b"%PDF-")

    # 13. Delete session & verify files cleaned up
    r_del = client.delete(f"/api/sessions/{session_id}")
    assert r_del.status_code == 200
    assert not (upload_dir / session_id).exists()
