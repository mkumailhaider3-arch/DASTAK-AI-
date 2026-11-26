import re
from difflib import SequenceMatcher


def normalize_value(value: str) -> str:
    """Normalise whitespace and letter case for comparison."""
    cleaned = re.sub(r"\s+", " ", value.strip()).lower()
    return cleaned


def compare_field_across_documents(
    field_name: str,
    doc_entries: list[dict],
    fuzzy_threshold: float = 0.85,
) -> dict:
    """Compare a single field across multiple documents.

    doc_entries: list of {"document_id", "document_name", "value"}
    Returns original & normalized values, exact match first, optional fuzzy near-match,
    or Missing / Not detected / Mismatch. Never silently labels uncertain values identical.
    """
    values_out = []
    non_empty_normalized: list[str] = []

    for entry in doc_entries:
        orig = str(entry.get("value") or "").strip()
        norm = normalize_value(orig)
        values_out.append(
            {
                "document_id": str(entry["document_id"]),
                "document_name": str(entry["document_name"]),
                "original_value": orig,
                "normalized_value": norm,
            }
        )
        if norm:
            non_empty_normalized.append(norm)

    if len(non_empty_normalized) == 0:
        return {
            "field_name": field_name,
            "values": values_out,
            "status": "Not detected",
            "similarity": None,
            "explanation": "Field was not detected in any uploaded document.",
        }

    if len(non_empty_normalized) < len(doc_entries):
        return {
            "field_name": field_name,
            "values": values_out,
            "status": "Missing",
            "similarity": None,
            "explanation": (
                f"Detected in {len(non_empty_normalized)} of {len(doc_entries)} documents; "
                "missing in at least one document."
            ),
        }

    if len(doc_entries) == 1:
        return {
            "field_name": field_name,
            "values": values_out,
            "status": "Not detected" if not non_empty_normalized else "Missing",
            "similarity": None,
            "explanation": "At least two documents are needed for cross-document comparison.",
        }

    unique_vals = set(non_empty_normalized)
    if len(unique_vals) == 1:
        return {
            "field_name": field_name,
            "values": values_out,
            "status": "Match",
            "similarity": 1.0,
            "explanation": "Exact match after normalizing whitespace and letter case.",
        }

    # Check pairwise fuzzy similarity
    min_sim = 1.0
    for i in range(len(non_empty_normalized)):
        for j in range(i + 1, len(non_empty_normalized)):
            sim = SequenceMatcher(None, non_empty_normalized[i], non_empty_normalized[j]).ratio()
            if sim < min_sim:
                min_sim = sim

    min_sim = round(min_sim, 4)
    if min_sim >= fuzzy_threshold:
        return {
            "field_name": field_name,
            "values": values_out,
            "status": "Near-match",
            "similarity": min_sim,
            "explanation": (
                f"Minor spelling or formatting difference detected (similarity {min_sim:.2f} >= {fuzzy_threshold:.2f}). "
                "Human review recommended."
            ),
        }

    return {
        "field_name": field_name,
        "values": values_out,
        "status": "Mismatch",
        "similarity": min_sim,
        "explanation": (
            f"Values differ across documents (similarity {min_sim:.2f}). "
            "Please verify or correct extracted fields."
        ),
    }
