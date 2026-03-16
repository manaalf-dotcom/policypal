"""
compare_policies.py — PolicyPal v2
Visual, structured comparison of two insurance policies.
Replaces the previous basic comparison module.
"""
import json
import openai
import plotly.graph_objects as go

# The 6 dimensions used in the radar chart and scoring table
DIMENSIONS = [
    "Coverage Completeness",
    "Affordability",
    "Flexibility",
    "Exclusion Risk",
    "Ease of Claims",
    "Overall Value",
]


# ─── LLM COMPARISON ──────────────────────────────────────────────────────────

def compare_policies_llm(analysis_a: dict, analysis_b: dict, api_key: str) -> dict:
    """
    Use GPT-4o to compare two analyzed policies across 6 dimensions.
    Returns a structured comparison dict.
    """
    c = openai.OpenAI(api_key=api_key)

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
    "Coverage Completeness": "A" | "B" | "Tie",
    "Affordability": "A" | "B" | "Tie",
    "Flexibility": "A" | "B" | "Tie",
    "Exclusion Risk": "A" | "B" | "Tie",
    "Ease of Claims": "A" | "B" | "Tie",
    "Overall Value": "A" | "B" | "Tie"
  }},
  "overall_winner": "A" | "B" | "Tie",
  "overall_score_a": 1_to_10,
  "overall_score_b": 1_to_10,
  "overall_winner_reason": "2–3 plain-English sentences explaining why",
  "best_for": {{
    "Young and healthy": "A" | "B",
    "Families with children": "A" | "B",
    "Chronic conditions": "A" | "B",
    "Budget-conscious": "A" | "B"
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
        model="gpt-4o",
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
    """Build a Plotly radar (spider) chart from comparison dimension scores."""
    dims = DIMENSIONS
    scores_a = [comparison["dimension_scores"][d]["a"] for d in dims]
    scores_b = [comparison["dimension_scores"][d]["b"] for d in dims]

    # Close the polygon by repeating the first value
    sa = scores_a + [scores_a[0]]
    sb = scores_b + [scores_b[0]]
    dc = dims + [dims[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=sa, theta=dc, fill="toself", name=name_a,
        line=dict(color="#3B82F6", width=2.5),
        fillcolor="rgba(59,130,246,0.15)",
        marker=dict(size=7, color="#3B82F6"),
    ))
    fig.add_trace(go.Scatterpolar(
        r=sb, theta=dc, fill="toself", name=name_b,
        line=dict(color="#10B981", width=2.5),
        fillcolor="rgba(16,185,129,0.15)",
        marker=dict(size=7, color="#10B981"),
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickvals=[2, 4, 6, 8, 10],
                tickfont=dict(size=9),
                gridcolor="rgba(128,128,128,0.15)",
                linecolor="rgba(128,128,128,0.2)",
            ),
            angularaxis=dict(tickfont=dict(size=11)),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2,
            xanchor="center", x=0.5, font=dict(size=11),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=50, t=20, b=70),
        height=400,
    )
    return fig
