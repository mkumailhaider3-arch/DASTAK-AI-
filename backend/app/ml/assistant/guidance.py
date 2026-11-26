from typing import Literal

LanguageCode = Literal["en", "ur", "roman_ur"]


INTENT_KEYWORDS: dict[str, list[str]] = {
    "missing_document": ["missing", "checklist", "required", "absent", "ghayab", "kam", "موجود", "غائب", "دستاویز"],
    "mismatch": ["mismatch", "differ", "compare", "name", "dob", "faraq", "mukhtalif", "فرق", "مختلف", "مطابقت"],
    "blurry_image": ["blur", "blurry", "quality", "dark", "glare", "resolution", "readable", "dhundla", "صاف", "دھندلا"],
    "readiness_score": ["score", "readiness", "points", "percentage", "breakdown", "نمبر", "اسکور"],
    "next_step": ["next", "step", "what should", "how to", "fix", "agla", "kya karun", "اگلا", "قدم"],
}


RESPONSES: dict[str, dict[LanguageCode, str]] = {
    "missing_document": {
        "en": (
            "A 'Missing' status means no uploaded document in your current session was assigned to that "
            "required checklist category. Upload the missing sample document or update the document's "
            "category on the Document Analysis page."
        ),
        "roman_ur": (
            "'Missing' ka matlab hai ke aap ke current session mein is zaroori category ka koi document "
            "upload ya select nahi hua. Missing document upload karein ya Document Analysis page par "
            "sahi category select karein."
        ),
        "ur": (
            "\"Missing\" کا مطلب ہے کہ آپ کے موجودہ سیشن میں اس مطلوبہ زمرے کی کوئی دستاویز اپ لوڈ یا منتخب نہیں کی گئی۔ "
            "براہ کرم مطلوبہ نمونہ دستاویز اپ لوڈ کریں یا Document Analysis صفحے پر درست زمرہ منتخب کریں۔"
        ),
    },
    "mismatch": {
        "en": (
            "A 'Mismatch' means the extracted or entered values (such as name or date of birth) differ "
            "across documents after normalizing spaces and letter case. Review the raw OCR text on the "
            "Document Analysis page and correct any OCR misreads before re-running comparison."
        ),
        "roman_ur": (
            "'Mismatch' ka matlab hai ke mukhtalif documents mein naam ya tareekh-e-paidaish jaisi maloomat "
            "ek jaisi nahi hain. Document Analysis page par OCR text check karein aur agar ghalti ho to "
            "field ko theek karke dobara compare karein."
        ),
        "ur": (
            "\"Mismatch\" کا مطلب ہے کہ مختلف دستاویزات میں نکالی گئی معلومات (جیسے نام یا تاریخ پیدائش) آپس میں مطابقت نہیں رکھتیں۔ "
            "براہ کرم Document Analysis صفحے پر OCR متن دیکھیں اور کسی بھی غلطی کو درست کر کے دوبارہ موازنہ کریں۔"
        ),
    },
    "blurry_image": {
        "en": (
            "Readability warnings use heuristic OpenCV checks (resolution, Laplacian blur variance, "
            "brightness, and contrast). They are advisory only. If your scan looks blurry, dark, or has "
            "glare, try re-capturing it in even lighting with flat framing."
        ),
        "roman_ur": (
            "Image quality warnings OpenCV ke heuristic checks (resolution, blur, brightness, contrast) "
            "par mabni hain. Yeh sirf madad ke liye hain. Agar tasveer dhundli ya andheri ho to achi "
            "roshni mein seedhi aur saaf tasveer dobara upload karein."
        ),
        "ur": (
            "تصویر کے معیار کی وارننگز OpenCV کے اندازوں (ریزولوشن، دھندلاپن، روشنی اور کنٹراسٹ) پر مبنی ہیں۔ "
            "یہ حتمی نہیں بلکہ رہنمائی کے لیے ہیں۔ اگر تصویر دھندلی یا کم روشنی والی ہو تو بہتر روشنی میں صاف تصویر دوبارہ اپ لوڈ کریں۔"
        ),
    },
    "readiness_score": {
        "en": (
            "The Prototype Readiness Score combines four transparent criteria: required categories (40 pts), "
            "readability heuristics (25 pts), key fields extracted (20 pts), and cross-document consistency (15 pts). "
            "Any criterion not yet evaluated is marked 'Not assessed' and excluded from the denominator."
        ),
        "roman_ur": (
            "Prototype Readiness Score chaar hisson par mabni hai: zaroori documents (40), image readability (25), "
            "extract shuda fields (20), aur cross-document consistency (15). Jo hissa abhi check nahi hua usay "
            "'Not assessed' rakha jata hai."
        ),
        "ur": (
            "Prototype Readiness Score چار واضح حصوں پر مشتمل ہے: مطلوبہ دستاویزات (40)، تصویر کی پڑھنے کی اہلیت (25)، "
            "نکالی گئی معلومات (20)، اور دستاویزات میں یکسانیت (15)۔ جو حصہ ابھی جانچا نہیں گیا اسے \"Not assessed\" رکھا جاتا ہے۔"
        ),
    },
    "next_step": {
        "en": (
            "Recommended next steps: (1) Run analysis on all uploaded files, (2) verify category and OCR "
            "fields on Document Analysis, (3) run Compare Documents, and (4) review the Readiness Checklist "
            "and download your PDF summary report."
        ),
        "roman_ur": (
            "Agla qadam: (1) Tamam uploaded files par analysis chalayein, (2) Document Analysis par category "
            "aur OCR fields check karein, (3) Compare Documents chalayein, aur (4) Readiness Checklist dekh "
            "kar PDF report download karein."
        ),
        "ur": (
            "اگلے اقدامات: (1) تمام اپ لوڈ کردہ فائلوں کا تجزیہ چلائیں، (2) Document Analysis پر زمرہ اور OCR فیلڈز کی تصدیق کریں، "
            "(3) Compare Documents چلائیں، اور (4) Readiness Checklist دیکھ کر PDF رپورٹ ڈاؤن لوڈ کریں۔"
        ),
    },
    "uncertain": {
        "en": (
            "I am not certain how to answer that specific question from the local prototype knowledge base. "
            "I can explain missing checklist items, field mismatches, blurry image warnings, the Prototype "
            "Readiness Score, or next steps. I cannot provide legal advice or official government rules."
        ),
        "roman_ur": (
            "Mujhe is sawal ka yaqeeni jawab local knowledge base mein nahi mila. Main missing documents, "
            "field mismatch, blurry image warning, readiness score, aur aglay qadam ke baray mein bata sakta "
            "hoon. Main qanooni mashwara ya sarkari qawaneen nahi de sakta."
        ),
        "ur": (
            "مجھے مقامی نالج بیس میں اس سوال کا یقینی جواب نہیں ملا۔ میں گمشدہ دستاویزات، معلومات کے فرق، دھندلی تصویر، "
            "ریڈینس اسکور اور اگلے اقدامات کی وضاحت کر سکتا ہوں۔ میں قانونی مشورہ یا سرکاری قواعد فراہم نہیں کر سکتا۔"
        ),
    },
}


