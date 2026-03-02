import re, io, math
from collections import defaultdict

import streamlit as st
import plotly.graph_objects as go
from afinn import Afinn
import pdfplumber
from docx import Document

from nrc_data import NRC_LEXICON, EMOTION_META
from auth import require_auth, show_nav

st.set_page_config(page_title="Analyzer — Sentiment Pro", page_icon="📊", layout="wide")
require_auth()
show_nav("Analyzer")

# ── Analysis Engine ───────────────────────────────────────────
afinn_scorer = Afinn()
EMOTIONS = list(EMOTION_META.keys())

def tokenize(text): return re.findall(r"\b[a-z']+\b", text.lower())

def extract_pdf(b):
    parts = []
    with pdfplumber.open(io.BytesIO(b)) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t: parts.append(t)
    return "\n\n".join(parts)

def extract_docx(b):
    doc = Document(io.BytesIO(b))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def analyze_sentiment(text):
    words = tokenize(text)
    raw = afinn_scorer.score(text)
    log = 0.0
    if raw != 0:
        log = (1 if raw > 0 else -1) * math.log10(1 + abs(raw))
    cat, emo = ("Positive", "😀") if log > 0.3 else (("Negative", "😡") if log < -0.3 else ("Neutral", "😐"))
    neg, pos, seen = [], [], set()
    for w in words:
        s = afinn_scorer.score(w)
        if w not in seen and s != 0:
            seen.add(w); (pos if s > 0 else neg).append(w)
    return dict(raw=raw, log=round(log,3), cat=cat, emo=emo, wc=len(words), neg=neg, pos=pos, text=text)

def analyze_emotions(text):
    words = tokenize(text)
    scores = defaultdict(int); wbe = defaultdict(list)
    for w in words:
        for e in NRC_LEXICON.get(w, []):
            scores[e] += 1
            if w not in wbe[e]: wbe[e].append(w)
    total = sum(scores.values())
    dom = max(scores, key=scores.get) if total > 0 else None
    for e in EMOTIONS:
        scores.setdefault(e, 0)
    return dict(scores=dict(scores), dominant=dom, wbe=dict(wbe), total=total)

def chips(words, cls):
    return " ".join(f'<span class="word-chip {cls}">{w}</span>' for w in words)

# ── UI ────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hero">
  <h1>📊 Sentiment Analyzer</h1>
  <p>Upload a document or paste text to get instant AI-powered sentiment & emotion insights</p>
