"""
auto_analysis.py — PolicyPal v4
Uses core.py smart chunking (token-based, header/footer removal) for PDF extraction.
Uses Google Gemini (google-genai SDK) for LLM calls.
"""
import json
import io
import os
from google import genai

GEMINI_MODEL = "gemini-2.5-flash"


def _client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def extract_pdf_text(uploaded_file, max_chars: int = 20000) -> str:
    """Smart extraction: header/footer removal + token chunking via core.py."""
    data = uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file
    tmp_path = "/tmp/_policypal_upload.pdf"
    with open(tmp_path, "wb") as f:
        f.write(data)
    try:
        from core import parse_pdf_to_pages
        pages = parse_pdf_to_pages(tmp_path)
        joined = "\n\n".join([f"[PAGE {p}]\n{txt}" for p, txt in pages])
        return joined[:max_chars]
    except Exception:
        import pdfplumber
        text_parts = []
        try:
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                for page in pdf.pages:
                    pt = page.extract_text()
                    if pt:
                        text_parts.append(pt)
        except Exception as e:
            return f"[PDF extraction error: {e}]"
        return "\n".join(text_parts)[:max_chars]


def analyze_policy_document(text: str, api_key: str) -> dict:
    client = _client(api_key)
    prompt = f"""You are a licensed insurance advisor. Analyze this insurance policy and extract key information.

Return ONLY a valid JSON object — no markdown fences, no preamble, no extra text.

Schema:
{{
  "policy_type": "Health | Auto | Home | Life | Renters | Other",
  "insurer": "Company name or Unknown",
  "deductible": "e.g. $1,500 or Not found",
  "annual_premium": "e.g. $2,400/yr or Not found",
  "monthly_premium": "e.g. $200/mo or Not found",
  "out_of_pocket_max": "e.g. $7,000 or Not found",
  "coverage_limit": "e.g. $500,000 or Not found",
  "coverage_areas": {{"AreaName": integer_percentage}},
  "key_benefits": ["Up to 5 specific benefits"],
  "exclusions": ["Up to 6 exclusions"],
  "risk_flags": ["Up to 3 serious gaps"],
  "risk_score": integer_1_to_10,
  "risk_explanation": "1-2 sentences",
  "plain_summary": "2-3 sentences plain English",
  "who_its_good_for": "1 sentence",
  "potential_savings": "Specific tip or None identified"
}}

Coverage areas must sum to 100.
Risk: 1-3 excellent, 4-6 average, 7-10 high risk.
If a value is not explicitly stated, use Not found — never guess numeric values.

POLICY TEXT:
{text}"""

    try:
        resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        raw = resp.text.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw)
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {type(e).__name__}: {e}") from e


def ask_policy_question(
    question: str,
    policy_text: str,
    api_key: str,
    chat_history: list = None,
) -> str:
    # Try full RAG pipeline if vector index exists
    if os.path.exists("storage/vector_store.json"):
        try:
            from core import rag_answer
            result = rag_answer(question, api_key=api_key)
            return result.get("answer", "")
        except Exception:
            pass

    # Intent classification even without vector store
    intent = "Informational"
    instruction = (
        "Answer using ONLY the policy document. Cite sections when possible.\n"
        "End scenario answers with: I recommend confirming directly with your insurer.\n"
    )
    try:
        from core import classify_intent, build_answer_instruction
        intent = classify_intent(question, api_key=api_key)
        instruction = build_answer_instruction(intent)
    except Exception:
        pass

    history_text = ""
    if chat_history:
        for msg in chat_history[-6:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n\n"

    client = _client(api_key)
    prompt = f"""You are PolicyPal — a friendly, expert insurance assistant.
Answer questions ONLY based on the policy document below.

POLICY DOCUMENT:
{policy_text[:12000]}

{history_text}User: {question}

{instruction}"""

    try:
        resp = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        return resp.text
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {type(e).__name__}: {e}") from e

