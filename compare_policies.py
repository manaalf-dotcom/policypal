"""
compare_policies.py — PolicyPal v3
Uses Google Gemini via the OpenAI-compatible endpoint.
"""
import json
import openai
import plotly.graph_objects as go

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL = "gemini-1.5-flash"

DIMENSIONS = [
    "Coverage Completeness",
    "Affordability",
    "Flexibility",
    "Exclusion Risk",
    "Ease of Claims",
    "Overall Value",
]


def _client(api_key: str) -> openai.OpenAI:
    return openai.OpenAI(api_key=api_key, base_url=GEMINI_BASE_URL)


# ─── LLM COMPARISON ──────────────────────────────────────────────────────────

def compare_policies_llm(analysis_a: dict, analysis_b: dict, api_key: str) -> dict:
    c = _client(api_key)

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
}}

SCORING GUIDE (10 = best):
- Coverage Completeness: How broadly does it cover typical needs?
- Affordability: Lower deductible + premium relative to coverage = higher score
- Flexibility: Network breadth, out-of-area coverage, provider choice
- Exclusion Risk: Fewer exclusions = higher score (10 = almost none)
- Ease of Claims: Simpler, faster, more transparent = higher
- Overall Value: Best combination of coverage and cost

Be specific and grounded in the actual policy data provided. Do not invent facts."""

    resp = c.chat.completions.create(
        model=GEMINI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=1500,
    )
    raw = resp.choices[0].message.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


# ─── RADAR CHART ─────────────────────────────────────────────────────────────

def build_radar_chart(
    comparison: dict,
    name_a: str = "Policy A",
    name_b: str = "Policy B",
) -> go.Figure:
    dims = DIMENSIONS
    scores_a = [comparison["dimension_scores"][d]["a"] for d in dims]
    scores_b = [comparison["dimension_scores"][d]["b"] for d in dims]
    sa = scores_a + [scores_a[0]]
    sb = scores_b + [scores_b[0]]
    dc = dims + [dims[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=sa, theta=dc, fill="toself", name=name_a,
        line=dict(color="#A78BFA", width=2.5),
        fillcolor="rgba(167,139,250,0.15)",
        marker=dict(size=7, color="#A78BFA"),
    ))
    fig.add_trace(go.Scatterpolar(
        r=sb, theta=dc, fill="toself", name=name_b,
        line=dict(color="#38BDF8", width=2.5),
        fillcolor="rgba(56,189,248,0.12)",
        marker=dict(size=7, color="#38BDF8"),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 10], tickvals=[2, 4, 6, 8, 10],
                tickfont=dict(size=9), gridcolor="rgba(255,255,255,0.08)",
                linecolor="rgba(255,255,255,0.1)",
            ),
            angularaxis=dict(tickfont=dict(size=11, color="#A89FCC")),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2,
                    xanchor="center", x=0.5, font=dict(size=11, color="#A89FCC")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=50, t=20, b=70),
        height=400,
    )
    return fig

