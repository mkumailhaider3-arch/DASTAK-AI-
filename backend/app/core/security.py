import io
import uuid
from pathlib import Path
from fastapi import HTTPException
from PIL import Image
import fitz  # PyMuPDF

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
ALLOWED_MIME_BY_EXT = {
    ".jpg": {"image/jpeg", "image/jpg"},
    ".jpeg": {"image/jpeg", "image/jpg"},
    ".png": {"image/png"},
    ".pdf": {"application/pdf"},
}


def validate_upload(
    filename: str | None,
    content_type: str | None,
    data: bytes,
    max_bytes: int,
) -> tuple[str, str]:
    """Validate extension, MIME type, size, and actual file contents (magic bytes + parser)."""
    if not filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{ext}'. Only JPG, PNG, and PDF are allowed.",
        )

    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size limit of {max_bytes // (1024 * 1024)} MB.",
        )

    if content_type:
        ct_lower = content_type.lower().split(";")[0].strip()
        if ct_lower not in ALLOWED_MIME_BY_EXT[ext] and ct_lower != "application/octet-stream":
            raise HTTPException(
                status_code=400,
                detail=f"MIME type '{ct_lower}' does not match extension '{ext}'.",
            )

    # Verify actual file contents rather than trusting extension/MIME alone
    if ext in {".jpg", ".jpeg"}:
        if not data.startswith(b"\xff\xd8\xff"):
            raise HTTPException(status_code=400, detail="Invalid JPEG file signature.")
        try:
            with Image.open(io.BytesIO(data)) as img:
                img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Corrupted or unreadable JPEG image.")
        return ext, "image/jpeg"

    if ext == ".png":
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise HTTPException(status_code=400, detail="Invalid PNG file signature.")
        try:
            with Image.open(io.BytesIO(data)) as img:
                img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Corrupted or unreadable PNG image.")
        return ext, "image/png"

    if ext == ".pdf":
        if not data.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="Invalid PDF file signature.")
        try:
            doc = fitz.open(stream=data, filetype="pdf")
            if doc.page_count < 1:
                raise HTTPException(status_code=400, detail="PDF contains no pages.")
            doc.close()
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Corrupted or unreadable PDF document.")
        return ext, "application/pdf"

    raise HTTPException(status_code=400, detail="Unsupported file type.")


def safe_storage_path(upload_dir: str, session_id: str, ext: str) -> tuple[str, Path]:
    """Generate a safe server-side UUID filename and prevent path traversal."""
    base = Path(upload_dir).resolve()
    session_dir = (base / session_id).resolve()
    if base not in session_dir.parents and base != session_dir:
        raise HTTPException(status_code=400, detail="Invalid session storage path.")
    session_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}{ext}"
    return safe_name, session_dir / safe_name
