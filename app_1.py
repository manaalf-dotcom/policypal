"""
PolicyPal v3.0 — Production Build
Deep purple/blue gradient theme · Pal v3 illustrated shield mascot
Auto-analysis on upload · Visual comparison · Server-side API key
"""
import streamlit as st
import os

st.set_page_config(
    page_title="PolicyPal — Your Insurance, Simplified",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS injection — reads from styles.css, works on all Streamlit versions ──
import pathlib
_css = pathlib.Path('styles.css').read_text()
_fonts = '<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
st.markdown(_fonts, unsafe_allow_html=True)
st.markdown(f'<style>{_css}</style>', unsafe_allow_html=True)

# ── API KEY — server-side only, never shown to users ─────────────────────────
def _get_api_key():
    try:
        k = st.secrets.get("OPENAI_API_KEY", "")
        if k: return k
    except Exception:
        pass
    k = os.environ.get("OPENAI_API_KEY", "")
    if k: return k
    st.error("⚠️ OPENAI_API_KEY not found. Add it to Streamlit Secrets or your environment.")
    st.stop()

API_KEY = _get_api_key()

from auto_analysis import extract_pdf_text, analyze_policy_document, ask_policy_question
from compare_policies import compare_policies_llm, build_radar_chart, DIMENSIONS
import plotly.graph_objects as go

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "page": "dashboard",
    "analysis": None, "policy_text": None, "last_file": None,
    "chat_history": [],
    "cmp_an_a": None, "cmp_an_b": None,
    "comparison": None, "cmp_name_a": "Policy A", "cmp_name_b": "Policy B",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── PAL SVG — detailed illustrated shield mascot ─────────────────────────────
def pal_svg(size=44, state="default"):
    s = size
    h = int(s * 1.2)

    if state == "alert":
        grad = f'<linearGradient id="pg{s}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#DC2626"/><stop offset="100%" stop-color="#F97316"/></linearGradient>'
    elif state == "happy":
        grad = f'<linearGradient id="pg{s}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#7C3AED"/><stop offset="100%" stop-color="#0EA5E9"/></linearGradient>'
    elif state == "analyzing":
        grad = f'<linearGradient id="pg{s}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#6D28D9"/><stop offset="100%" stop-color="#0284C7"/></linearGradient>'
    else:
        grad = f'<linearGradient id="pg{s}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#7C3AED"/><stop offset="100%" stop-color="#0EA5E9"/></linearGradient>'

    # Shield body
    shield = (f'<path d="M{s*.5} {s*.04} C{s*.5} {s*.04} {s*.94} {s*.15} {s*.97} {s*.22} '
              f'L{s*.97} {s*.5} C{s*.97} {s*.78} {s*.5} {s*1.15} {s*.5} {s*1.15} '
              f'C{s*.5} {s*1.15} {s*.03} {s*.78} {s*.03} {s*.5} '
              f'L{s*.03} {s*.22} C{s*.06} {s*.15} {s*.5} {s*.04} {s*.5} {s*.04}Z" fill="url(#pg{s})"/>')

    # Inner dashed border
    inner = (f'<path d="M{s*.5} {s*.1} C{s*.5} {s*.1} {s*.88} {s*.2} {s*.9} {s*.26} '
             f'L{s*.9} {s*.5} C{s*.9} {s*.72} {s*.5} {s*1.08} {s*.5} {s*1.08} '
             f'C{s*.5} {s*1.08} {s*.1} {s*.72} {s*.1} {s*.5} '
             f'L{s*.1} {s*.26} C{s*.12} {s*.2} {s*.5} {s*.1} {s*.5} {s*.1}Z" '
             f'fill="none" stroke="rgba(255,255,255,0.16)" stroke-width="{s*.014}" stroke-dasharray="3 3"/>')

    # Emblem (top area)
    if state == "alert":
        emblem = (f'<path d="M{s*.38} {s*.28} L{s*.5} {s*.1} L{s*.62} {s*.28}Z" '
                  f'fill="rgba(255,255,255,0.28)" stroke="rgba(255,255,255,0.55)" stroke-width="{s*.015}"/>'
                  f'<rect x="{s*.478}" y="{s*.13}" width="{s*.044}" height="{s*.08}" rx="{s*.015}" fill="rgba(255,255,255,0.8)"/>'
                  f'<circle cx="{s*.5}" cy="{s*.26}" r="{s*.022}" fill="rgba(255,255,255,0.8)"/>')
    elif state == "happy":
        emblem = (f'<polygon points="{s*.5},{s*.09} {s*.53},{s*.18} {s*.63},{s*.18} {s*.56},{s*.24} '
                  f'{s*.58},{s*.33} {s*.5},{s*.28} {s*.42},{s*.33} {s*.44},{s*.24} {s*.37},{s*.18} {s*.47},{s*.18}" '
                  f'fill="rgba(255,255,255,0.45)"/>')
    elif state == "analyzing":
        emblem = (f'<circle cx="{s*.36}" cy="{s*.2}" r="{s*.04}" fill="rgba(255,255,255,0.55)"/>'
                  f'<circle cx="{s*.5}" cy="{s*.18}" r="{s*.04}" fill="rgba(255,255,255,0.75)"/>'
                  f'<circle cx="{s*.64}" cy="{s*.2}" r="{s*.04}" fill="rgba(255,255,255,0.55)"/>')
    else:
        emblem = (f'<circle cx="{s*.5}" cy="{s*.2}" r="{s*.1}" fill="rgba(255,255,255,0.18)" '
                  f'stroke="rgba(255,255,255,0.35)" stroke-width="{s*.012}"/>'
                  f'<path d="M{s*.42} {s*.2} L{s*.48} {s*.26} L{s*.58} {s*.16}" '
                  f'stroke="white" stroke-width="{s*.03}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

    # Eyes
    ey = s * 0.52  # eye center y
    elx, erx = s * 0.33, s * 0.67  # eye centers x
    ew, eh = s * 0.105, s * 0.115  # radii

    if state == "happy":
        # Squinting crescents
        eyes = (f'<path d="M{s*.22} {ey} Q{elx} {s*.44} {s*.44} {ey}" stroke="#1A0F3C" stroke-width="{s*.05}" fill="rgba(255,255,255,0.9)" stroke-linecap="round"/>'
                f'<path d="M{s*.56} {ey} Q{erx} {s*.44} {s*.78} {ey}" stroke="#1A0F3C" stroke-width="{s*.05}" fill="rgba(255,255,255,0.9)" stroke-linecap="round"/>'
                f'<ellipse cx="{s*.18}" cy="{s*.6}" rx="{s*.07}" ry="{s*.05}" fill="rgba(255,180,180,0.3)"/>'
                f'<ellipse cx="{s*.82}" cy="{s*.6}" rx="{s*.07}" ry="{s*.05}" fill="rgba(255,180,180,0.3)"/>')
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
                f'<circle cx="{elx}" cy="{ey}" r="{s*.07}" fill="#5B21B6"/>'
                f'<circle cx="{erx}" cy="{ey}" r="{s*.07}" fill="#5B21B6"/>'
                f'<circle cx="{elx+s*.01}" cy="{ey}" r="{s*.038}" fill="#1A0F3C"/>'
                f'<circle cx="{erx+s*.01}" cy="{ey}" r="{s*.038}" fill="#1A0F3C"/>'
                f'<circle cx="{elx+s*.025}" cy="{ey-s*.03}" r="{s*.02}" fill="white"/>'
                f'<circle cx="{erx+s*.025}" cy="{ey-s*.03}" r="{s*.02}" fill="white"/>'
                f'<circle cx="{elx-s*.01}" cy="{ey+s*.02}" r="{s*.01}" fill="rgba(255,255,255,0.5)"/>'
                f'<circle cx="{erx-s*.01}" cy="{ey+s*.02}" r="{s*.01}" fill="rgba(255,255,255,0.5)"/>')

    # Brows
    by = s * 0.42
    if state == "alert":
        brows = (f'<path d="M{s*.2} {by-s*.02} Q{elx} {by-s*.06} {s*.44} {by}" stroke="#1A0F3C" stroke-width="{s*.028}" fill="none" stroke-linecap="round"/>'
                 f'<path d="M{s*.56} {by} Q{erx} {by-s*.06} {s*.8} {by-s*.02}" stroke="#1A0F3C" stroke-width="{s*.028}" fill="none" stroke-linecap="round"/>')
    elif state == "happy":
        brows = (f'<path d="M{s*.21} {by-s*.04} Q{elx} {by-s*.09} {s*.44} {by-s*.04}" stroke="#1A0F3C" stroke-width="{s*.024}" fill="none" stroke-linecap="round"/>'
                 f'<path d="M{s*.56} {by-s*.04} Q{erx} {by-s*.09} {s*.79} {by-s*.04}" stroke="#1A0F3C" stroke-width="{s*.024}" fill="none" stroke-linecap="round"/>')
    elif state == "analyzing":
        brows = (f'<path d="M{s*.21} {by-s*.05} Q{elx} {by-s*.1} {s*.44} {by-s*.02}" stroke="#1A0F3C" stroke-width="{s*.024}" fill="none" stroke-linecap="round"/>'
                 f'<path d="M{s*.56} {by} Q{erx} {by-s*.06} {s*.79} {by}" stroke="#1A0F3C" stroke-width="{s*.024}" fill="none" stroke-linecap="round"/>')
    else:
        brows = (f'<path d="M{s*.21} {by} Q{elx} {by-s*.06} {s*.44} {by}" stroke="#1A0F3C" stroke-width="{s*.025}" fill="none" stroke-linecap="round"/>'
                 f'<path d="M{s*.56} {by} Q{erx} {by-s*.06} {s*.79} {by}" stroke="#1A0F3C" stroke-width="{s*.025}" fill="none" stroke-linecap="round"/>')

    # Nose hint
    nose = (f'<path d="M{s*.46} {s*.62} Q{s*.5} {s*.66} {s*.54} {s*.62}" '
            f'stroke="rgba(26,15,60,0.28)" stroke-width="{s*.015}" fill="none" stroke-linecap="round"/>')

    # Mouth
    my = s * 0.76
    if state == "alert":
        mouth = f'<path d="M{s*.28} {my} Q{s*.36} {my-s*.05} {s*.5} {my+s*.02} Q{s*.64} {my+s*.09} {s*.72} {my+s*.04}" stroke="#1A0F3C" stroke-width="{s*.032}" fill="none" stroke-linecap="round"/>'
    elif state == "happy":
        mouth = (f'<path d="M{s*.22} {my-s*.02} Q{s*.5} {my+s*.12} {s*.78} {my-s*.02}" '
                 f'stroke="#1A0F3C" stroke-width="{s*.038}" fill="rgba(26,15,60,0.18)" stroke-linecap="round"/>')
    elif state == "analyzing":
        mouth = f'<path d="M{s*.3} {my} Q{s*.5} {my+s*.04} {s*.7} {my}" stroke="#1A0F3C" stroke-width="{s*.028}" fill="none" stroke-linecap="round"/>'
    else:
        mouth = (f'<path d="M{s*.3} {my-s*.01} Q{s*.5} {my+s*.09} {s*.7} {my-s*.01}" '
                 f'stroke="#1A0F3C" stroke-width="{s*.034}" fill="rgba(26,15,60,0.1)" stroke-linecap="round"/>')

    # Cheeks for happy
    cheeks = ""
    if state == "happy":
        cheeks = (f'<ellipse cx="{s*.19}" cy="{s*.65}" rx="{s*.08}" ry="{s*.055}" fill="rgba(255,180,180,0.22)"/>'
                  f'<ellipse cx="{s*.81}" cy="{s*.65}" rx="{s*.08}" ry="{s*.055}" fill="rgba(255,180,180,0.22)"/>')

    # Extras
    extras = ""
    if state == "analyzing":
        extras = (f'<circle cx="{s*.5}" cy="{s*1.22}" r="{s*1.18}" fill="none" '
                  f'stroke="rgba(167,139,250,0.18)" stroke-width="{s*.02}" stroke-dasharray="4 7"/>'
                  f'<circle cx="{s*.5}" cy="{s*.02}" r="{s*.045}" fill="#A78BFA" opacity="0.8"/>')
    elif state == "happy":
        extras = (f'<line x1="{s*.06}" y1="{s*.35}" x2="{s*.12}" y2="{s*.35}" stroke="#A78BFA" stroke-width="{s*.025}" opacity="0.85"/>'
                  f'<line x1="{s*.09}" y1="{s*.32}" x2="{s*.09}" y2="{s*.38}" stroke="#A78BFA" stroke-width="{s*.025}" opacity="0.85"/>'
                  f'<line x1="{s*.88}" y1="{s*.28}" x2="{s*.94}" y2="{s*.28}" stroke="#38BDF8" stroke-width="{s*.025}" opacity="0.85"/>'
                  f'<line x1="{s*.91}" y1="{s*.25}" x2="{s*.91}" y2="{s*.31}" stroke="#38BDF8" stroke-width="{s*.025}" opacity="0.85"/>')

    return (f'<svg width="{s}" height="{h}" viewBox="0 0 {s} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs>{grad}</defs>'
            f'{extras}{shield}{inner}{emblem}{eyes}{brows}{nose}{mouth}{cheeks}'
            f'</svg>')


def chk_svg():
    return '<svg width="11" height="11" viewBox="0 0 11 11" fill="none"><path d="M1.5 5.5L4 8L9.5 2.5" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def x_svg():
    return '<svg width="11" height="11" viewBox="0 0 11 11" fill="none"><path d="M2 2L9 9M9 2L2 9" stroke="white" stroke-width="1.8" stroke-linecap="round"/></svg>'


# ── CHARTS ────────────────────────────────────────────────────────────────────
def donut_chart(areas):
    labels = list(areas.keys())
    values = list(areas.values())
    colors = ["#7C3AED", "#A855F7", "#0EA5E9", "#38BDF8", "#6D28D9", "#0284C7"]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.58,
        marker=dict(colors=colors[:len(labels)], line=dict(color="rgba(26,15,60,0.6)", width=3)),
        textinfo="label+percent",
        textfont=dict(size=11, family="Plus Jakarta Sans", color="#EEE8FF"),
        hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5,
                    font=dict(size=10, family="Plus Jakarta Sans", color="#A89FCC")),
        margin=dict(l=0, r=0, t=10, b=50),
        paper_bgcolor="rgba(0,0,0,0)", height=255,
    )
    return fig


