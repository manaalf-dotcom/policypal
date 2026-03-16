"""
PolicyPal v4.0 — Figma layout-accurate, dark purple theme
"""
import streamlit as st
import os
import pathlib

st.set_page_config(
    page_title="PolicyPal — Your Insurance, Simplified",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import pathlib
_css = pathlib.Path("styles.css").read_text()
_fonts = '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
st.markdown(_fonts, unsafe_allow_html=True)
st.markdown(f"<style>{_css}</style>", unsafe_allow_html=True)

def _get_api_key():
    try:
        k = st.secrets.get("GEMINI_API_KEY", "")
        if k: return k
    except Exception:
        pass
    k = os.environ.get("GEMINI_API_KEY", "")
    if k: return k
    st.error("⚠️ Add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

API_KEY = _get_api_key()

from auto_analysis import extract_pdf_text, analyze_policy_document, ask_policy_question
from compare_policies import compare_policies_llm, build_radar_chart, DIMENSIONS
import plotly.graph_objects as go

for k, v in {
    "page": "dashboard",
    "analysis": None, "policy_text": None, "last_file": None,
    "chat_history": [],
    "cmp_an_a": None, "cmp_an_b": None,
    "comparison": None, "cmp_name_a": "Policy A", "cmp_name_b": "Policy B",
    "is_typing": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── PAL SVG ───────────────────────────────────────────────────────────────────
def pal_svg(size=44, state="default"):
    s = size
    h = int(s * 1.2)
    if state == "alert":
        grad = f'<linearGradient id="pg{s}{state}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#DC2626"/><stop offset="100%" stop-color="#F97316"/></linearGradient>'
    elif state in ("positive", "happy"):
        grad = f'<linearGradient id="pg{s}{state}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#4F46E5"/><stop offset="100%" stop-color="#06B6D4"/></linearGradient>'
    elif state == "analyzing":
        grad = f'<linearGradient id="pg{s}{state}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#6D28D9"/><stop offset="100%" stop-color="#0284C7"/></linearGradient>'
    else:
        grad = f'<linearGradient id="pg{s}{state}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#4F46E5"/><stop offset="100%" stop-color="#7C3AED"/></linearGradient>'

    shield = (f'<path d="M{s*.5} {s*.04} C{s*.5} {s*.04} {s*.94} {s*.15} {s*.97} {s*.22} '
              f'L{s*.97} {s*.5} C{s*.97} {s*.78} {s*.5} {s*1.15} {s*.5} {s*1.15} '
              f'C{s*.5} {s*1.15} {s*.03} {s*.78} {s*.03} {s*.5} '
              f'L{s*.03} {s*.22} C{s*.06} {s*.15} {s*.5} {s*.04} {s*.5} {s*.04}Z" fill="url(#pg{s}{state})"/>')
    inner = (f'<path d="M{s*.5} {s*.1} C{s*.5} {s*.1} {s*.88} {s*.2} {s*.9} {s*.26} '
             f'L{s*.9} {s*.5} C{s*.9} {s*.72} {s*.5} {s*1.08} {s*.5} {s*1.08} '
             f'C{s*.5} {s*1.08} {s*.1} {s*.72} {s*.1} {s*.5} '
             f'L{s*.1} {s*.26} C{s*.12} {s*.2} {s*.5} {s*.1} {s*.5} {s*.1}Z" '
             f'fill="none" stroke="rgba(255,255,255,0.16)" stroke-width="{s*.014}" stroke-dasharray="3 3"/>')

    if state == "alert":
        emblem = (f'<path d="M{s*.38} {s*.28} L{s*.5} {s*.1} L{s*.62} {s*.28}Z" fill="rgba(255,255,255,0.25)" stroke="rgba(255,255,255,0.5)" stroke-width="{s*.015}"/>'
                  f'<rect x="{s*.478}" y="{s*.13}" width="{s*.044}" height="{s*.08}" rx="{s*.015}" fill="rgba(255,255,255,0.8)"/>'
                  f'<circle cx="{s*.5}" cy="{s*.26}" r="{s*.022}" fill="rgba(255,255,255,0.8)"/>')
    elif state in ("positive", "happy"):
        emblem = (f'<polygon points="{s*.5},{s*.09} {s*.53},{s*.18} {s*.63},{s*.18} {s*.56},{s*.24} '
                  f'{s*.58},{s*.33} {s*.5},{s*.28} {s*.42},{s*.33} {s*.44},{s*.24} {s*.37},{s*.18} {s*.47},{s*.18}" '
                  f'fill="rgba(255,255,255,0.45)"/>')
    elif state == "analyzing":
        emblem = (f'<circle cx="{s*.36}" cy="{s*.2}" r="{s*.04}" fill="rgba(255,255,255,0.55)"/>'
                  f'<circle cx="{s*.5}" cy="{s*.18}" r="{s*.04}" fill="rgba(255,255,255,0.75)"/>'
                  f'<circle cx="{s*.64}" cy="{s*.2}" r="{s*.04}" fill="rgba(255,255,255,0.55)"/>')
    else:
        emblem = (f'<circle cx="{s*.5}" cy="{s*.2}" r="{s*.1}" fill="rgba(255,255,255,0.18)" stroke="rgba(255,255,255,0.35)" stroke-width="{s*.012}"/>'
                  f'<path d="M{s*.42} {s*.2} L{s*.48} {s*.26} L{s*.58} {s*.16}" stroke="white" stroke-width="{s*.03}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

    ey = s * 0.52
    elx, erx = s * 0.33, s * 0.67
    ew, eh = s * 0.105, s * 0.115

    if state in ("positive", "happy"):
        eyes = (f'<path d="M{s*.22} {ey} Q{elx} {s*.44} {s*.44} {ey}" stroke="#1A0F3C" stroke-width="{s*.05}" fill="rgba(255,255,255,0.9)" stroke-linecap="round"/>'
                f'<path d="M{s*.56} {ey} Q{erx} {s*.44} {s*.78} {ey}" stroke="#1A0F3C" stroke-width="{s*.05}" fill="rgba(255,255,255,0.9)" stroke-linecap="round"/>'
                f'<ellipse cx="{s*.19}" cy="{s*.62}" rx="{s*.07}" ry="{s*.05}" fill="rgba(255,180,180,0.3)"/>'
                f'<ellipse cx="{s*.81}" cy="{s*.62}" rx="{s*.07}" ry="{s*.05}" fill="rgba(255,180,180,0.3)"/>')
    elif state == "alert":
        eyes = (f'<ellipse cx="{elx}" cy="{ey}" rx="{ew*1.1}" ry="{eh*1.1}" fill="white"/>'
                f'<ellipse cx="{erx}" cy="{ey}" rx="{ew*1.1}" ry="{eh*1.1}" fill="white"/>'
                f'<circle cx="{elx}" cy="{ey}" r="{s*.075}" fill="#7F1D1D"/>'
                f'<circle cx="{erx}" cy="{ey}" r="{s*.075}" fill="#7F1D1D"/>'
                f'<circle cx="{elx}" cy="{ey}" r="{s*.042}" fill="#1A0F3C"/>'
                f'<circle cx="{erx}" cy="{ey}" r="{s*.042}" fill="#1A0F3C"/>'
                f'<circle cx="{elx+s*.02}" cy="{ey-s*.02}" r="{s*.02}" fill="white"/>'
                f'<circle cx="{erx+s*.02}" cy="{ey-s*.02}" r="{s*.02}" fill="white"/>')
    elif state == "analyzing":
        eyes = (f'<ellipse cx="{elx}" cy="{ey}" rx="{ew}" ry="{eh}" fill="white"/>'
                f'<ellipse cx="{erx}" cy="{ey}" rx="{ew}" ry="{eh}" fill="white"/>'
                f'<circle cx="{elx}" cy="{ey}" r="{s*.07}" fill="#4C1D95"/>'
                f'<circle cx="{erx}" cy="{ey}" r="{s*.07}" fill="#4C1D95"/>'
                f'<circle cx="{elx+s*.02}" cy="{ey-s*.025}" r="{s*.038}" fill="#1A0F3C"/>'
                f'<circle cx="{erx+s*.02}" cy="{ey-s*.025}" r="{s*.038}" fill="#1A0F3C"/>'
                f'<circle cx="{elx+s*.035}" cy="{ey-s*.04}" r="{s*.018}" fill="white"/>'
                f'<circle cx="{erx+s*.035}" cy="{ey-s*.04}" r="{s*.018}" fill="white"/>')
    else:
        eyes = (f'<ellipse cx="{elx}" cy="{ey}" rx="{ew}" ry="{eh}" fill="white"/>'
                f'<ellipse cx="{erx}" cy="{ey}" rx="{ew}" ry="{eh}" fill="white"/>'
                f'<circle cx="{elx}" cy="{ey}" r="{s*.07}" fill="#3730A3"/>'
                f'<circle cx="{erx}" cy="{ey}" r="{s*.07}" fill="#3730A3"/>'
                f'<circle cx="{elx+s*.01}" cy="{ey}" r="{s*.038}" fill="#1A0F3C"/>'
                f'<circle cx="{erx+s*.01}" cy="{ey}" r="{s*.038}" fill="#1A0F3C"/>'
                f'<circle cx="{elx+s*.025}" cy="{ey-s*.03}" r="{s*.02}" fill="white"/>'
                f'<circle cx="{erx+s*.025}" cy="{ey-s*.03}" r="{s*.02}" fill="white"/>')

    by = s * 0.42
    if state == "alert":
        brows = (f'<path d="M{s*.2} {by-s*.02} Q{elx} {by-s*.06} {s*.44} {by}" stroke="#1A0F3C" stroke-width="{s*.028}" fill="none" stroke-linecap="round"/>'
                 f'<path d="M{s*.56} {by} Q{erx} {by-s*.06} {s*.8} {by-s*.02}" stroke="#1A0F3C" stroke-width="{s*.028}" fill="none" stroke-linecap="round"/>')
    elif state in ("positive", "happy"):
        brows = (f'<path d="M{s*.21} {by-s*.04} Q{elx} {by-s*.09} {s*.44} {by-s*.04}" stroke="#1A0F3C" stroke-width="{s*.024}" fill="none" stroke-linecap="round"/>'
                 f'<path d="M{s*.56} {by-s*.04} Q{erx} {by-s*.09} {s*.79} {by-s*.04}" stroke="#1A0F3C" stroke-width="{s*.024}" fill="none" stroke-linecap="round"/>')
    elif state == "analyzing":
        brows = (f'<path d="M{s*.21} {by-s*.05} Q{elx} {by-s*.1} {s*.44} {by-s*.02}" stroke="#1A0F3C" stroke-width="{s*.024}" fill="none" stroke-linecap="round"/>'
                 f'<path d="M{s*.56} {by} Q{erx} {by-s*.06} {s*.79} {by}" stroke="#1A0F3C" stroke-width="{s*.024}" fill="none" stroke-linecap="round"/>')
    else:
        brows = (f'<path d="M{s*.21} {by} Q{elx} {by-s*.06} {s*.44} {by}" stroke="#1A0F3C" stroke-width="{s*.025}" fill="none" stroke-linecap="round"/>'
                 f'<path d="M{s*.56} {by} Q{erx} {by-s*.06} {s*.79} {by}" stroke="#1A0F3C" stroke-width="{s*.025}" fill="none" stroke-linecap="round"/>')

    my = s * 0.76
    if state == "alert":
        mouth = f'<path d="M{s*.28} {my} Q{s*.36} {my-s*.05} {s*.5} {my+s*.02} Q{s*.64} {my+s*.09} {s*.72} {my+s*.04}" stroke="#1A0F3C" stroke-width="{s*.032}" fill="none" stroke-linecap="round"/>'
    elif state in ("positive", "happy"):
        mouth = f'<path d="M{s*.22} {my-s*.02} Q{s*.5} {my+s*.12} {s*.78} {my-s*.02}" stroke="#1A0F3C" stroke-width="{s*.038}" fill="rgba(26,15,60,0.18)" stroke-linecap="round"/>'
    elif state == "analyzing":
        mouth = f'<path d="M{s*.3} {my} Q{s*.5} {my+s*.04} {s*.7} {my}" stroke="#1A0F3C" stroke-width="{s*.028}" fill="none" stroke-linecap="round"/>'
    else:
        mouth = f'<path d="M{s*.3} {my-s*.01} Q{s*.5} {my+s*.09} {s*.7} {my-s*.01}" stroke="#1A0F3C" stroke-width="{s*.034}" fill="rgba(26,15,60,0.1)" stroke-linecap="round"/>'

    cheeks = ""
    if state in ("positive", "happy"):
        cheeks = (f'<ellipse cx="{s*.19}" cy="{s*.65}" rx="{s*.08}" ry="{s*.055}" fill="rgba(255,180,180,0.22)"/>'
                  f'<ellipse cx="{s*.81}" cy="{s*.65}" rx="{s*.08}" ry="{s*.055}" fill="rgba(255,180,180,0.22)"/>')

    extras = ""
    if state == "analyzing":
        extras = f'<circle cx="{s*.5}" cy="{s*1.22}" r="{s*1.18}" fill="none" stroke="rgba(129,140,248,0.2)" stroke-width="{s*.02}" stroke-dasharray="4 7"/>'
    elif state in ("positive", "happy"):
        extras = (f'<line x1="{s*.06}" y1="{s*.35}" x2="{s*.12}" y2="{s*.35}" stroke="#818CF8" stroke-width="{s*.025}" opacity="0.85"/>'
                  f'<line x1="{s*.09}" y1="{s*.32}" x2="{s*.09}" y2="{s*.38}" stroke="#818CF8" stroke-width="{s*.025}" opacity="0.85"/>'
                  f'<line x1="{s*.88}" y1="{s*.28}" x2="{s*.94}" y2="{s*.28}" stroke="#38BDF8" stroke-width="{s*.025}" opacity="0.85"/>'
                  f'<line x1="{s*.91}" y1="{s*.25}" x2="{s*.91}" y2="{s*.31}" stroke="#38BDF8" stroke-width="{s*.025}" opacity="0.85"/>')

    return (f'<svg width="{s}" height="{h}" viewBox="0 0 {s} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs>{grad}</defs>'
            f'{extras}{shield}{inner}{emblem}{eyes}{brows}{mouth}{cheeks}'
            f'</svg>')


def chk():
    return '<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 6L4.5 8.5L10 3" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def xcl():
    return '<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 2L10 10M10 2L2 10" stroke="white" stroke-width="2.2" stroke-linecap="round"/></svg>'

def sparkle():
    return '<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M6 1L7 5L11 6L7 7L6 11L5 7L1 6L5 5Z" fill="#A78BFA"/></svg>'


# ── CHARTS ────────────────────────────────────────────────────────────────────
def donut_chart(areas):
    labels = list(areas.keys())
    values = list(areas.values())
    colors = ["#6366F1", "#8B5CF6", "#06B6D4", "#10B981", "#F59E0B", "#EF4444"]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.58,
        marker=dict(colors=colors[:len(labels)], line=dict(color="rgba(26,15,60,0.5)", width=3)),
        textinfo="label+percent",
        textfont=dict(size=11, family="Plus Jakarta Sans", color="rgba(238,232,255,0.9)"),
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5,
                    font=dict(size=11, family="Plus Jakarta Sans", color="#A89FCC")),
        margin=dict(l=0, r=0, t=10, b=50),
        paper_bgcolor="rgba(0,0,0,0)", height=280,
    )
    return fig


def trend_chart():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    vals = [420, 435, 450, 448, 452, 450]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=vals, mode="lines+markers",
        line=dict(color="#6366F1", width=3, shape="spline"),
        marker=dict(color="#6366F1", size=8, line=dict(color="rgba(26,15,60,0.8)", width=2)),
        fill="tozeroy", fillcolor="rgba(99,102,241,0.1)",
        hovertemplate="<b>%{x}</b><br>$%{y}/mo<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(showgrid=False, tickfont=dict(size=11, family="Plus Jakarta Sans", color="#A89FCC"),
                   linecolor="rgba(255,255,255,0.06)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)",
                   tickprefix="$", tickfont=dict(size=11, family="Plus Jakarta Sans", color="#A89FCC"),
                   range=[350, 500]),
        margin=dict(l=45, r=10, t=10, b=35),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=280,
    )
    return fig


