import re
import io
import math
from collections import defaultdict

import streamlit as st
import plotly.graph_objects as go
from afinn import Afinn
import pdfplumber
from docx import Document

from nrc_data import NRC_LEXICON, EMOTION_META

# ────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sentiment Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main-header {
    background: linear-gradient(135deg, #4e54c8, #8f94fb);
    padding: 2.5rem 2rem 2rem;
    border-radius: 16px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
  }
  .main-header h1 { font-size: 2.5rem; font-weight: 800; margin: 0; }
  .main-header p  { font-size: 1.1rem; opacity: 0.9; margin: 0.5rem 0 0; }

  .metric-card {
    background: white;
    border: 1px solid #e0e0ef;
    border-radius: 16px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  }
  .metric-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
                  letter-spacing: 0.05em; color: #6b7280; margin-bottom: 0.4rem; }
  .metric-value { font-size: 2rem; font-weight: 800; line-height: 1; }
  .metric-sub   { font-size: 0.8rem; color: #9ca3af; margin-top: 0.3rem; }

  .positive { color: #2ed573; }
  .negative { color: #ff4757; }
  .neutral  { color: #9ca3af; }

  .result-box {
    background: #fafbff;
    border: 1px solid #e0e0ef;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
  }

  .word-chip {
    display: inline-block;
    padding: 0.3rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 0.2rem;
  }
  .chip-neg { background: rgba(255,71,87,0.12); color: #ff4757; }
  .chip-pos { background: rgba(46,213,115,0.12); color: #1a9e4e; }

  .emotion-header-bar {
    background: linear-gradient(135deg, #4e54c8, #8f94fb);
    padding: 0.85rem 1.5rem;
    border-radius: 12px;
    color: white;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 1rem;
  }

  .dominant-box {
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .section-divider {
    border: none;
    border-top: 2px solid #f0f0f5;
    margin: 2rem 0;
  }

  .footer {
    text-align: center;
    color: #9ca3af;
    font-size: 0.85rem;
    margin-top: 3rem;
    padding: 2rem 0;
    border-top: 1px solid #f0f0f5;
  }

  /* Hide Streamlit default header */
  #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# INIT
# ────────────────────────────────────────────────────────────────
afinn_scorer = Afinn()

EMOTIONS      = list(EMOTION_META.keys())
EMOTION_EMOJIS = {e: EMOTION_META[e]["emoji"] for e in EMOTIONS}
EMOTION_COLORS = {e: EMOTION_META[e]["color"] for e in EMOTIONS}


# ────────────────────────────────────────────────────────────────
# TEXT EXTRACTION
# ────────────────────────────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


# ────────────────────────────────────────────────────────────────
# SENTIMENT ANALYSIS
# ────────────────────────────────────────────────────────────────
def tokenize(text: str):
    return re.findall(r"\b[a-z']+\b", text.lower())


def analyze_sentiment(text: str) -> dict:
    words = tokenize(text)
    raw_score = afinn_scorer.score(text)

    # Log normalization
    if raw_score != 0:
        sign = 1 if raw_score > 0 else -1
        log_score = sign * math.log10(1 + abs(raw_score))
    else:
        log_score = 0.0

    if   log_score > 0.3:  category, emoji = "Positive", "😀"
    elif log_score < -0.3: category, emoji = "Negative", "😡"
    else:                  category, emoji = "Neutral",  "😐"

    # Collect scored words
    neg_words, pos_words = [], []
    seen = set()
    for w in words:
        s = afinn_scorer.score(w)
        if w not in seen and s != 0:
            seen.add(w)
            (pos_words if s > 0 else neg_words).append(w)

    return {
        "raw_score":  raw_score,
        "log_score":  round(log_score, 3),
        "category":   category,
        "emoji":      emoji,
        "word_count": len(words),
        "neg_words":  neg_words,
        "pos_words":  pos_words,
        "text":       text,
    }


# ────────────────────────────────────────────────────────────────
# EMOTION ANALYSIS
# ────────────────────────────────────────────────────────────────
def analyze_emotions(text: str) -> dict:
    words = tokenize(text)
    scores = defaultdict(int)
    words_by_emotion = defaultdict(list)

    for w in words:
        if w in NRC_LEXICON:
            for e in NRC_LEXICON[w]:
                scores[e] += 1
                if w not in words_by_emotion[e]:
                    words_by_emotion[e].append(w)

    total = sum(scores.values())
    if total > 0:
        dominant = max(scores, key=scores.get)
    else:
        dominant = None

    # Ensure all emotions present
    for e in EMOTIONS:
        if e not in scores:
            scores[e] = 0

    return {
        "scores":          dict(scores),
        "dominant":        dominant,
        "words_by_emotion": dict(words_by_emotion),
        "total":           total,
    }


# ────────────────────────────────────────────────────────────────
# UI HELPERS
# ────────────────────────────────────────────────────────────────
def render_word_chips(words: list, chip_class: str = "chip-neg") -> str:
    return " ".join(
        f'<span class="word-chip {chip_class}">{w}</span>'
        for w in words
    )


def render_sentiment_results(result: dict):
    st.markdown("---")
    st.markdown("### 📊 Sentiment Results")

    # Score cards
    col1, col2, col3, col4 = st.columns(4)
    score_color = "positive" if result["log_score"] > 0.3 else ("negative" if result["log_score"] < -0.3 else "neutral")
    with col1:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Sentiment</div>
          <div class="metric-value">{result['emoji']}</div>
          <div class="metric-sub">{result['category']}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Score</div>
          <div class="metric-value {score_color}">{result['log_score']}</div>
          <div class="metric-sub">log-normalized</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Total Words</div>
          <div class="metric-value" style="color:#4e54c8">{result['word_count']}</div>
          <div class="metric-sub">tokens</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-label">Raw AFINN</div>
          <div class="metric-value" style="color:#8f94fb">{int(result['raw_score'])}</div>
          <div class="metric-sub">sum</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Positive words
    if result["pos_words"]:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown("**✅ Positive Words Detected**")
        st.markdown(render_word_chips(result["pos_words"], "chip-pos"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Negative words + suggestions
    if result["neg_words"]:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown("**⚠️ Negative Words Detected**")
        st.markdown(render_word_chips(result["neg_words"], "chip-neg"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Text preview with highlighting
    with st.expander("📄 View Highlighted Text", expanded=False):
        words_in_text = set(result["neg_words"] + result["pos_words"])
        if words_in_text:
            highlighted = result["text"]
            for w in result["pos_words"]:
                highlighted = re.sub(
                    rf'\b({re.escape(w)})\b',
                    r'<mark style="background:#d4f7e7;border-radius:3px;padding:1px 3px">\1</mark>',
                    highlighted, flags=re.IGNORECASE
                )
            for w in result["neg_words"]:
                highlighted = re.sub(
                    rf'\b({re.escape(w)})\b',
                    r'<mark style="background:#fde8ea;border-radius:3px;padding:1px 3px">\1</mark>',
                    highlighted, flags=re.IGNORECASE
                )
            st.markdown(
                f'<div style="line-height:1.9;font-size:0.95rem;max-height:400px;overflow-y:auto;'
                f'border:1px solid #e0e0ef;border-radius:12px;padding:1rem;">{highlighted}</div>',
                unsafe_allow_html=True
            )
        else:
            st.text(result["text"][:2000])


def render_emotion_results(emo: dict):
    if emo["total"] == 0:
        st.info("No emotion-linked words detected in this text.")
        return

    st.markdown('<div class="emotion-header-bar">🧠 Emotion Breakdown Analysis</div>',
                unsafe_allow_html=True)

    dominant = emo["dominant"]
    if dominant:
        dm = EMOTION_META[dominant]
        st.markdown(
            f'<div class="dominant-box" style="background:{dm["color"]}22; border:1.5px solid {dm["color"]}">'
            f'<span style="font-size:2.5rem">{dm["emoji"]}</span>'
            f'<div><div style="font-size:1.4rem;font-weight:800;color:{dm["color"]}">{dm["label"]}</div>'
            f'<div style="font-size:0.85rem;color:#6b7280">Dominant emotion · '
            f'{emo["scores"][dominant]} word{"s" if emo["scores"][dominant]!=1 else ""} detected</div></div>'
            f'</div>',
            unsafe_allow_html=True
        )

    col_chart, col_bars = st.columns([1, 1])

    # Sort by score
    sorted_emo = sorted(emo["scores"].items(), key=lambda x: x[1], reverse=True)
    labels = [f'{EMOTION_META[e]["emoji"]} {EMOTION_META[e]["label"]}' for e, _ in sorted_emo]
    values = [v for _, v in sorted_emo]
    colors = [EMOTION_META[e]["color"] for e, _ in sorted_emo]

    # Radar chart
    with col_chart:
        fig = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=labels + [labels[0]],
            fill='toself',
            fillcolor='rgba(78,84,200,0.15)',
            line=dict(color='rgba(78,84,200,0.8)', width=2),
            marker=dict(color=colors + [colors[0]], size=8),
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, showticklabels=False, gridcolor="#eee"),
                angularaxis=dict(gridcolor="#eee"),
            ),
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Progress bars
    with col_bars:
        max_v = values[0] if values[0] > 0 else 1
        total = emo["total"]
        for e, count in sorted_emo:
            m = EMOTION_META[e]
            pct = round((count / total) * 100) if total > 0 else 0
            bar_w = round((count / max_v) * 100) if max_v > 0 else 0
            st.markdown(
                f'<div style="margin-bottom:0.6rem">'
                f'<div style="display:flex;justify-content:space-between;font-size:0.82rem;font-weight:600">'
                f'<span>{m["emoji"]} {m["label"]}</span><span>{pct}% ({count})</span></div>'
                f'<div style="height:8px;background:#f0f0f5;border-radius:4px;overflow:hidden">'
                f'<div style="height:100%;width:{bar_w}%;background:{m["color"]};border-radius:4px;'
                f'transition:width 0.5s"></div></div></div>',
                unsafe_allow_html=True
            )

    # Words by emotion
    st.markdown("<br>**🔍 Words Contributing to Each Emotion**", unsafe_allow_html=True)
    active = [(e, v) for e, v in sorted_emo if v > 0]
    for e, _ in active:
        m = EMOTION_META[e]
        words = emo["words_by_emotion"].get(e, [])
        if words:
            tags = " ".join(
                f'<span style="background:{m["color"]}22;color:{m["color"]};'
                f'padding:0.25rem 0.65rem;border-radius:20px;font-size:0.78rem;font-weight:600;'
                f'display:inline-block;margin:0.2rem">{w}</span>'
                for w in words
            )
            st.markdown(
                f'<div style="margin-bottom:0.6rem">'
                f'<span style="font-size:0.75rem;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:0.05em;color:#9ca3af">{m["emoji"]} {m["label"]}</span><br>{tags}'
                f'</div>',
                unsafe_allow_html=True
            )


# ────────────────────────────────────────────────────────────────
# MAIN APP
# ────────────────────────────────────────────────────────────────
def main():
    # Header
    st.markdown("""
    <div class="main-header">
      <h1>📊 Sentiment Analyzer Pro</h1>
      <p>AI-powered sentiment & emotion analysis for documents and text</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Input Section ──
    tab_file, tab_text = st.tabs(["📁 Upload File", "✏️ Paste Text"])

    text_to_analyze = None
    source_name = None

    with tab_file:
        st.markdown("Upload a **PDF** or **Word (.docx)** document to analyze.")
        uploaded = st.file_uploader(
            "Choose a file",
            type=["pdf", "docx"],
            help="Supported: PDF and DOCX files up to 200MB"
        )
        if uploaded:
            if st.button("🔍 Analyze Document", key="btn_file", type="primary"):
                with st.spinner("Extracting text…"):
                    try:
                        raw = uploaded.read()
                        if uploaded.name.endswith(".pdf"):
                            text_to_analyze = extract_text_from_pdf(raw)
                        else:
                            text_to_analyze = extract_text_from_docx(raw)
                        source_name = uploaded.name
                        if not text_to_analyze.strip():
                            st.error("⚠️ Could not extract any text from this file. It may be scanned/image-based.")
                            text_to_analyze = None
                    except Exception as ex:
                        st.error(f"⚠️ Error reading file: {ex}")

    with tab_text:
        st.markdown("Paste any text — reviews, emails, feedback, articles, or speeches.")
        user_text = st.text_area(
            "Your text",
            height=220,
            placeholder="Paste your text here…",
            label_visibility="collapsed"
        )
        if st.button("🔍 Analyze Text", key="btn_text", type="primary"):
            if user_text.strip():
                text_to_analyze = user_text.strip()
                source_name = "Pasted Text"
            else:
                st.warning("Please enter some text first.")

    # ── Results ──
    if text_to_analyze:
        with st.spinner("Analyzing sentiment & emotions…"):
            sentiment = analyze_sentiment(text_to_analyze)
            emotions  = analyze_emotions(text_to_analyze)

        st.success(f"✅ Analysis complete for **{source_name}**")

        # Sentiment
        render_sentiment_results(sentiment)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # Emotions
        render_emotion_results(emotions)

    # Footer
    st.markdown(
        '<div class="footer">© 2026 Sentiment Analyzer Pro · '
        'Powered by AFINN-165 & NRC Emotion Lexicon</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
