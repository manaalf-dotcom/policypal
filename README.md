# 🛡️ PolicyPal — AI-Powered Insurance Intelligence

> Upload any insurance policy PDF and instantly understand your coverage, exclusions, risk score, and how it compares — in plain English, no jargon.

**Live Demo:** [your-app.streamlit.app](https://your-app.streamlit.app)

---

## What It Does

PolicyPal is a production-ready AI web application that helps consumers understand insurance policies before making decisions. The app uses Retrieval-Augmented Generation (RAG) to analyze uploaded PDF documents and surface key information automatically.

**On upload, PolicyPal instantly shows you:**
- Deductible, premium, and out-of-pocket maximum
- Coverage breakdown donut chart
- Plain-English summary with zero jargon
- Key benefits vs exclusions side-by-side
- Risk score (1–10) with color-coded severity
- Specific risk flags with actionable explanations
- Potential savings tips

**Compare two policies:**
- Radar chart across 6 dimensions
- Dimension-by-dimension bar comparison
- Overall winner with reasoning
- "Best for…" matrix by user profile

**Ask Pal anything:**
- Multi-turn chat grounded strictly in your uploaded policy
- Source citations for every answer
- Quick-question chips per policy type

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit + custom CSS |
| AI / LLM | Google Gemini 2.0 Flash |
| RAG Pipeline | Custom chunking + semantic retrieval |
| PDF Parsing | pdfplumber |
| Charts | Plotly |
| Deployment | Streamlit Cloud |

---

## Project Structure

```
PolicyPal/
├── app.py                  # Main Streamlit application
├── auto_analysis.py        # PDF extraction, policy analysis, Q&A
├── compare_policies.py     # Policy comparison logic + radar chart
├── requirements.txt        # Python dependencies
├── .gitignore
├── README.md
├── ARCHITECTURE.md
├── SETUP.md
├── USER_GUIDE.md
├── TEAM_CONTRIBUTIONS.md
└── LICENSE
```

---

## Quick Start

See [SETUP.md](SETUP.md) for full installation instructions.

```bash
git clone https://github.com/your-username/PolicyPal
cd PolicyPal
pip install -r requirements.txt
echo 'GEMINI_API_KEY = "your-key-here"' > .streamlit/secrets.toml
streamlit run app.py
```

---

## Course Concepts Applied

- **RAG (Retrieval-Augmented Generation)** — all answers grounded in uploaded policy text
- **Embeddings** — semantic chunking and retrieval
- **Prompt Engineering** — citation-enforced responses, anti-hallucination guards
- **Intent Classification** — queries routed to appropriate response templates

---

## Team

Group 9 — NLP Course Project, UC Irvine