def radar_fig(cmp, na, nb):
    dims = DIMENSIONS
    sa = [cmp["dimension_scores"][d]["a"] for d in dims] + [cmp["dimension_scores"][dims[0]]["a"]]
    sb = [cmp["dimension_scores"][d]["b"] for d in dims] + [cmp["dimension_scores"][dims[0]]["b"]]
    dc = dims + [dims[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=sa, theta=dc, fill="toself", name=na,
        line=dict(color="#6366F1", width=3), fillcolor="rgba(99,102,241,0.25)",
        marker=dict(size=7, color="#6366F1")))
    fig.add_trace(go.Scatterpolar(r=sb, theta=dc, fill="toself", name=nb,
        line=dict(color="#06B6D4", width=3), fillcolor="rgba(6,182,212,0.2)",
        marker=dict(size=7, color="#06B6D4")))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], tickvals=[2, 4, 6, 8, 10],
                            tickfont=dict(size=10, color="#7B6FA0"),
                            gridcolor="rgba(255,255,255,0.08)", linecolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(tickfont=dict(size=13, family="Plus Jakarta Sans", color="#C4B5FD")),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5,
                    font=dict(size=13, family="Plus Jakarta Sans", color="#C4B5FD"),
                    bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=40, r=40, t=20, b=80), height=450,
    )
    return fig