def trend_chart():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    vals = [420, 435, 450, 448, 452, 450]
    fig = go.Figure(go.Scatter(
        x=months, y=vals, mode="lines+markers",
        line=dict(color="#A78BFA", width=2.5, shape="spline"),
        marker=dict(color="#A78BFA", size=7, line=dict(color="rgba(26,15,60,0.8)", width=2)),
        fill="tozeroy", fillcolor="rgba(124,58,237,0.1)",
    ))
    fig.update_layout(
        xaxis=dict(showgrid=False, tickfont=dict(size=11, family="Plus Jakarta Sans", color="#7B6FA0"),
                   linecolor="rgba(255,255,255,0.08)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)",
                   tickprefix="$", tickfont=dict(size=11, family="Plus Jakarta Sans", color="#7B6FA0"),
                   range=[0, 600]),
        margin=dict(l=40, r=10, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=225,
    )
    return fig


def radar_fig(cmp, na, nb):
    dims = DIMENSIONS
    sa = [cmp["dimension_scores"][d]["a"] for d in dims]
    sb = [cmp["dimension_scores"][d]["b"] for d in dims]
    sa = sa + [sa[0]]; sb = sb + [sb[0]]; dc = dims + [dims[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=sa, theta=dc, fill="toself", name=na,
        line=dict(color="#A78BFA", width=2), fillcolor="rgba(124,58,237,0.15)",
        marker=dict(size=6, color="#A78BFA")))
    fig.add_trace(go.Scatterpolar(r=sb, theta=dc, fill="toself", name=nb,
        line=dict(color="#38BDF8", width=2), fillcolor="rgba(56,189,248,0.12)",
        marker=dict(size=6, color="#38BDF8")))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], tickvals=[2, 4, 6, 8, 10],
                            tickfont=dict(size=9, color="#7B6FA0"),
                            gridcolor="rgba(255,255,255,0.08)", linecolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(tickfont=dict(size=11, family="Plus Jakarta Sans", color="#A89FCC")),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5,
                    font=dict(size=11, family="Plus Jakarta Sans", color="#A89FCC"),
                    bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=40, r=40, t=20, b=60), height=380,
    )
    return fig


