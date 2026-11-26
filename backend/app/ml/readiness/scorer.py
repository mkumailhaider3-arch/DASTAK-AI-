from dataclasses import dataclass

CHECKLISTS: dict[str, list[dict]] = {
    "General Application": [
        {"category": "identity-card-style sample", "label": "Identity-Card-Style Sample", "required": True},
        {"category": "educational certificate", "label": "Educational Certificate", "required": True},
        {"category": "application form", "label": "Application Form", "required": True},
    ],
    "University Admission Demo": [
        {"category": "identity-card-style sample", "label": "Identity-Card-Style Sample", "required": True},
        {"category": "educational certificate", "label": "Educational Certificate", "required": True},
        {"category": "application form", "label": "Application Form", "required": True},
        {"category": "receipt/other", "label": "Fee Receipt / Other", "required": False},
    ],
    "Travel / Visa Package Demo": [
        {"category": "passport-style sample", "label": "Passport-Style Sample", "required": True},
        {"category": "identity-card-style sample", "label": "Identity-Card-Style Sample", "required": True},
        {"category": "application form", "label": "Application Form", "required": True},
        {"category": "receipt/other", "label": "Booking / Fee Receipt", "required": False},
    ],
}


@dataclass
class ReadinessWeights:
    categories_weight: float = 40.0
    readability_weight: float = 25.0
    fields_weight: float = 20.0
    consistency_weight: float = 15.0


def evaluate_readiness(
    application_type: str,
    documents: list[dict],
    comparisons: list[dict] | None = None,
    weights: ReadinessWeights | None = None,
) -> dict:
    """Compute transparent rule-based Prototype Readiness Score.

    If a criterion cannot be assessed, marks it 'Not assessed' and adjusts denominator.
    """
    w = weights or ReadinessWeights()
    template = CHECKLISTS.get(application_type, CHECKLISTS["General Application"])

    # 1. Checklist evaluation
    checklist_items = []
    required_count = 0
    present_required_count = 0

    for req in template:
        cat = req["category"]
        matched = [
            d["original_filename"]
            for d in documents
            if d.get("selected_category") == cat
        ]
        needs_review = any(
            d.get("selected_category") == cat and d.get("quality") and not d["quality"].get("is_readable", True)
            for d in documents
        )
        if not matched:
            status = "Missing"
        elif needs_review:
            status = "Needs review"
        else:
            status = "Present"

        if req["required"]:
            required_count += 1
            if matched:
                present_required_count += 1

        checklist_items.append(
            {
                "category": cat,
                "label": req["label"],
                "required": req["required"],
                "status": status,
                "matched_documents": matched,
            }
        )

    criteria = []
    assessed_max = 0.0
    earned_total = 0.0

    # Criterion 1: Required document categories present (40 pts)
    if required_count > 0:
        cat_score = w.categories_weight * (present_required_count / required_count)
        assessed_max += w.categories_weight
        earned_total += cat_score
        criteria.append(
            {
                "name": "Required document categories present",
                "weight": w.categories_weight,
                "earned": round(cat_score, 2),
                "status": "assessed",
                "explanation": f"{present_required_count} of {required_count} required categories present.",
            }
        )
    else:
        criteria.append(
            {
                "name": "Required document categories present",
                "weight": w.categories_weight,
                "earned": None,
                "status": "Not assessed",
                "explanation": "No required categories configured.",
            }
        )

    # Criterion 2: Readability of uploaded documents (25 pts)
    docs_with_quality = [d for d in documents if d.get("quality") is not None]
    if docs_with_quality:
        readable_count = sum(1 for d in docs_with_quality if d["quality"].get("is_readable"))
        read_score = w.readability_weight * (readable_count / len(docs_with_quality))
        assessed_max += w.readability_weight
        earned_total += read_score
        criteria.append(
            {
                "name": "Readability of uploaded documents",
                "weight": w.readability_weight,
                "earned": round(read_score, 2),
                "status": "assessed",
                "explanation": f"{readable_count} of {len(docs_with_quality)} documents passed heuristic readability checks.",
            }
        )
    else:
        criteria.append(
            {
                "name": "Readability of uploaded documents",
                "weight": w.readability_weight,
                "earned": None,
                "status": "Not assessed",
                "explanation": "No documents have been analyzed for readability yet.",
            }
        )

    # Criterion 3: Required fields extracted (20 pts)
    analyzed_docs = [d for d in documents if d.get("analyzed")]
    if analyzed_docs:
        total_slots = 0
        filled_slots = 0
        for d in analyzed_docs:
            for f in d.get("fields", []):
                if f.get("field_name") in {"full_name", "date_of_birth", "id_number"}:
                    total_slots += 1
                    if str(f.get("value") or "").strip():
                        filled_slots += 1
        field_ratio = (filled_slots / total_slots) if total_slots > 0 else 0.0
        field_score = w.fields_weight * field_ratio
        assessed_max += w.fields_weight
        earned_total += field_score
        criteria.append(
            {
                "name": "Required fields extracted",
                "weight": w.fields_weight,
                "earned": round(field_score, 2),
                "status": "assessed",
                "explanation": f"{filled_slots} of {total_slots} key fields (name, DOB, ID) populated or corrected.",
            }
        )
    else:
        criteria.append(
            {
                "name": "Required fields extracted",
                "weight": w.fields_weight,
                "earned": None,
                "status": "Not assessed",
                "explanation": "No documents analyzed for field extraction yet.",
            }
        )

    # Criterion 4: Cross-document consistency (15 pts)
    if comparisons and len(documents) >= 2:
        comparable = [c for c in comparisons if c["status"] in {"Match", "Near-match", "Mismatch"}]
        if comparable:
            match_pts = sum(
                1.0 if c["status"] == "Match" else (0.5 if c["status"] == "Near-match" else 0.0)
                for c in comparable
            )
            cons_score = w.consistency_weight * (match_pts / len(comparable))
            assessed_max += w.consistency_weight
            earned_total += cons_score
            criteria.append(
                {
                    "name": "Cross-document consistency",
                    "weight": w.consistency_weight,
                    "earned": round(cons_score, 2),
                    "status": "assessed",
                    "explanation": f"Assessed {len(comparable)} compared fields across documents.",
                }
            )
        else:
            criteria.append(
                {
                    "name": "Cross-document consistency",
                    "weight": w.consistency_weight,
                    "earned": None,
                    "status": "Not assessed",
                    "explanation": "Compared fields were missing or not detected across documents.",
                }
            )
    else:
        criteria.append(
            {
                "name": "Cross-document consistency",
                "weight": w.consistency_weight,
                "earned": None,
                "status": "Not assessed",
                "explanation": "Run cross-document comparison with at least 2 documents to assess consistency.",
            }
        )

    percentage = round((earned_total / assessed_max) * 100.0, 1) if assessed_max > 0 else None

    return {
        "score_label": "Prototype readiness score",
        "total_score": round(earned_total, 2) if assessed_max > 0 else None,
        "max_assessed_score": round(assessed_max, 2),
        "percentage": percentage,
        "criteria": criteria,
        "checklist": checklist_items,
        "disclaimer": (
            "Prototype readiness score only — reflects heuristic pre-checks and user-confirmed fields, "
            "not approval probability or any official government score."
        ),
    }