# ── NAV ───────────────────────────────────────────────────────────────────────
def render_nav():
    logo_col, c1, c2, c3 = st.columns([1.2, 1, 1, 1])
    with logo_col:
        st.markdown(f'<div class="pp-logo" style="height:44px;display:flex;align-items:center;gap:10px;padding-left:8px">{pal_svg(28)} PolicyPal</div>',
                    unsafe_allow_html=True)
    with c1:
        if st.button("📊  Dashboard", key="n1", use_container_width=True,
                     type="primary" if st.session_state.page == "dashboard" else "secondary"):
            st.session_state.page = "dashboard"; st.rerun()
    with c2:
        if st.button("⚖️  Compare", key="n2", use_container_width=True,
                     type="primary" if st.session_state.page == "compare" else "secondary"):
            st.session_state.page = "compare"; st.rerun()
    with c3:
        if st.button("💬  Ask Pal", key="n3", use_container_width=True,
                     type="primary" if st.session_state.page == "ask" else "secondary"):
            st.session_state.page = "ask"; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    an = st.session_state.analysis
    st.markdown('<div class="pp-page"><div class="orb-tr"></div><div class="orb-bl"></div>', unsafe_allow_html=True)

    # ── UPLOAD / HERO ─────────────────────────────────────────────────────────
    if an is None:
        st.markdown(f'''<div class="hero-wrap">
          <div class="hero-h">Your insurance,<br><span class="hero-grad">simplified.</span></div>
          <div class="hero-sub">Upload your policy PDF and get instant AI-powered insights<br>in plain English — no jargon, no confusion.</div>
        </div>''', unsafe_allow_html=True)

        uc, _ = st.columns([2, 1])
        with uc:
            st.markdown(f'''<div class="upload-zone-wrapper">
              <div class="upload-zone-inner">
                <div style="flex-shrink:0">{pal_svg(88)}</div>
                <div class="upload-card-text">
                  <h3>Drop your policy PDF here</h3>
                  <p>Or click to browse &nbsp;•&nbsp; Supports PDF up to 25MB<br>Health · Auto · Home · Renters · Life</p>
                </div>
              </div>
            </div>''', unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload your policy PDF", type=["pdf"],
                                        key="main_upload", label_visibility="collapsed")

        st.markdown('''<div class="chips">
          <div class="chip">📄 Plain-English summaries</div>
          <div class="chip">🛡️ Risk scoring &amp; alerts</div>
          <div class="chip">⚖️ Policy comparison</div>
          <div class="chip">✨ Instant AI analysis</div>
          <div class="chip">💬 Ask questions</div>
        </div>
        <div class="trust">
          <span>🔒 Bank-level encryption</span>
          <span>⚡ Analysis in seconds</span>
          <span>✦ Powered by AI</span>
        </div>''', unsafe_allow_html=True)

        if uploaded and uploaded.name != st.session_state.last_file:
            with st.spinner("✨ Analyzing your policy — about 15 seconds…"):
                uploaded.seek(0)
                text = extract_pdf_text(uploaded)
                st.session_state.policy_text = text
                st.session_state.analysis = analyze_policy_document(text, API_KEY)
                st.session_state.last_file = uploaded.name
                st.session_state.chat_history = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── POLICY BANNER ─────────────────────────────────────────────────────────
    ptype = an.get("policy_type", "Insurance").upper()
    rs = an.get("risk_score", 5)
    av_state = "alert" if rs >= 7 else ("positive" if rs <= 3 else "default")

    st.markdown(f'''<div class="policy-banner">
      <div class="banner-gradient-bar"></div>
      {pal_svg(52, av_state)}
      <span class="ptype-badge">{ptype} Insurance</span>
      <div>
        <div class="policy-name">{an.get("insurer", "Your Policy")}</div>
        <div class="policy-meta">Uploaded policy &nbsp;·&nbsp; <span class="active">Active</span></div>
      </div>
      <div class="analysis-done">
        <div class="lbl">✨ Analysis complete</div>
        <div class="sub">Processed in seconds</div>
      </div>
    </div>''', unsafe_allow_html=True)

    # ── STAT CARDS ────────────────────────────────────────────────────────────
    prem = an.get("monthly_premium") or an.get("annual_premium") or "—"
    rt = "Excellent" if rs <= 3 else ("Average" if rs <= 6 else "High Risk")
    rt_cls = "st-good" if rs <= 3 else "st-warn"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''<div class="stat-card sc-1">
          <div class="stat-top"><div class="stat-icon-wrap si-1">💲</div><span class="stat-tag st-warn">+12% vs avg</span></div>
          <div class="stat-label">Annual Deductible</div>
          <div class="stat-value">{an.get("deductible","—")}</div>
        </div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="stat-card sc-2">
          <div class="stat-top"><div class="stat-icon-wrap si-2">📈</div><span class="stat-tag st-good">Market rate</span></div>
          <div class="stat-label">Monthly Premium</div>
          <div class="stat-value">{prem}</div>
        </div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="stat-card sc-3">
          <div class="stat-top"><div class="stat-icon-wrap si-3">💊</div><span class="stat-tag st-warn">+8% vs avg</span></div>
          <div class="stat-label">Max Out-of-Pocket</div>
          <div class="stat-value">{an.get("out_of_pocket_max","—")}</div>
        </div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="stat-card sc-4">
          <div class="stat-top"><div class="stat-icon-wrap si-4">🛡️</div><span class="stat-tag {rt_cls}">{rt}</span></div>
          <div class="stat-label">Coverage Score</div>
          <div class="stat-value">{rs}/10</div>
        </div>''', unsafe_allow_html=True)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── CHARTS ────────────────────────────────────────────────────────────────
    lc, rc = st.columns(2)
    with lc:
        st.markdown('<div class="cc"><div class="cc-title">Coverage Breakdown</div>', unsafe_allow_html=True)
        areas = an.get("coverage_areas", {})
        if areas:
            st.plotly_chart(donut_chart(areas), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with rc:
        st.markdown('<div class="cc"><div class="cc-title">Premium Trend (6 months)</div>', unsafe_allow_html=True)
        st.plotly_chart(trend_chart(), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── PLAIN ENGLISH SUMMARY ─────────────────────────────────────────────────
    st.markdown(f'''<div class="summary-card">
      <div class="sum-header">{pal_svg(52, "default")}<div><h3>Plain English Summary</h3><p>Here's what you need to know about your policy</p></div></div>
      <div class="sum-text">{an.get("plain_summary","")}</div>
      <div class="ideal-for">💡 <strong>Ideal for:</strong> {an.get("who_its_good_for","")}</div>
    </div>''', unsafe_allow_html=True)

    savings = an.get("potential_savings", "")
    if savings and savings.lower() not in ("none identified", "none", ""):
        st.markdown(f'<div class="gap-sm"></div><div class="cc" style="border-color:rgba(56,189,248,0.25);background:rgba(6,182,212,0.08)"><div class="cc-title" style="color:#38BDF8">💰 Potential Savings Tip</div><p style="font-size:0.9rem;color:#BAE6FD;line-height:1.65">{savings}</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── BENEFITS + EXCLUSIONS ─────────────────────────────────────────────────
    lc2, rc2 = st.columns(2)
    with lc2:
        items = "".join([f'<div class="cov-item"><div class="ic-g">{chk()}</div><span>{b}</span></div>' for b in an.get("key_benefits", [])])
        st.markdown(f'<div class="cc"><div class="cc-title"><span class="dot-g"></span>What\'s Covered</div>{items}</div>', unsafe_allow_html=True)
    with rc2:
        items = "".join([f'<div class="cov-item excl"><div class="ic-o">{xcl()}</div><span>{e}</span></div>' for e in an.get("exclusions", [])])
        st.markdown(f'<div class="cc"><div class="cc-title"><span class="dot-o"></span>What\'s Not Covered</div>{items}</div>', unsafe_allow_html=True)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── RISK FLAGS ────────────────────────────────────────────────────────────
    flags = an.get("risk_flags", [])
    if flags:
        flags_html = ""
        for f in flags:
            parts = f.split(":", 1)
            title = parts[0].strip() if len(parts) > 1 else f
            desc = parts[1].strip() if len(parts) > 1 else an.get("risk_explanation", "")
            flags_html += f'<div class="flag-card"><div class="flag-icon">⚠️</div><div><div class="flag-title">{title}</div><div class="flag-desc">{desc}</div></div></div>'
        st.markdown(f'<div class="watch-h">{pal_svg(30, "alert")} Things to Watch Out For</div>{flags_html}', unsafe_allow_html=True)

    st.markdown('<div class="gap-lg"></div>', unsafe_allow_html=True)

    # ── CTA BUTTONS ───────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⚖️  Compare with other policies", key="g_cmp", type="primary", use_container_width=True):
            st.session_state.page = "compare"; st.rerun()
    with c2:
        if st.button("💬  Ask Pal a question", key="g_ask", use_container_width=True):
            st.session_state.page = "ask"; st.rerun()
    with c3:
        if st.button("📄  Analyze new policy", key="g_new", use_container_width=True):
            for k in ["analysis", "policy_text", "last_file"]:
                st.session_state[k] = None
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COMPARE
# ══════════════════════════════════════════════════════════════════════════════
def page_compare():
    st.markdown('<div class="pp-page"><div class="orb-tr"></div><div class="orb-bl"></div>', unsafe_allow_html=True)
    st.markdown('''<div style="text-align:center;padding:1.5rem 0 1.25rem;position:relative;z-index:1">
      <div class="cmp-headline">Policy <span>Comparison</span></div>
      <div class="cmp-sub">Head-to-head analysis of your options</div>
    </div>''', unsafe_allow_html=True)

    uc1, uc2 = st.columns(2)
    with uc1:
        st.markdown('<p style="font-weight:600;color:#A78BFA;margin-bottom:6px;position:relative;z-index:1">Policy A</p>', unsafe_allow_html=True)
        fa = st.file_uploader("Upload Policy A", type=["pdf"], key="cmp_a")
        na = st.text_input("Label for Policy A", value="Policy A", key="na")
    with uc2:
        st.markdown('<p style="font-weight:600;color:#38BDF8;margin-bottom:6px;position:relative;z-index:1">Policy B</p>', unsafe_allow_html=True)
        fb = st.file_uploader("Upload Policy B", type=["pdf"], key="cmp_b")
        nb = st.text_input("Label for Policy B", value="Policy B", key="nb")

    if fa and fb:
        if st.button("✨  Run Comparison", type="primary", use_container_width=True):
            with st.spinner("Analyzing both policies — about 30 seconds…"):
                fa.seek(0); fb.seek(0)
                ta = extract_pdf_text(fa); tb = extract_pdf_text(fb)
                an_a = analyze_policy_document(ta, API_KEY)
                an_b = analyze_policy_document(tb, API_KEY)
                cmp = compare_policies_llm(an_a, an_b, API_KEY)
                st.session_state.cmp_an_a = an_a
                st.session_state.cmp_an_b = an_b
                st.session_state.comparison = cmp
                st.session_state.cmp_name_a = na
                st.session_state.cmp_name_b = nb
            st.rerun()

    cmp = st.session_state.comparison
    if not cmp:
        st.markdown("</div>", unsafe_allow_html=True)
        return

    na = st.session_state.cmp_name_a
    nb = st.session_state.cmp_name_b
    winner = cmp.get("overall_winner", "Tie")
    sa = cmp.get("overall_score_a", 0)
    sb = cmp.get("overall_score_b", 0)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── VS SCORE PODS ─────────────────────────────────────────────────────────
    sc1, vsc, sc2 = st.columns([5, 1, 5])
    with sc1:
        wp = '<div class="pod-winner-badge">🏆 Overall Winner</div>' if winner == "A" else ""
        st.markdown(f'''<div class="score-pod pod-a">
          <div class="pod-gradient-bar" style="background:linear-gradient(90deg,#4F46E5,#7C3AED)"></div>
          {wp}
          <div class="pod-name">{na}</div>
          <div><span class="pod-score pod-score-a">{sa}</span><span class="pod-denom"> / 10</span></div>
          <div style="font-size:0.8rem;color:rgba(255,255,255,0.35);margin-top:5px">Overall Score</div>
        </div>''', unsafe_allow_html=True)
    with vsc:
        st.markdown('<div style="display:flex;align-items:center;height:100%;justify-content:center;padding-top:0.75rem"><div class="vs-circle"><div class="vs-inner">VS</div></div></div>', unsafe_allow_html=True)
    with sc2:
        rp = '<div class="pod-runner-badge">Runner Up</div>' if winner == "A" else ('<div class="pod-winner-badge">🏆 Overall Winner</div>' if winner == "B" else "")
        st.markdown(f'''<div class="score-pod pod-b">
          <div class="pod-gradient-bar" style="background:linear-gradient(90deg,#06B6D4,#38BDF8)"></div>
          {rp}
          <div class="pod-name">{nb}</div>
          <div><span class="pod-score pod-score-b">{sb}</span><span class="pod-denom"> / 10</span></div>
          <div style="font-size:0.8rem;color:rgba(255,255,255,0.35);margin-top:5px">Overall Score</div>
        </div>''', unsafe_allow_html=True)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── RADAR CHART ───────────────────────────────────────────────────────────
    st.markdown('<div class="cc"><div class="cc-title">Performance Comparison</div>', unsafe_allow_html=True)
    st.plotly_chart(radar_fig(cmp, na, nb), use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div><div class='gap-md'></div>", unsafe_allow_html=True)

    # ── DETAILED COMPARISON BARS ──────────────────────────────────────────────
    st.markdown('<div class="cc"><div class="cc-title">Detailed Comparison</div>', unsafe_allow_html=True)
    dim_scores = cmp.get("dimension_scores", {})
    cat_winners = cmp.get("category_winners", {})
    an_a = st.session_state.cmp_an_a or {}
    an_b = st.session_state.cmp_an_b or {}

    for dim in DIMENSIONS:
        sc = dim_scores.get(dim, {})
        va = sc.get("a", 5); vb = sc.get("b", 5)
        w = cat_winners.get(dim, "Tie")
        wn = na if w == "A" else (nb if w == "B" else "Tie")
        wc = "win-tag-a" if w == "A" else ("win-tag-b" if w == "B" else "win-tag-tie")
        pa = min(100, int(va / 10 * 100))
        pb = min(100, int(vb / 10 * 100))
        st.markdown(f'''<div class="dim-block">
          <div class="dim-header">
            <div class="dim-name">{dim}</div>
            <span class="{wc}">Winner: {wn}</span>
          </div>
          <div class="dim-row">
            <div class="dim-lbl" style="color:#818CF8">{na}</div>
            <div class="bar-track"><div class="bar-fill-a" style="width:{pa}%"></div></div>
            <div class="dim-val-a">{va}/10</div>
          </div>
          <div class="dim-row">
            <div class="dim-lbl" style="color:#38BDF8">{nb}</div>
            <div class="bar-track"><div class="bar-fill-b" style="width:{pb}%"></div></div>
            <div class="dim-val-b">{vb}/10</div>
          </div>
        </div>''', unsafe_allow_html=True)
    st.markdown("</div><div class='gap-md'></div>", unsafe_allow_html=True)

    # ── BEST FOR ──────────────────────────────────────────────────────────────
    best = cmp.get("best_for", {})
    if best:
        dots = {"A": "●", "B": "●"}
        cols_bf = ["from-indigo-500 to-purple-500", "from-cyan-500 to-blue-500"]
        cards = ""
        for scenario, wl in best.items():
            wname = na if wl == "A" else nb
            wc = "bf-win-a" if wl == "A" else "bf-win-b"
            dot_color = "#818CF8" if wl == "A" else "#38BDF8"
            cards += f'<div class="bf-card"><div class="bf-label"><span style="width:10px;height:10px;border-radius:50%;background:{dot_color};display:inline-block;box-shadow:0 0 8px {dot_color}80"></span>{scenario}</div><div class="{wc}">{wname}</div></div>'
        st.markdown(f'<div class="cc"><div class="cc-title">Best For…</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">{cards}</div></div>', unsafe_allow_html=True)
        st.markdown("<div class='gap-md'></div>", unsafe_allow_html=True)

    # ── PAL RECOMMENDATION ────────────────────────────────────────────────────
    reason = cmp.get("overall_winner_reason", "")
    wname = na if winner == "A" else nb
    if reason:
        adv_a = cmp.get("a_advantages", [])
        adv_b = cmp.get("b_advantages", [])
        badges = "".join([f'<span class="rec-badge">✓ {a}</span> ' for a in (adv_a if winner == "A" else adv_b)[:2]])
        st.markdown(f'''<div class="pal-rec" style="position:relative;z-index:1">
          <div style="display:flex;align-items:flex-start;gap:1rem">
            {pal_svg(52, "positive")}
            <div style="flex:1">
              <h3>Pal's Recommendation</h3>
              <p>Based on your policies, I recommend <span class="hi">{wname}</span>. {reason}</p>
              <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:1rem">{badges}</div>
            </div>
          </div>
        </div>''', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ASK PAL
# ══════════════════════════════════════════════════════════════════════════════
def page_ask():
    st.markdown('<div class="pp-page"><div class="orb-tr"></div><div class="orb-bl"></div>', unsafe_allow_html=True)

    if not st.session_state.policy_text:
        st.markdown(f'''<div class="no-policy">
          <div style="margin-bottom:1rem">{pal_svg(88, "analyzing")}</div>
          <h3>Upload a policy first</h3>
          <p>Head to Dashboard, upload your PDF,<br>then come back to ask Pal anything.</p>
        </div>''', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    an = st.session_state.analysis or {}
    ptype = an.get("policy_type", "Insurance")

    # ── HEADER ────────────────────────────────────────────────────────────────
    st.markdown(f'''<div style="text-align:center;padding:2rem 0 1.5rem;position:relative;z-index:1">
      <div style="font-size:3rem;font-weight:800;color:#EEE8FF;letter-spacing:-1px">
        Ask <span style="background:linear-gradient(135deg,#818CF8,#A78BFA,#38BDF8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">Pal</span>
      </div>
      <div style="font-size:1rem;color:#7B6FA0;margin-top:6px">Get instant AI-powered answers about your policy</div>
    </div>''', unsafe_allow_html=True)

    st.markdown(f'''<div class="ask-banner">
      {pal_svg(34)}
      Asking about: <strong>{an.get("insurer","your policy")}</strong>
      <span class="ask-badge">{ptype.upper()}</span>
    </div>''', unsafe_allow_html=True)

    # ── QUICK QUESTIONS ───────────────────────────────────────────────────────
    examples = {
        "Health":  ["What's my total out-of-pocket exposure?", "Is maternity care covered?", "Can I see specialists without referral?", "What's covered for prescriptions?"],
        "Auto":    ["Am I covered if someone borrows my car?", "Does this include roadside assistance?", "What happens after a collision?", "Is a rental car included?"],
        "Home":    ["Are floods covered?", "What's the personal property limit?", "Is my home office covered?", "How do I file a claim?"],
        "Renters": ["What's the personal property limit?", "Am I covered for theft?", "Does it cover temporary housing?", "Is my laptop covered?"],
    }.get(ptype, ["What is covered?", "What are the main exclusions?", "How do I file a claim?", "What are my deductibles?"])

    eq = st.columns(2)
    for i, q in enumerate(examples):
        if eq[i % 2].button(q, key=f"qq{i}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": q})
            with st.spinner("Reading your policy…"):
                ans = ask_policy_question(q, st.session_state.policy_text, API_KEY,
                                         st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()

    st.markdown("<div class='gap-md'></div>", unsafe_allow_html=True)

    # ── CHAT THREAD ───────────────────────────────────────────────────────────
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            _, c2 = st.columns([1, 4])
            with c2:
                st.markdown(f'''<div style="display:flex;gap:10px;align-items:flex-start;justify-content:flex-end;margin-bottom:14px">
                  <div class="bubble-user">{msg["content"]}</div>
                  <div class="user-av">U</div>
                </div>''', unsafe_allow_html=True)
        else:
            c1, _ = st.columns([4, 1])
            with c1:
                # Check if there's a section citation in the response
                content = msg["content"]
                cite_html = ""
                for kw in ["Section", "Article", "Clause", "Part", "Chapter"]:
                    if kw in content:
                        idx = content.find(kw)
                        end = content.find(".", idx)
                        if end > idx and end - idx < 60:
                            cite_text = content[idx:end].strip()
                            cite_html = f'<div class="cite-pill">{sparkle()} {cite_text}</div>'
                            break

                st.markdown(f'''<div style="display:flex;gap:12px;align-items:flex-start;margin-bottom:14px">
                  {pal_svg(44)}
                  <div class="bubble-pal">{content}{cite_html}</div>
                </div>''', unsafe_allow_html=True)

    # ── CHAT INPUT ────────────────────────────────────────────────────────────
    user_q = st.chat_input("Ask me anything about your policy…")
    if user_q:
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        with st.spinner("Searching your policy…"):
            ans = ask_policy_question(user_q, st.session_state.policy_text, API_KEY,
                                      st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": ans})
        st.rerun()

    st.markdown('''<div style="text-align:center;font-size:0.78rem;color:#4A3F6B;margin-top:1rem;position:relative;z-index:1">
      Powered by AI · Responses based on your policy document
    </div>''', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── RENDER ────────────────────────────────────────────────────────────────────
render_nav()
if st.session_state.page == "dashboard":
    page_dashboard()
elif st.session_state.page == "compare":
    page_compare()
elif st.session_state.page == "ask":
    page_ask()


