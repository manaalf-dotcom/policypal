"""
compare_policies.py — PolicyPal v3
Uses Google Gemini via the official google-generativeai SDK.
"""
import json
import google.generativeai as genai
import plotly.graph_objects as go

GEMINI_MODEL = "gemini-1.5-flash"

DIMENSIONS = [
    "Coverage Completeness",
    "Affordability",
    "Flexibility",
    "Exclusion Risk",
    "Ease of Claims",
    "Overall Value",
]


def _client(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_MODEL)


def compare_policies_llm(analysis_a: dict, analysis_b: dict, api_key: str) -> dict:
    model = _client(api_key)

    prompt = f"""You are an expert, impartial insurance advisor comparing two policies side by side.

POLICY A ANALYSIS:
{json.dumps(analysis_a, indent=2)}

POLICY B ANALYSIS:
{json.dumps(analysis_b, indent=2)}

Return ONLY a valid JSON object — no markdown fences, no extra text — using this exact schema:
{{
  "dimension_scores": {{
    "Coverage Completeness": {{"a": 1_to_10, "b": 1_to_10}},
    "Affordability":          {{"a": 1_to_10, "b": 1_to_10}},
    "Flexibility":            {{"a": 1_to_10, "b": 1_to_10}},
    "Exclusion Risk":         {{"a": 1_to_10, "b": 1_to_10}},
    "Ease of Claims":         {{"a": 1_to_10, "b": 1_to_10}},
    "Overall Value":          {{"a": 1_to_10, "b": 1_to_10}}
  }},
  "category_winners": {{
    "Coverage Completeness": "A or B or Tie",
    "Affordability": "A or B or Tie",
    "Flexibility": "A or B or Tie",
    "Exclusion Risk": "A or B or Tie",
    "Ease of Claims": "A or B or Tie",
    "Overall Value": "A or B or Tie"
  }},
  "overall_winner": "A or B or Tie",
  "overall_score_a": 1_to_10,
  "overall_score_b": 1_to_10,
  "overall_winner_reason": "2-3 plain-English sentences explaining why",
  "best_for": {{
    "Young and healthy": "A or B",
    "Families with children": "A or B",
    "Chronic conditions": "A or B",
    "Budget-conscious": "A or B"
  }},
  "key_tradeoffs": ["3 specific tradeoffs between the two plans"],
  "a_advantages": ["3 specific advantages of Policy A"],
  "b_advantages": ["3 specific advantages of Policy B"],
  "red_flag_a": "Single most important concern about Policy A, or null",
  "red_flag_b": "Single most important concern about Policy B, or null"
}}"""

    resp = model.generate_content(prompt)
    raw = resp.text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


def build_radar_chart(comparison: dict, name_a: str = "Policy A", name_b: str = "Policy B") -> go.Figure:
    dims = DIMENSIONS
    scores_a = [comparison["dimension_scores"][d]["a"] for d in dims]
    scores_b = [comparison["dimension_scores"][d]["b"] for d in dims]
    sa = scores_a + [scores_a[0]]
    sb = scores_b + [scores_b[0]]
    dc = dims + [dims[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=sa, theta=dc, fill="toself", name=name_a,
        line=dict(color="#6366F1", width=3), fillcolor="rgba(99,102,241,0.25)",
        marker=dict(size=7, color="#6366F1")))
    fig.add_trace(go.Scatterpolar(r=sb, theta=dc, fill="toself", name=name_b,
        line=dict(color="#06B6D4", width=3), fillcolor="rgba(6,182,212,0.2)",
        marker=dict(size=7, color="#06B6D4")))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], tickvals=[2,4,6,8,10],
                            tickfont=dict(size=10, color="#7B6FA0"),
                            gridcolor="rgba(255,255,255,0.08)", linecolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(tickfont=dict(size=13, family="Plus Jakarta Sans", color="#C4B5FD")),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5,
                    font=dict(size=13, color="#C4B5FD"), bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=40, r=40, t=20, b=80), height=450,
    )
    return fig

