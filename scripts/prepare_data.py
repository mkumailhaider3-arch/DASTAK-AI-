"""Generate synthetic fictional document images and reproducible train/val/test splits.

Never uses real personal documents. All names/IDs are fictional placeholders.
"""

import csv
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "sample_synthetic"
SEED = 42

CATEGORIES = [
    "identity-card-style sample",
    "passport-style sample",
    "educational certificate",
    "application form",
    "receipt/other",
]

TEMPLATES = {
    "identity-card-style sample": [
        "SYNTHETIC IDENTITY CARD SAMPLE\nFull Name: {name}\nDate of Birth: {dob}\nID Number: {id_num}\nIssue Date: {issue_date}\nNOT AN OFFICIAL DOCUMENT",
        "FICTIONAL DEMO ID CARD\nName: {name}\nDOB: {dob}\nID No: {id_num}\nDocument Date: {issue_date}\nACADEMIC PROTOTYPE ONLY",
    ],
    "passport-style sample": [
        "SYNTHETIC PASSPORT SAMPLE\nFull Name: {name}\nDate of Birth: {dob}\nPassport No: {id_num}\nIssue Date: {issue_date}\nFICTIONAL SPECIMEN",
        "DEMO TRAVEL DOCUMENT\nApplicant Name: {name}\nBirth Date: {dob}\nPassport Number: {id_num}\nIssued On: {issue_date}\nNOT OFFICIAL",
    ],
    "educational certificate": [
        "SYNTHETIC ACADEMIC TRANSCRIPT\nStudent Name: {name}\nDate of Birth: {dob}\nRegistration No: {id_num}\nIssue Date: {issue_date}\nBoard of Demo Studies\nGrade: A",
        "FICTIONAL DEGREE CERTIFICATE\nFull Name: {name}\nDOB: {dob}\nRoll Number: {id_num}\nDocument Date: {issue_date}\nDemo University",
    ],
    "application form": [
        "GENERAL APPLICATION FORM (DEMO)\nApplicant Name: {name}\nDate of Birth: {dob}\nReference No: {id_num}\nDocument Date: {issue_date}\nChecklist Package Submission",
        "ADMISSION APPLICATION FORM\nFull Name: {name}\nBirth Date: {dob}\nRef ID: {id_num}\nDate: {issue_date}\nSignature: Demo Applicant",
    ],
    "receipt/other": [
        "DEMO FEE PAYMENT RECEIPT\nPaid By: {name}\nReference No: {id_num}\nDate: {issue_date}\nAmount: PKR 1,500\nStatus: Demo Paid",
        "SYNTHETIC PROCESSING RECEIPT\nName: {name}\nReceipt Ref: {id_num}\nDocument Date: {issue_date}\nFee: 2000 PKR\nAcademic Test",
    ],
}

FICTIONAL_NAMES = [
    "Ayesha Khan",
    "Bilal Ahmed",
    "Zainab Fatima",
    "Usman Tariq",
    "Hira Siddiqui",
    "Hamza Raza",
]


def render_document_image(text: str, out_path: Path, blurry: bool = False) -> None:
    img = Image.new("RGB", (900, 560), color=(248, 250, 252))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 880, 540], outline=(18, 59, 93), width=4)
    try:
        font = ImageFont.truetype("arial.ttf", 26)
    except Exception:
        font = ImageFont.load_default()

    y = 60
    for line in text.splitlines():
        draw.text((55, y), line, fill=(15, 23, 42), font=font)
        y += 52

    if blurry:
        img = img.filter(ImageFilter.GaussianBlur(radius=3.5))
    img.save(out_path)


def main() -> None:
    rng = random.Random(SEED)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest_rows = []

    samples_per_class = 15  # 75 total synthetic documents
    for cat in CATEGORIES:
        cat_slug = cat.replace(" ", "_").replace("/", "_")
        cat_dir = DATA_DIR / cat_slug
        cat_dir.mkdir(parents=True, exist_ok=True)

        for idx in range(samples_per_class):
            name = rng.choice(FICTIONAL_NAMES)
            dob = f"{rng.randint(10, 28):02d}/0{rng.randint(1, 9)}/199{rng.randint(2, 9)}"
            id_num = f"DEMO-{rng.randint(10000, 99999)}-{rng.randint(1, 9)}"
            issue_date = f"15/0{rng.randint(1, 9)}/2025"
            tpl = TEMPLATES[cat][idx % len(TEMPLATES[cat])]
            text = tpl.format(name=name, dob=dob, id_num=id_num, issue_date=issue_date)

            blurry = idx == 0  # include 1 blurry sample per class for quality testing
            fname = f"{cat_slug}_{idx + 1:02d}.png"
            out_path = cat_dir / fname
            render_document_image(text, out_path, blurry=blurry)

            # Fixed deterministic split: 60% train, 20% val, 20% test
            if idx < 9:
                split = "train"
            elif idx < 12:
                split = "val"
            else:
                split = "test"

            manifest_rows.append(
                {
                    "filepath": str(out_path.relative_to(PROJECT_ROOT)),
                    "category": cat,
                    "split": split,
                    "synthetic_text": text.replace("\n", " | "),
                    "is_blurry_sample": str(blurry),
                }
            )

    manifest_path = DATA_DIR / "dataset_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["filepath", "category", "split", "synthetic_text", "is_blurry_sample"]
        )
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"Generated {len(manifest_rows)} synthetic samples at {DATA_DIR}")
    print(f"Manifest written to {manifest_path}")


if __name__ == "__main__":
    main()
