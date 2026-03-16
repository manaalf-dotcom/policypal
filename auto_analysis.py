"""
auto_analysis.py — PolicyPal v3
Uses Google Gemini via the OpenAI-compatible endpoint.
"""
import json
import io
import pdfplumber
import openai


GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL = "gemini-1.5-flash-latest"


def _client(api_key: str) -> openai.OpenAI:
    return openai.OpenAI(api_key=api_key, base_url=GEMINI_BASE_URL)


# ─── TEXT EXTRACTION ─────────────────────────────────────────────────────────

def extract_pdf_text(uploaded_file, max_chars: int = 20000) -> str:
    text_parts = []
    try:
        data = uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        return f"[PDF extraction error: {e}]"
    return "\n".join(text_parts)[:max_chars]


# ─── POLICY ANALYSIS ─────────────────────────────────────────────────────────

def analyze_policy_document(text: str, api_key: str) -> dict:
    c = _client(api_key)

    prompt = f"""You are a licensed insurance advisor. Carefully analyze this insurance policy document and extract key information.

Return ONLY a valid JSON object — no markdown fences, no preamble, no extra text.

Use this exact schema:
{{
  "policy_type": "Health | Auto | Home | Life | Renters | Other",
  "insurer": "Company name or 'Unknown'",
  "deductible": "e.g. '$1,500' or 'Not found'",
  "annual_premium": "e.g. '$2,400/yr' or 'Not found'",
  "monthly_premium": "e.g. '$200/mo' or 'Not found'",
  "out_of_pocket_max": "e.g. '$7,000' or 'Not found'",
  "coverage_limit": "e.g. '$500,000' or 'Not found'",
  "coverage_areas": {{
    "AreaName": integer_percentage
  }},
  "key_benefits": ["Up to 5 specific benefits, include dollar/percentage amounts if found"],
  "exclusions": ["Up to 6 specific exclusions — things the policy does NOT cover"],
  "risk_flags": ["Up to 3 serious gaps or gotchas the policyholder should know"],
  "risk_score": integer_1_to_10,
  "risk_explanation": "1-2 sentences explaining the risk score",
  "plain_summary": "2-3 sentences in plain English — no jargon",
  "who_its_good_for": "1 sentence describing the ideal policyholder for this plan",
  "potential_savings": "Specific savings tip if you see one, or 'None identified'"
}}

COVERAGE AREAS — pick based on policy_type and make values sum to 100:
- Health: Medical, Prescription, Mental Health, Dental, Vision
- Auto: Liability, Collision, Comprehensive, Medical, Uninsured Motorist
- Home: Dwelling, Personal Property, Liability, Additional Living Expenses
- Renters: Personal Property, Liability, Additional Living Expenses, Medical Payments
- Life: Death Benefit, Riders, Cash Value
- Other: make reasonable categories

RISK SCORE GUIDE:
1-3 = Excellent (broad coverage, low deductible, few exclusions)
4-6 = Average (some gaps or high deductible worth watching)
7-10 = High risk (major exclusions, very high out-of-pocket, or thin coverage)

POLICY TEXT:
{text}"""

    resp = c.chat.completions.create(
        model=GEMINI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=1800,
    )
    raw = resp.choices[0].message.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


# ─── Q&A ─────────────────────────────────────────────────────────────────────

def ask_policy_question(
    question: str,
    policy_text: str,
    api_key: str,
    chat_history: list = None,
) -> str:
    c = _client(api_key)

    system = f"""You are PolicyPal — a friendly, expert insurance assistant. You answer questions ONLY based on the policy document provided below.

Rules:
1. Only state facts found in the policy text. If something is not mentioned, say so clearly.
2. Cite the relevant section or page whenever possible (e.g. "Section 4.2 states...").
3. Use plain English. Define any insurance term you must use.
4. For scenario questions ("Will my plan cover X?"), reason step by step before concluding.
5. End every scenario answer with: "I recommend confirming directly with your insurer before making a decision."
6. Be concise — aim for 3-6 sentences unless a scenario requires more detail.

POLICY DOCUMENT:
{policy_text[:12000]}"""

    messages = [{"role": "system", "content": system}]
    if chat_history:
        messages.extend(chat_history[-6:])
    messages.append({"role": "user", "content": question})

    resp = c.chat.completions.create(
        model=GEMINI_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=800,
    )
    return resp.choices[0].message.content



