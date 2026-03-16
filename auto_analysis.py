"""
auto_analysis.py — PolicyPal v2
Extracts structured insight from uploaded insurance PDFs automatically.
"""
import json
import io
import pdfplumber
import openai


# ─── TEXT EXTRACTION ──────────────────────────────────────────────────────────

def extract_pdf_text(uploaded_file, max_chars: int = 20000) -> str:
    """Extract plain text from a Streamlit UploadedFile PDF."""
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
    full = "\n".join(text_parts)
    return full[:max_chars]


# ─── POLICY ANALYSIS ─────────────────────────────────────────────────────────

def analyze_policy_document(text: str, api_key: str) -> dict:
    """
    Call GPT-4o to extract structured insight from policy text.
    Returns a dict with all key policy fields.
    """
    c = openai.OpenAI(api_key=api_key)

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
  "risk_explanation": "1–2 sentences explaining the risk score",
  "plain_summary": "2–3 sentences in plain English — no jargon",
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
1–3 = Excellent (broad coverage, low deductible, few exclusions)
4–6 = Average (some gaps or high deductible worth watching)
7–10 = High risk (major exclusions, very high out-of-pocket, or thin coverage)

POLICY TEXT:
{text}"""

    resp = c.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=1800,
    )
    raw = resp.choices[0].message.content.strip()
    # Strip any accidental markdown fences
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


# ─── Q&A ─────────────────────────────────────────────────────────────────────

def ask_policy_question(
    question: str,
    policy_text: str,
    api_key: str,
    chat_history: list = None,
) -> str:
    """
    Answer a user question grounded strictly in the uploaded policy text.
    Maintains multi-turn conversation history.
    """
    c = openai.OpenAI(api_key=api_key)

    system = f"""You are PolicyPal — a friendly, expert insurance assistant. You answer questions ONLY based on the policy document provided below.

Rules:
1. Only state facts found in the policy text. If something is not mentioned, say so clearly.
2. Cite the relevant section or page whenever possible (e.g. "Section 4.2 states...").
3. Use plain English. Define any insurance term you must use.
4. For scenario questions ("Will my plan cover X?"), reason step by step before concluding.
5. End every scenario answer with: "I recommend confirming directly with your insurer before making a decision."
6. Be concise — aim for 3–6 sentences unless a scenario requires more detail.

POLICY DOCUMENT:
{policy_text[:12000]}"""

    messages = [{"role": "system", "content": system}]
    if chat_history:
        # Include last 3 turns (6 messages) for context
        messages.extend(chat_history[-6:])
    messages.append({"role": "user", "content": question})

    resp = c.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
        max_tokens=800,
    )
    return resp.choices[0].message.content
