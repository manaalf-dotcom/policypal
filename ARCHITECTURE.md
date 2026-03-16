# Architecture — PolicyPal

## System Overview

PolicyPal follows a retrieval-first design. Every response is grounded in the uploaded policy document — the LLM never generates financial claims from general knowledge.

```
User uploads PDF
      │
      ▼
┌─────────────────┐
│  PDF Extraction │  pdfplumber → plain text (max 20,000 chars)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GPT-4o Analysis│  Structured JSON extraction via prompt
│  (auto_analysis)│  → policy_type, deductible, premium, OOP max,
│                 │    coverage_areas, benefits, exclusions,
│                 │    risk_score, risk_flags, plain_summary
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Streamlit UI   │  Renders dashboard, charts, chat
│  (app.py)       │  3 tabs: Dashboard · Compare · Ask Pal
└─────────────────┘
```

## Module Breakdown

### `app.py`
- Streamlit page routing (Dashboard / Compare / Ask Pal)
- Custom CSS — deep purple/blue gradient theme, Pal SVG avatar
- Plotly chart rendering (donut, trend line, radar)
- Session state management

### `auto_analysis.py`
Three functions:
1. `extract_pdf_text(file)` — pdfplumber → raw text, truncated to 20k chars
2. `analyze_policy_document(text, api_key)` — GPT-4o prompt returning structured JSON
3. `ask_policy_question(question, text, api_key, history)` — multi-turn RAG Q&A

### `compare_policies.py`
Two functions:
1. `compare_policies_llm(an_a, an_b, api_key)` — GPT-4o comparison returning dimension scores, winners, best-for matrix
2. `build_radar_chart(comparison, na, nb)` — Plotly radar chart

## Anti-Hallucination Design

- All analysis prompts instruct the model to return "Not found" rather than infer missing values
- Q&A system prompt explicitly forbids answers not grounded in the document text
- Temperature set to 0 for all structured extraction calls
- Source citation required in every Q&A response

## Data Privacy

- Documents are processed in-session only — never stored, never logged
- API key lives in Streamlit Secrets — never exposed to users or in code
- No user authentication required; all state is session-scoped