def detect_intent(question: str) -> str:
    q = question.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            return intent
    return "uncertain"


def build_grounded_facts(session_summary: dict | None, readiness: dict | None) -> list[str]:
    facts: list[str] = []
    if session_summary:
        facts.append(
            f"Session '{session_summary.get('application_type')}' has {session_summary.get('document_count', 0)} document(s)."
        )
    if readiness:
        missing = [c["label"] for c in readiness.get("checklist", []) if c["status"] == "Missing"]
        if missing:
            facts.append(f"Missing checklist categories: {', '.join(missing)}.")
        else:
            facts.append("All required demo checklist categories are present.")
        pct = readiness.get("percentage")
        if pct is not None:
            facts.append(f"Current Prototype Readiness Score: {pct:.1f}%.")
    return facts


def answer_question(
    question: str,
    language: LanguageCode,
    session_summary: dict | None = None,
    readiness: dict | None = None,
) -> dict:
    intent = detect_intent(question)
    uncertain = intent == "uncertain"
    answer = RESPONSES[intent][language]
    facts = build_grounded_facts(session_summary, readiness)

    disclaimer = {
        "en": "Academic prototype guidance only. Not legal advice or an official NADRA/government source.",
        "roman_ur": "Yeh sirf academic prototype ki rehnumai hai; qanooni mashwara ya sarkari/NADRA service nahi hai.",
        "ur": "یہ صرف تعلیمی پروٹوٹائپ کی رہنمائی ہے؛ قانونی مشورہ یا سرکاری/نادرا سروس نہیں۔",
    }[language]

    return {
        "language": language,
        "intent": intent,
        "answer": answer,
        "grounded_facts": facts,
        "uncertain": uncertain,
        "disclaimer": disclaimer,
    }