# ── NAV ───────────────────────────────────────────────────────────────────────
def render_nav():
    st.markdown(f'<div class="pp-nav"><div class="pp-logo">{pal_svg(26)} PolicyPal</div></div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
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
# PAGE — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    an = st.session_state.analysis
    st.markdown('<div class="pp-page">', unsafe_allow_html=True)

    if an is None:
        # ── Hero / upload ──────────────────────────────────────────────────
        st.markdown(f'''<div class="hero-wrap">
          <div class="hero-h">Your insurance,<br><em>simplified.</em></div>
          <div class="hero-sub">Upload your policy PDF and get instant AI-powered insights<br>in plain English — no jargon, no confusion.</div>
        </div>''', unsafe_allow_html=True)

        uc, _ = st.columns([2, 1])
        with uc:
            st.markdown(f'''<div class="upload-card">
              <div style="flex-shrink:0">{pal_svg(72)}</div>
              <div class="upload-card-text">
                <h3>Drop your policy PDF here</h3>
                <p>Or click to browse &nbsp;•&nbsp; Supports PDF up to 25MB<br>Health · Auto · Home · Renters · Life</p>
              </div>
            </div>''', unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload your policy PDF", type=["pdf"], key="main_upload",
                                        label_visibility="collapsed")

        st.markdown('''<div class="chips">
          <div class="chip">📄 Plain-English summaries</div>
          <div class="chip">🛡️ Risk scoring &amp; alerts</div>
          <div class="chip">⚖️ Policy comparison</div>
          <div class="chip">✨ Instant analysis</div>
          <div class="chip">💬 Ask questions</div>
        </div>
        <div class="trust">
          <span>🔒 Bank-level encryption</span>
          <span>⚡ Analysis in seconds</span>
          <span>🤖 Powered by AI</span>
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

        st.markdown('</div>', unsafe_allow_html=True)
        return

    # ── Policy banner ──────────────────────────────────────────────────────
    ptype = an.get("policy_type", "Insurance").upper()
    rs = an.get("risk_score", 5)
    av_state = "alert" if rs >= 7 else ("happy" if rs <= 3 else "default")

    st.markdown(f'''<div class="policy-banner">
      {pal_svg(48, av_state)}
      <span class="ptype-badge">{ptype} Insurance</span>
      <div>
        <div class="policy-name">{an.get("insurer", "Your Policy")}</div>
        <div class="policy-meta">Uploaded policy &nbsp;·&nbsp; <span class="active">Active</span></div>
      </div>
      <div class="analysis-done">✨ Analysis complete</div>
    </div>''', unsafe_allow_html=True)

    # ── 4 stat cards ──────────────────────────────────────────────────────
    rt = "Excellent" if rs <= 3 else ("Average" if rs <= 6 else "High Risk")
    rt_cls = "sc-tag-good" if rs <= 3 else "sc-tag-warn"
    prem = an.get("monthly_premium") or an.get("annual_premium") or "—"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card sc-1"><div class="sc-top"><div class="sc-icon">💲</div><span class="sc-tag sc-tag-warn">+12% vs avg</span></div><div class="sc-label">Annual Deductible</div><div class="sc-value">{an.get("deductible","—")}</div><div class="sc-sub">Before insurance kicks in</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card sc-2"><div class="sc-top"><div class="sc-icon">📈</div><span class="sc-tag sc-tag-good">Market rate</span></div><div class="sc-label">Monthly Premium</div><div class="sc-value">{prem}</div><div class="sc-sub">{an.get("insurer","")}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card sc-3"><div class="sc-top"><div class="sc-icon">💊</div><span class="sc-tag sc-tag-warn">+8% vs avg</span></div><div class="sc-label">Max Out-of-Pocket</div><div class="sc-value">{an.get("out_of_pocket_max","—")}</div><div class="sc-sub">Worst-case annual spend</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card sc-4"><div class="sc-top"><div class="sc-icon">🛡️</div><span class="sc-tag {rt_cls}">{rt}</span></div><div class="sc-label">Coverage Score</div><div class="sc-value" style="color:#38BDF8">{rs}/10</div><div class="sc-sub" style="color:#38BDF8">{rt}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── Charts row ────────────────────────────────────────────────────────
    lc, rc = st.columns(2)
    with lc:
        st.markdown('<div class="cc"><div class="cc-h">Coverage Breakdown</div>', unsafe_allow_html=True)
        areas = an.get("coverage_areas", {})
        if areas:
            st.plotly_chart(donut_chart(areas), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with rc:
        st.markdown('<div class="cc"><div class="cc-h">Premium Trend (6 months)</div>', unsafe_allow_html=True)
        st.plotly_chart(trend_chart(), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── Plain English summary ──────────────────────────────────────────────
    st.markdown(f'''<div class="cc">
      <div class="sum-header">{pal_svg(40, "happy")}<div><h3>Plain English Summary</h3><p>Here's what you need to know about your policy</p></div></div>
      <div class="sum-text">{an.get("plain_summary","")}</div>
      <div class="ideal">💡 <strong>Ideal for:</strong> {an.get("who_its_good_for","")}</div>
    </div>''', unsafe_allow_html=True)

    savings = an.get("potential_savings", "")
    if savings and savings.lower() != "none identified":
        st.markdown(f'<div class="gap-sm"></div><div class="cc" style="border-color:rgba(56,189,248,0.25);background:rgba(14,165,233,0.1)"><div class="cc-h" style="color:#38BDF8">💰 Potential Savings Tip</div><div style="font-size:0.9rem;color:#BAE6FD;line-height:1.65">{savings}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── Covered / Not Covered ─────────────────────────────────────────────
    lc2, rc2 = st.columns(2)
    with lc2:
        items = "".join([f'<div class="cov-item"><div class="ic-g">{chk_svg()}</div><span>{b}</span></div>' for b in an.get("key_benefits", [])])
        st.markdown(f'<div class="cc"><div class="cc-h"><span class="dot-g"></span>What\'s Covered</div>{items}</div>', unsafe_allow_html=True)
    with rc2:
        items = "".join([f'<div class="cov-item"><div class="ic-o">{x_svg()}</div><span>{e}</span></div>' for e in an.get("exclusions", [])])
        st.markdown(f'<div class="cc"><div class="cc-h"><span class="dot-o"></span>What\'s Not Covered</div>{items}</div>', unsafe_allow_html=True)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── Risk flags ────────────────────────────────────────────────────────
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

    # ── CTAs ──────────────────────────────────────────────────────────────
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

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — COMPARE
# ══════════════════════════════════════════════════════════════════════════════
def page_compare():
    st.markdown('<div class="pp-page">', unsafe_allow_html=True)
    st.markdown('''<div style="padding:1.5rem 0 1rem">
      <div class="cmp-h">Policy <em>Comparison</em></div>
      <div class="cmp-sub">Head-to-head analysis of your options</div>
    </div>''', unsafe_allow_html=True)

    uc1, uc2 = st.columns(2)
    with uc1:
        st.markdown('<p style="font-weight:600;color:#C4B5FD;margin-bottom:6px">Policy A</p>', unsafe_allow_html=True)
        fa = st.file_uploader("Upload Policy A", type=["pdf"], key="cmp_a")
        na = st.text_input("Label for Policy A", value="Policy A", key="na")
    with uc2:
        st.markdown('<p style="font-weight:600;color:#C4B5FD;margin-bottom:6px">Policy B</p>', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)
        return

    na = st.session_state.cmp_name_a
    nb = st.session_state.cmp_name_b
    winner = cmp.get("overall_winner", "Tie")
    sa = cmp.get("overall_score_a", 0)
    sb = cmp.get("overall_score_b", 0)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── Score pods ────────────────────────────────────────────────────────
    sc1, vsc, sc2 = st.columns([5, 1, 5])
    with sc1:
        wp = '<div class="pod-winner">🏆 Overall Winner</div>' if winner == "A" else ""
        st.markdown(f'<div class="score-pod pod-a">{wp}<div class="pod-name">{na}</div><div><span class="pod-score pod-score-a">{sa}</span><span class="pod-denom"> / 10</span></div><div style="font-size:0.78rem;color:rgba(255,255,255,0.35);margin-top:4px">Overall Score</div></div>', unsafe_allow_html=True)
    with vsc:
        st.markdown('<div style="display:flex;align-items:center;height:100%;justify-content:center;padding-top:1rem"><div class="vs-circle">VS</div></div>', unsafe_allow_html=True)
    with sc2:
        rp = '<div class="pod-runner">Runner Up</div>' if winner == "A" else ('<div class="pod-winner">🏆 Overall Winner</div>' if winner == "B" else "")
        st.markdown(f'<div class="score-pod pod-b">{rp}<div class="pod-name">{nb}</div><div><span class="pod-score pod-score-b">{sb}</span><span class="pod-denom"> / 10</span></div><div style="font-size:0.78rem;color:rgba(255,255,255,0.35);margin-top:4px">Overall Score</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    # ── Radar chart ────────────────────────────────────────────────────────
    st.markdown('<div class="cc"><div class="cc-h">Performance Comparison</div>', unsafe_allow_html=True)
    st.plotly_chart(radar_fig(cmp, na, nb), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div><div class="gap-md"></div>', unsafe_allow_html=True)

    # ── Dimension bars ────────────────────────────────────────────────────
    st.markdown('<div class="cc"><div class="cc-h">Detailed Comparison</div>', unsafe_allow_html=True)
    dim_scores = cmp.get("dimension_scores", {})
    cat_winners = cmp.get("category_winners", {})
    for dim in DIMENSIONS:
        sc = dim_scores.get(dim, {})
        va = sc.get("a", 5); vb = sc.get("b", 5)
        w = cat_winners.get(dim, "Tie")
        wn = na if w == "A" else (nb if w == "B" else "Tie")
        wc = "win-a" if w == "A" else ("win-b" if w == "B" else "win-tie")
        pa = min(100, int(va / 10 * 100))
        pb = min(100, int(vb / 10 * 100))
        st.markdown(f'''<div style="margin-bottom:14px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px">
            <div style="font-size:0.85rem;font-weight:600;color:#EEE8FF">{dim}</div>
            <span class="win-pill {wc}">Winner: {wn}</span>
          </div>
          <div class="dim-row">
            <div class="dim-name" style="color:#A78BFA;font-weight:500">{na}</div>
            <div class="bar-track"><div class="fill-a" style="width:{pa}%"></div></div>
            <div style="font-size:0.82rem;font-weight:600;color:#A78BFA;flex:0 0 44px;text-align:right">{va}/10</div>
          </div>
          <div class="dim-row" style="border:none">
            <div class="dim-name" style="color:#38BDF8;font-weight:500">{nb}</div>
            <div class="bar-track"><div class="fill-b" style="width:{pb}%"></div></div>
            <div style="font-size:0.82rem;font-weight:600;color:#38BDF8;flex:0 0 44px;text-align:right">{vb}/10</div>
          </div>
        </div>''', unsafe_allow_html=True)
    st.markdown('</div><div class="gap-md"></div>', unsafe_allow_html=True)

    # ── Best for grid ─────────────────────────────────────────────────────
    best = cmp.get("best_for", {})
    if best:
        st.markdown('<div class="cc"><div class="cc-h">Best For…</div><div class="bf-grid">', unsafe_allow_html=True)
        for scenario, wl in best.items():
            wname = na if wl == "A" else nb
            wcls = "bf-win-a" if wl == "A" else "bf-win-b"
            st.markdown(f'<div class="bf-card"><div class="bf-label">{scenario}</div><div class="{wcls}">{wname}</div></div>', unsafe_allow_html=True)
        st.markdown('</div></div><div class="gap-md"></div>', unsafe_allow_html=True)

    # ── Winner reason ──────────────────────────────────────────────────────
    reason = cmp.get("overall_winner_reason", "")
    if reason:
        wname = na if winner == "A" else nb
        st.markdown(f'<div class="cc" style="border-color:rgba(167,139,250,0.25);background:rgba(124,58,237,0.12)"><div class="cc-h" style="color:#A78BFA">Why {wname} wins</div><p style="font-size:0.9rem;color:#C4B5FD;line-height:1.7">{reason}</p></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — ASK PAL
# ══════════════════════════════════════════════════════════════════════════════
def page_ask():
    st.markdown('<div class="pp-page">', unsafe_allow_html=True)

    if not st.session_state.policy_text:
        st.markdown(f'''<div class="no-policy">
          <div class="ic">{pal_svg(88)}</div>
          <h3>Upload a policy first</h3>
          <p>Head to the Dashboard tab, upload your PDF,<br>then come back here to ask Pal anything.</p>
        </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    an = st.session_state.analysis or {}
    ptype = an.get("policy_type", "Insurance")

    st.markdown(f'''<div class="ask-banner">
      {pal_svg(34)}
      Asking about: <strong>{an.get("insurer", "your policy")}</strong>
      <span class="ask-badge">{ptype.upper()}</span>
    </div>''', unsafe_allow_html=True)

    examples = {
        "Health":  ["Will ER visits be covered?", "What's my specialist copay?", "Is therapy included?", "What if I travel abroad?"],
        "Auto":    ["Covered if someone borrows my car?", "Does this include roadside?", "What after a collision?", "Is a rental car included?"],
        "Home":    ["Are floods covered?", "What's the property limit?", "Home office covered?", "How do I file a claim?"],
        "Renters": ["What's the personal property limit?", "Am I covered for theft?", "Does it cover temp housing?", "Is my laptop covered?"],
    }.get(ptype, ["What is covered?", "Main exclusions?", "How do I file a claim?", "What are my deductibles?"])

    eq = st.columns(2)
    for i, q in enumerate(examples):
        if eq[i % 2].button(q, key=f"qq{i}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": q})
            with st.spinner("Searching your policy…"):
                ans = ask_policy_question(q, st.session_state.policy_text, API_KEY,
                                         st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()

    st.markdown('<div class="gap-md"></div>', unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            _, c2 = st.columns([1, 4])
            with c2:
                st.markdown(f'<div class="bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            c1, _ = st.columns([4, 1])
            with c1:
                st.markdown(f'<div style="display:flex;gap:10px;align-items:flex-start">{pal_svg(36)}<div class="bubble-pal">{msg["content"]}</div></div>', unsafe_allow_html=True)

    user_q = st.chat_input("Ask anything about your policy…")
    if user_q:
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        with st.spinner("Searching your policy…"):
            ans = ask_policy_question(user_q, st.session_state.policy_text, API_KEY,
                                      st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": ans})
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ── RENDER ────────────────────────────────────────────────────────────────────
render_nav()
if st.session_state.page == "dashboard":
    page_dashboard()
elif st.session_state.page == "compare":
    page_compare()
elif st.session_state.page == "ask":
    page_ask()