</div>
""", unsafe_allow_html=True)

tab_file, tab_text = st.tabs(["📁 Upload File (.pdf / .docx)", "✏️ Paste Text"])

text_to_analyze = None
source_name = None

with tab_file:
    up = st.file_uploader("Choose a file", type=["pdf","docx"])
    if up:
        if st.button("🔍 Analyze Document", type="primary"):
            with st.spinner("Extracting text…"):
                try:
                    raw = up.read()
                    txt = extract_pdf(raw) if up.name.endswith(".pdf") else extract_docx(raw)
                    if txt.strip(): text_to_analyze, source_name = txt.strip(), up.name
                    else: st.error("⚠️ No readable text found. File may be scanned/image-based.")
                except Exception as ex:
                    st.error(f"⚠️ Error: {ex}")

with tab_text:
    user_text = st.text_area("Paste your text here", height=220, label_visibility="collapsed",
                              placeholder="Paste reviews, emails, feedback, articles…")
    if st.button("🔍 Analyze Text", type="primary"):
        if user_text.strip(): text_to_analyze, source_name = user_text.strip(), "Pasted Text"
        else: st.warning("Please enter some text.")

# ── Results ───────────────────────────────────────────────────
if text_to_analyze:
    with st.spinner("Analyzing…"):
        sa = analyze_sentiment(text_to_analyze)
        ea = analyze_emotions(text_to_analyze)

    st.success(f"✅ Analysis complete for **{source_name}**")
    st.markdown("---")

    # Score cards
    st.markdown("### 📊 Sentiment Results")
    c1, c2, c3, c4 = st.columns(4)
    sc = "positive" if sa["log"] > 0.3 else ("negative" if sa["log"] < -0.3 else "neutral")
    with c1: st.markdown(f'<div class="metric-card"><div class="metric-label">Sentiment</div><div class="metric-value">{sa["emo"]}</div><div class="metric-sub">{sa["cat"]}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="metric-label">Score</div><div class="metric-value {sc}">{sa["log"]}</div><div class="metric-sub">log-normalized</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="metric-label">Total Words</div><div class="metric-value" style="color:#4e54c8">{sa["wc"]}</div><div class="metric-sub">tokens</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="metric-label">Raw AFINN</div><div class="metric-value" style="color:#8f94fb">{int(sa["raw"])}</div><div class="metric-sub">sum</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if sa["pos"]:
        st.markdown('<div class="result-box"><b>✅ Positive Words</b><br>', unsafe_allow_html=True)
        st.markdown(chips(sa["pos"], "chip-pos"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if sa["neg"]:
        st.markdown('<div class="result-box"><b>⚠️ Negative Words</b><br>', unsafe_allow_html=True)
        st.markdown(chips(sa["neg"], "chip-neg"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("📄 View Highlighted Text"):
        hl = sa["text"]
        for w in sa["pos"]:
            hl = re.sub(rf'\b({re.escape(w)})\b', r'<mark style="background:#d4f7e7;border-radius:3px;padding:1px 3px">\1</mark>', hl, flags=re.IGNORECASE)
        for w in sa["neg"]:
            hl = re.sub(rf'\b({re.escape(w)})\b', r'<mark style="background:#fde8ea;border-radius:3px;padding:1px 3px">\1</mark>', hl, flags=re.IGNORECASE)
        st.markdown(f'<div style="line-height:1.9;font-size:0.92rem;max-height:380px;overflow-y:auto;border:1px solid #e0e0ef;border-radius:12px;padding:1rem">{hl}</div>', unsafe_allow_html=True)

    # Emotion section
    st.markdown("---")
    st.markdown("### 🧠 Emotion Breakdown")

    if ea["total"] == 0:
        st.info("No emotion-linked words detected.")
    else:
        dom = ea["dominant"]
        if dom:
            dm = EMOTION_META[dom]
            st.markdown(f'<div style="background:{dm["color"]}22;border:1.5px solid {dm["color"]};border-radius:12px;padding:1rem 1.25rem;display:flex;align-items:center;gap:1rem;margin-bottom:1rem"><span style="font-size:2.5rem">{dm["emoji"]}</span><div><div style="font-size:1.3rem;font-weight:800;color:{dm["color"]}">{dm["label"]}</div><div style="font-size:0.83rem;color:#6b7280">Dominant emotion · {ea["scores"][dom]} word{"s" if ea["scores"][dom]!=1 else ""}</div></div></div>', unsafe_allow_html=True)

        sorted_emo = sorted(ea["scores"].items(), key=lambda x: x[1], reverse=True)
        labels = [f'{EMOTION_META[e]["emoji"]} {EMOTION_META[e]["label"]}' for e, _ in sorted_emo]
        values = [v for _, v in sorted_emo]
        colors = [EMOTION_META[e]["color"] for e, _ in sorted_emo]

        col_r, col_b = st.columns(2)
        with col_r:
            fig = go.Figure(go.Scatterpolar(
                r=values + [values[0]], theta=labels + [labels[0]], fill='toself',
                fillcolor='rgba(78,84,200,0.15)',
                line=dict(color='rgba(78,84,200,0.8)', width=2),
                marker=dict(color=colors + [colors[0]], size=8),
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, showticklabels=False, gridcolor="#eee"), angularaxis=dict(gridcolor="#eee")),
                showlegend=False, height=300, margin=dict(t=20,b=20,l=20,r=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            total_emo = ea["total"] or 1; max_v = values[0] or 1
            for e, count in sorted_emo:
                m = EMOTION_META[e]; pct = round(count/total_emo*100); bw = round(count/max_v*100)
                st.markdown(f'<div class="emotion-bar-row"><div class="emotion-bar-label"><span>{m["emoji"]} {m["label"]}</span><span>{pct}% ({count})</span></div><div class="emotion-bar-track"><div style="height:100%;width:{bw}%;background:{m["color"]};border-radius:4px"></div></div></div>', unsafe_allow_html=True)

        st.markdown("<br>**🔍 Words by Emotion**", unsafe_allow_html=True)
        for e, count in sorted_emo:
            if count == 0: continue
            m = EMOTION_META[e]; words_e = ea["wbe"].get(e, [])
            if words_e:
                tags = " ".join(f'<span class="emotion-tag" style="background:{m["color"]}22;color:{m["color"]}">{w}</span>' for w in words_e)
                st.markdown(f'<div style="margin-bottom:0.6rem"><div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:#9ca3af">{m["emoji"]} {m["label"]}</div>{tags}</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro · AFINN-165 & NRC Emotion Lexicon</div>', unsafe_allow_html=True)
