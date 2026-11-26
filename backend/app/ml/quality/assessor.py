from dataclasses import dataclass
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF


@dataclass
class QualityThresholds:
    """Configurable heuristic thresholds for image readability assessment."""
    min_width: int = 400
    min_height: int = 400
    min_blur_variance: float = 60.0
    min_brightness: float = 55.0
    max_brightness: float = 225.0
    min_contrast_std: float = 22.0


def load_image_for_cv(file_path: Path, mime_type: str) -> np.ndarray:
    """Load an image (JPG/PNG) or render page 1 of a PDF to an OpenCV BGR array."""
    if mime_type == "application/pdf" or file_path.suffix.lower() == ".pdf":
        doc = fitz.open(str(file_path))
        try:
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            arr = np.array(img)
            return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        finally:
            doc.close()

    with Image.open(file_path) as pil_img:
        rgb = pil_img.convert("RGB")
        arr = np.array(rgb)
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def assess_image_quality(
    file_path: Path,
    mime_type: str,
    thresholds: QualityThresholds | None = None,
) -> dict:
    """Assess dimensions, blur (Laplacian variance), brightness, and contrast.

    Note: Quality warnings are heuristic, not definitive proof of legibility.
    """
    cfg = thresholds or QualityThresholds()
    bgr = load_image_for_cv(file_path, mime_type)
    height, width = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))

    warnings: list[str] = []
    if width < cfg.min_width or height < cfg.min_height:
        warnings.append(
            f"Low resolution ({width}x{height}px; recommended at least {cfg.min_width}x{cfg.min_height}px)."
        )
    if blur_score < cfg.min_blur_variance:
        warnings.append(
            f"Possible blur detected (Laplacian variance {blur_score:.1f} < {cfg.min_blur_variance:.1f})."
        )
    if brightness < cfg.min_brightness:
        warnings.append(f"Image appears too dark (mean brightness {brightness:.1f} < {cfg.min_brightness:.1f}).")
    elif brightness > cfg.max_brightness:
        warnings.append(
            f"Possible glare or overexposure (mean brightness {brightness:.1f} > {cfg.max_brightness:.1f})."
        )
    if contrast < cfg.min_contrast_std:
        warnings.append(f"Low contrast detected (std {contrast:.1f} < {cfg.min_contrast_std:.1f}).")

    is_readable = len(warnings) == 0
    explanation = (
        "Heuristic readability checks passed. Note: automated checks are advisory only."
        if is_readable
        else "Heuristic quality warnings were triggered. Please review the image visually; automated thresholds are not definitive."
    )

    return {
        "width": int(width),
        "height": int(height),
        "blur_score": round(blur_score, 2),
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "warnings": warnings,
        "is_readable": is_readable,
        "explanation": explanation,
    }
