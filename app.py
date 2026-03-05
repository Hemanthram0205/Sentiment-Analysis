import re, io, math
from collections import defaultdict

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from afinn import Afinn
import pdfplumber
from docx import Document

# ─────────────────────────────────────────────────────────────
# NRC Word-Emotion Association Lexicon
# ─────────────────────────────────────────────────────────────
NRC_LEXICON = {
    "abandon": ["fear","sadness"], "abhor": ["anger","disgust"],
    "abhorrent": ["anger","disgust"], "abuse": ["anger","disgust","sadness"],
    "accomplish": ["joy","anticipation","trust"], "achievement": ["joy","anticipation"],
    "admire": ["joy","trust"], "adore": ["joy","trust"],
    "adventure": ["anticipation","joy","surprise"], "afraid": ["fear","sadness"],
    "aggression": ["anger"], "agony": ["sadness","fear"],
    "alarm": ["fear","surprise"], "amazing": ["joy","surprise"],
    "anger": ["anger"], "anguish": ["sadness","fear"],
    "annoy": ["anger","disgust"], "anxiety": ["fear","sadness"],
    "appalled": ["disgust","anger","surprise"], "appreciate": ["joy","trust"],
    "aspire": ["anticipation","joy"], "astound": ["surprise","joy"],
    "attack": ["anger","fear"], "awe": ["surprise","joy","trust"],
    "awful": ["sadness","disgust"], "bad": ["sadness","disgust"],
    "beautiful": ["joy","trust"], "beloved": ["joy","trust"],
    "bereave": ["sadness"], "bereavement": ["sadness","fear"],
    "betrayal": ["anger","sadness","disgust"], "bewildered": ["surprise","fear"],
    "bliss": ["joy","trust"], "bold": ["anticipation","trust"],
    "boring": ["sadness","disgust"], "brave": ["anticipation","trust","joy"],
    "bravery": ["trust","anticipation"], "calm": ["trust","joy"],
    "catastrophe": ["fear","sadness","surprise"], "celebrate": ["joy","anticipation"],
    "chaos": ["fear","anger","surprise"], "charm": ["joy","trust"],
    "cheat": ["anger","disgust","sadness"], "cheerful": ["joy"],
    "comfort": ["joy","trust"], "compassion": ["trust","sadness","joy"],
    "confident": ["trust","anticipation","joy"], "confusion": ["fear","surprise"],
    "courageous": ["trust","anticipation"], "crime": ["anger","disgust","fear"],
    "cruel": ["disgust","anger","sadness"], "curious": ["anticipation","surprise","joy"],
    "danger": ["fear","anticipation"], "death": ["sadness","fear"],
    "deceit": ["disgust","anger"], "defeat": ["sadness","anger"],
    "depressed": ["sadness"], "depression": ["sadness","fear"],
    "desperate": ["fear","sadness","anticipation"], "destroy": ["anger","sadness"],
    "devastated": ["sadness","surprise"], "devoted": ["joy","trust"],
    "dirty": ["disgust"], "disappoint": ["sadness","anger"],
    "disaster": ["fear","sadness","surprise"], "distress": ["sadness","fear"],
    "doubt": ["fear","sadness"], "dreadful": ["fear","disgust"],
    "ecstasy": ["joy","surprise"], "effective": ["trust","anticipation"],
    "empathy": ["trust","sadness","joy"], "encourage": ["trust","anticipation","joy"],
    "enjoy": ["joy","anticipation"], "enlighten": ["surprise","trust","anticipation"],
    "enthusiasm": ["joy","anticipation"], "excited": ["joy","anticipation","surprise"],
    "exhausted": ["sadness"], "fail": ["sadness","anger"],
    "faithful": ["trust","joy"], "fantastic": ["joy","surprise"],
    "fear": ["fear"], "fearful": ["fear","sadness"],
    "fierce": ["anger","anticipation"], "forgive": ["trust","joy"],
    "fraud": ["disgust","anger"], "free": ["joy","anticipation","trust"],
    "friendly": ["trust","joy"], "frightened": ["fear","surprise"],
    "frustrated": ["anger","sadness"], "fun": ["joy","anticipation"],
    "funny": ["joy","surprise"], "gentle": ["trust","joy"],
    "glad": ["joy"], "glory": ["joy","trust","anticipation"],
    "good": ["joy","trust"], "graceful": ["joy","trust"],
    "grateful": ["joy","trust"], "great": ["joy","anticipation"],
    "grief": ["sadness","fear"], "growth": ["anticipation","joy","trust"],
    "guilty": ["sadness","fear"], "happiness": ["joy"],
    "happy": ["joy"], "harm": ["anger","sadness","fear"],
    "hate": ["anger","disgust"], "helpless": ["sadness","fear"],
    "heroic": ["trust","joy","anticipation"], "hopeful": ["anticipation","joy","trust"],
    "hopeless": ["sadness","fear"], "horrible": ["disgust","fear","sadness"],
    "hostile": ["anger","disgust"], "humble": ["trust","joy"],
    "hurt": ["sadness","anger"], "ignorant": ["anger","disgust"],
    "injustice": ["anger","sadness","disgust"], "inspire": ["joy","anticipation","trust"],
    "insult": ["anger","disgust","sadness"], "jealous": ["anger","sadness","disgust"],
    "joyful": ["joy"], "joyous": ["joy","surprise"],
    "jubilant": ["joy","surprise"], "kind": ["trust","joy"],
    "kindness": ["trust","joy"], "lazy": ["disgust","sadness"],
    "lonely": ["sadness"], "love": ["joy","trust","anticipation"],
    "loyal": ["trust","joy"], "magnificent": ["joy","surprise","trust"],
    "manipulate": ["anger","disgust"], "melancholy": ["sadness"],
    "miracle": ["surprise","joy","trust"], "miserable": ["sadness"],
    "motivated": ["anticipation","joy","trust"], "mourning": ["sadness","fear"],
    "neglect": ["sadness","anger","disgust"], "nervous": ["fear"],
    "nightmare": ["fear","sadness"], "optimistic": ["anticipation","joy","trust"],
    "outstanding": ["joy","surprise","trust"], "overwhelmed": ["fear","surprise","sadness"],
    "panic": ["fear","surprise"], "passionate": ["joy","anticipation","trust"],
    "patience": ["trust","anticipation"], "peaceful": ["joy","trust"],
    "pessimistic": ["sadness","fear"], "powerful": ["trust","anticipation","joy"],
    "prejudice": ["disgust","anger"], "pride": ["joy","trust","anticipation"],
    "purposeful": ["anticipation","trust"], "rage": ["anger"],
    "regret": ["sadness"], "rejected": ["sadness","anger"],
    "resilient": ["trust","anticipation"], "respect": ["trust","joy"],
    "restore": ["trust","anticipation","joy"], "ruin": ["sadness","anger","disgust"],
    "sad": ["sadness"], "sadness": ["sadness"],
    "selfish": ["disgust","anger"], "shame": ["sadness","fear","disgust"],
    "shocked": ["surprise","fear"], "sincere": ["trust"],
    "sorrow": ["sadness"], "stable": ["trust"],
    "stress": ["fear","anger","sadness"], "struggle": ["sadness","fear","anger"],
    "success": ["joy","trust","anticipation"], "suffering": ["sadness","fear"],
    "support": ["trust","joy"], "surprise": ["surprise"],
    "terror": ["fear"], "thankful": ["joy","trust"],
    "thoughtful": ["trust","anticipation"], "toxic": ["disgust","anger","sadness"],
    "tragedy": ["sadness","fear"], "trust": ["trust"],
    "truthful": ["trust"], "uncertain": ["fear","anticipation"],
    "unfair": ["anger","sadness","disgust"], "upset": ["sadness","anger"],
    "valuable": ["trust","anticipation"], "victorious": ["joy","anticipation","trust"],
    "violence": ["anger","fear","disgust"], "vulnerable": ["fear","sadness"],
    "warmth": ["joy","trust"], "wonderful": ["joy","surprise","trust"],
    "worry": ["fear","sadness"], "worthless": ["sadness","disgust"],
    "zealous": ["anticipation","anger"],
}

EMOTION_META = {
    "joy":          {"emoji": "😊", "color": "#f9d71c", "label": "Joy"},
    "sadness":      {"emoji": "😢", "color": "#74b9ff", "label": "Sadness"},
    "anger":        {"emoji": "😡", "color": "#ff4757", "label": "Anger"},
    "fear":         {"emoji": "😨", "color": "#a29bfe", "label": "Fear"},
    "disgust":      {"emoji": "🤢", "color": "#55efc4", "label": "Disgust"},
    "surprise":     {"emoji": "😮", "color": "#fd79a8", "label": "Surprise"},
    "trust":        {"emoji": "🤝", "color": "#00cec9", "label": "Trust"},
    "anticipation": {"emoji": "⏳", "color": "#e17055", "label": "Anticipation"},
}


# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sentiment Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  #MainMenu, footer, header { visibility: hidden; }
  .page-hero {
    background: linear-gradient(135deg, #4e54c8, #8f94fb);
    padding: 2.5rem 2rem; border-radius: 16px; color: white !important;
    text-align: center; margin-bottom: 2rem;
  }
  .page-hero h1 { font-size: 2rem; font-weight: 800; margin: 0; color: white !important; }
  .page-hero p  { font-size: 1rem; opacity: 0.88; margin: 0.4rem 0 0; color: white !important; }
  .card {
    background: white !important; border: 1px solid #e0e0ef; border-radius: 14px;
    padding: 1.5rem; box-shadow: 0 4px 16px rgba(0,0,0,0.06); margin-bottom: 1rem;
    color: #1f2937 !important;
  }
  .card h3, .card h4, .card p, .card li, .card b, .card span, .card a { color: #1f2937 !important; }
  .card h3[style*="color:#4e54c8"], .card h4[style*="color:#4e54c8"] { color: #4e54c8 !important; }
  .metric-card {
    background: white !important; border: 1px solid #e0e0ef; border-radius: 16px;
    padding: 1.25rem; text-align: center; box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    color: #1f2937 !important;
  }
  .metric-label { font-size:.72rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.05em; color:#6b7280 !important; margin-bottom:.3rem; }
  .metric-value { font-size:2rem; font-weight:800; line-height:1.1; color:#1f2937 !important; }
  .metric-sub   { font-size:.78rem; color:#9ca3af !important; margin-top:.25rem; }
  .positive{color:#2ed573 !important} .negative{color:#ff4757 !important} .neutral{color:#9ca3af !important}
  .result-box {
    background:#f8f9ff !important; border:1px solid #e0e0ef; border-radius:12px;
    padding:1.1rem 1.4rem; margin-bottom:.9rem; color:#1f2937 !important;
  }
  .result-box b { color:#1f2937 !important; }
  .word-chip { display:inline-block; padding:.3rem .75rem; border-radius:20px;
    font-size:.78rem; font-weight:600; margin:.2rem; }
  .chip-neg{background:rgba(255,71,87,.15) !important;color:#ff4757 !important}
  .chip-pos{background:rgba(46,213,115,.15) !important;color:#1a9e4e !important}
  .emotion-tag { display:inline-block; padding:.25rem .65rem; border-radius:20px;
    font-size:.78rem; font-weight:600; margin:.2rem .2rem .2rem 0; }
  .footer { text-align:center; color:#9ca3af !important; font-size:.83rem;
    margin-top:3rem; padding:1.5rem 0; border-top:1px solid #f0f0f5; }
  /* Force dark text in all inline HTML divs */
  [data-testid="stMarkdownContainer"] p,
  [data-testid="stMarkdownContainer"] li,
  [data-testid="stMarkdownContainer"] span { color: inherit; }
  /* Keep sidebar always open — hide all collapse/expand toggle buttons */
  [data-testid="collapsedControl"],
  button[kind="header"],
  section[data-testid="stSidebar"] > div:first-child > div > button,
  .st-emotion-cache-1ihkpx7 { display: none !important; }
  /* Ensure sidebar itself is never hidden */
  section[data-testid="stSidebar"] {
    min-width: 220px !important;
    transform: none !important;
    visibility: visible !important;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ANALYSIS ENGINE
# ─────────────────────────────────────────────────────────────
afinn_scorer = Afinn()

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
    cat, emo = ("Positive","😀") if log > 0.3 else (("Negative","😡") if log < -0.3 else ("Neutral","😐"))
    neg, pos, seen = [], [], set()
    for w in words:
        s = afinn_scorer.score(w)
        if w not in seen and s != 0:
            seen.add(w); (pos if s > 0 else neg).append(w)
    return dict(raw=raw, log=round(log,3), cat=cat, emo=emo, wc=len(words), neg=neg, pos=pos, text=text)

def analyze_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s for s in sentences if len(tokenize(s)) > 0]
    if len(sentences) < 2: return None
    data = []
    for i, s in enumerate(sentences):
        sc = afinn_scorer.score(s)
        data.append({"id": i+1, "text": s, "score": sc})
    return data

def analyze_emotions(text):
    words = tokenize(text)
    scores = defaultdict(int); wbe = defaultdict(list)
    for w in words:
        for e in NRC_LEXICON.get(w, []):
            scores[e] += 1
            if w not in wbe[e]: wbe[e].append(w)
    total = sum(scores.values())
    dom = max(scores, key=scores.get) if total > 0 else None
    for e in EMOTION_META: scores.setdefault(e, 0)
    return dict(scores=dict(scores), dominant=dom, wbe=dict(wbe), total=total)

def chips(words, cls):
    return " ".join(f'<span class="word-chip {cls}">{w}</span>' for w in words)

# ─────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION (only when logged in)
# ─────────────────────────────────────────────────────────────
PAGES = [
    ("🏠", "Home"),
    ("📊", "Analyzer"),
    ("🛠️", "Services"),
    ("💬", "Support"),
    ("📞", "Contact"),
    ("❓", "Help"),
]

def show_sidebar():
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.get('username','User')}")
        st.markdown("---")
        for icon, name in PAGES:
            if st.button(f"{icon} {name}", key=f"nav_{name}", use_container_width=True):
                st.session_state["page"] = name
                st.rerun()
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ─────────────────────────────────────────────────────────────
# PAGE: LOGIN
# ─────────────────────────────────────────────────────────────
def page_login():
    st.markdown("""
    <div style="max-width:420px;margin:3rem auto 0">
    <div style="text-align:center;margin-bottom:1.5rem">
      <div style="font-size:3.5rem">📊</div>
      <h1 style="font-size:1.8rem;font-weight:800;color:#4e54c8;margin:.3rem 0">Sentiment Analyzer Pro</h1>
      <p style="color:#6b7280;margin:0">AI-powered sentiment & emotion analysis</p>
    </div></div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        tab_in, tab_up = st.tabs(["Sign In", "Sign Up"])

        with tab_in:
            with st.form("login_form"):
                uname = st.text_input("Username", placeholder="demo")
                pwd   = st.text_input("Password", type="password", placeholder="demo123")
                ok    = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            if ok:
                if not uname or not pwd:
                    st.error("Fill in both fields.")
                else:
                    try:    users = dict(st.secrets["users"])
                    except: users = {"demo": "demo123", "admin": "admin123"}
                    if users.get(uname) == pwd:
                        st.session_state.update(authenticated=True, username=uname, page="Home")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials.")
            st.caption("Demo: `demo` / `demo123`")

        with tab_up:
            with st.form("signup_form", clear_on_submit=True):
                sname  = st.text_input("Full Name")
                semail = st.text_input("Email")
                spass  = st.text_input("Password (min 8 chars)", type="password")
                sconf  = st.text_input("Confirm Password", type="password")
                sreg   = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            if sreg:
                if not all([sname, semail, spass, sconf]):    st.error("All fields required.")
                elif len(spass) < 8:                          st.error("Password too short.")
                elif spass != sconf:                          st.error("Passwords don't match.")
                else:
                    st.session_state.update(authenticated=True, username=semail.split("@")[0], page="Home")
                    st.rerun()

    st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PAGE: ANALYZER
# ─────────────────────────────────────────────────────────────
def page_analyzer():
    st.markdown('<div class="page-hero"><h1>📊 Sentiment Analyzer</h1><p>Upload a document or paste text for instant sentiment & emotion insights</p></div>', unsafe_allow_html=True)

    tab_file, tab_text = st.tabs(["📁 Upload File (.pdf / .docx)", "✏️ Paste Text"])
    text_to_analyze = source_name = None

    with tab_file:
        up = st.file_uploader("Choose a file", type=["pdf","docx"])
        if up and st.button("🔍 Analyze Document", type="primary"):
            with st.spinner("Extracting text…"):
                try:
                    raw = up.read()
                    txt = extract_pdf(raw) if up.name.endswith(".pdf") else extract_docx(raw)
                    if txt.strip(): text_to_analyze, source_name = txt.strip(), up.name
                    else: st.error("⚠️ No readable text found (file may be image-based).")
                except Exception as ex: st.error(f"⚠️ Error: {ex}")

    with tab_text:
        user_text = st.text_area("Paste your text", height=200, label_visibility="collapsed",
                                  placeholder="Paste reviews, emails, feedback, articles…")
        if st.button("🔍 Analyze Text", type="primary"):
            if user_text.strip(): text_to_analyze, source_name = user_text.strip(), "Pasted Text"
            else: st.warning("Please enter some text.")

    if text_to_analyze:
        with st.spinner("Analyzing…"):
            sa = analyze_sentiment(text_to_analyze)
            ea = analyze_emotions(text_to_analyze)
        st.success(f"✅ Analysis complete for **{source_name}**")
        st.markdown("---")

        # Sentiment score cards
        st.markdown("### 📊 Sentiment Results")
        c1,c2,c3,c4 = st.columns(4)
        sc = "positive" if sa["log"]>0.3 else ("negative" if sa["log"]<-0.3 else "neutral")
        with c1: st.markdown(f'<div class="metric-card"><div class="metric-label">Sentiment</div><div class="metric-value">{sa["emo"]}</div><div class="metric-sub">{sa["cat"]}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="metric-label">Score</div><div class="metric-value {sc}">{sa["log"]}</div><div class="metric-sub">log-normalized</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><div class="metric-label">Total Words</div><div class="metric-value" style="color:#4e54c8">{sa["wc"]}</div><div class="metric-sub">tokens</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card"><div class="metric-label">Raw AFINN</div><div class="metric-value" style="color:#8f94fb">{int(sa["raw"])}</div><div class="metric-sub">sum</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if sa["pos"]:
            st.markdown(f'<div class="result-box"><b>✅ Positive Words</b><br>{chips(sa["pos"],"chip-pos")}</div>', unsafe_allow_html=True)
        if sa["neg"]:
            st.markdown(f'<div class="result-box"><b>⚠️ Negative Words</b><br>{chips(sa["neg"],"chip-neg")}</div>', unsafe_allow_html=True)

        with st.expander("📄 View Highlighted Text"):
            hl = sa["text"]
            for w in sa["pos"]: hl = re.sub(rf'\b({re.escape(w)})\b', r'<mark style="background:#d4f7e7;border-radius:3px;padding:1px 3px">\1</mark>', hl, flags=re.IGNORECASE)
            for w in sa["neg"]: hl = re.sub(rf'\b({re.escape(w)})\b', r'<mark style="background:#fde8ea;border-radius:3px;padding:1px 3px">\1</mark>', hl, flags=re.IGNORECASE)
            st.markdown(f'<div style="line-height:1.9;font-size:.92rem;max-height:380px;overflow-y:auto;border:1px solid #e0e0ef;border-radius:12px;padding:1rem">{hl}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🧠 Emotion Breakdown")

        if ea["total"] == 0:
            st.info("No emotion-linked words detected.")
        else:
            dom = ea["dominant"]
            if dom:
                dm = EMOTION_META[dom]
                st.markdown(f'<div style="background:{dm["color"]}22;border:1.5px solid {dm["color"]};border-radius:12px;padding:1rem 1.25rem;margin-bottom:1rem"><span style="font-size:2rem">{dm["emoji"]}</span> <span style="font-size:1.3rem;font-weight:800;color:{dm["color"]}">{dm["label"]}</span> <span style="color:#6b7280;font-size:.83rem"> · Dominant emotion · {ea["scores"][dom]} word{"s" if ea["scores"][dom]!=1 else ""}</span></div>', unsafe_allow_html=True)

            sorted_emo = sorted(ea["scores"].items(), key=lambda x: x[1], reverse=True)
            labels = [f'{EMOTION_META[e]["emoji"]} {EMOTION_META[e]["label"]}' for e,_ in sorted_emo]
            values = [v for _,v in sorted_emo]
            colors = [EMOTION_META[e]["color"] for e,_ in sorted_emo]

            cr, cb = st.columns(2)
            with cr:
                fig = go.Figure(go.Scatterpolar(
                    r=values+[values[0]], theta=labels+[labels[0]], fill='toself',
                    fillcolor='rgba(78,84,200,0.15)', line=dict(color='rgba(78,84,200,0.8)',width=2),
                    marker=dict(color=colors+[colors[0]], size=8)))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True,showticklabels=False,gridcolor="#eee"),angularaxis=dict(gridcolor="#eee")), showlegend=False,height=300,margin=dict(t=20,b=20,l=20,r=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            with cb:
                total_e = ea["total"] or 1; max_v = values[0] or 1
                for e,count in sorted_emo:
                    m=EMOTION_META[e]; pct=round(count/total_e*100); bw=round(count/max_v*100)
                    st.markdown(f'<div style="margin-bottom:.6rem"><div style="display:flex;justify-content:space-between;font-size:.82rem;font-weight:600"><span>{m["emoji"]} {m["label"]}</span><span>{pct}% ({count})</span></div><div style="height:8px;background:#f0f0f5;border-radius:4px;overflow:hidden"><div style="height:100%;width:{bw}%;background:{m["color"]};border-radius:4px"></div></div></div>', unsafe_allow_html=True)

            st.markdown("<br>**🔍 Words by Emotion**", unsafe_allow_html=True)
            for e,count in sorted_emo:
                if count==0: continue
                m=EMOTION_META[e]; ws=ea["wbe"].get(e,[])
                if ws:
                    tags=" ".join(f'<span class="emotion-tag" style="background:{m["color"]}22;color:{m["color"]}">{w}</span>' for w in ws)
                    st.markdown(f'<div style="margin-bottom:.6rem"><div style="font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#9ca3af">{m["emoji"]} {m["label"]}</div>{tags}</div>', unsafe_allow_html=True)

        # Sentence-Level Analysis
        sentences = analyze_sentences(text_to_analyze)
        if sentences:
            st.markdown("---")
            st.markdown("### 📈 Sentence-Level Sentiment Flow")
            s_df = pd.DataFrame(sentences)
            fig_s = go.Figure()
            fig_s.add_trace(go.Bar(
                x=s_df["id"], y=s_df["score"],
                text=s_df["text"].str.slice(0, 50) + "...",
                marker_color=["#2ed573" if s > 0 else "#ff4757" if s < 0 else "#9ca3af" for s in s_df["score"]],
                hovertemplate="Sentence %{x}<br>Score: %{y}<br>Text: %{text}<extra></extra>"
            ))
            fig_s.update_layout(height=250, margin=dict(l=0,r=0,t=30,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Sentence Sequence", yaxis_title="Sentiment Score")
            st.plotly_chart(fig_s, use_container_width=True)

        st.markdown("---")
        # Generate Report for Download
        report_text = f"Sentiment Analysis Report - {source_name}\n{'='*50}\n\n"
        report_text += f"Sentiment Score (Normalized): {sa['log']}\nSentiment Category: {sa['cat']} {sa['emo']}\nRaw AFINN Score: {int(sa['raw'])}\nWord Count: {sa['wc']}\n\n"
        report_text += f"-- Positive Words --\n{', '.join(sa['pos'])}\n\n-- Negative Words --\n{', '.join(sa['neg'])}\n\n"
        report_text += f"-- Emotion Breakdown --\n"
        for e,count in sorted_emo: report_text += f"{EMOTION_META[e]['label']}: {count}\n"
        
        # Download Button
        st.download_button(
            label="📥 Download Detailed Report",
            data=report_text,
            file_name=f"Sentiment_Report.txt",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )

    st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro · AFINN-165 & NRC Emotion Lexicon</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────────────────────
def page_home():
    st.markdown('<div class="page-hero"><h1>🏠 Home</h1><p>Welcome to Sentiment Analyzer Pro</p></div>', unsafe_allow_html=True)
    c1,c2 = st.columns([2,1])
    with c1:
        st.markdown("""
        <div class="card"><h3 style="color:#4e54c8">🎯 Our Mission</h3>
        <p>Sentiment Analyzer Pro empowers individuals, researchers, and businesses to instantly understand the emotional tone of any text — from customer reviews to academic documents.</p></div>
        <div class="card"><h3 style="color:#4e54c8">🔬 How It Works</h3>
        <p>We combine two proven NLP methods:</p>
        <ul><li><b>AFINN-165</b> — 3,382 words rated −5 to +5, with log normalization for balanced scoring.</li>
        <li><b>NRC Emotion Lexicon</b> — maps words to 8 basic emotions developed by NRC Canada.</li></ul></div>
        <div class="card"><h3 style="color:#4e54c8">📂 Supported Formats</h3>
        <p>Upload <b>PDF</b> or <b>Word (.docx)</b> documents, or paste text directly. All processing is real-time.</p></div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card" style="text-align:center"><div style="font-size:3rem">📊</div>
        <h3 style="color:#4e54c8">Version 2.0</h3>
        <hr style="border-color:#f0f0f5">
        <p style="font-size:.85rem">Built with Python, Streamlit, AFINN-165, NRC Lexicon, Pandas & Plotly.</p></div>
        <div class="card" style="text-align:center"><h4 style="color:#4e54c8">🏆 Key Stats</h4>
        <p><b>3,382</b> AFINN words</p><p><b>8</b> Emotion categories</p>
        <p><b>300+</b> Emotion-mapped words</p><p><b>PDF & DOCX</b> support</p></div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PAGE: SERVICES
# ─────────────────────────────────────────────────────────────
def page_services():
    st.markdown('<div class="page-hero"><h1>🛠️ Services</h1><p>Everything Sentiment Analyzer Pro offers</p></div>', unsafe_allow_html=True)
    services = [
        ("📄","Document Analysis","Upload PDF or Word docs up to 200MB. Text is extracted automatically."),
        ("✏️","Text Analysis","Paste any raw text — emails, reviews, speeches — results in under a second."),
        ("😀😡😐","Sentiment Scoring","AFINN-165 with log-normalization classifies Positive, Negative, or Neutral."),
        ("🧠","Emotion Detection","8-emotion NRC breakdown: Joy, Sadness, Anger, Fear, Disgust, Surprise, Trust, Anticipation."),
        ("🕸️","Radar Chart","Interactive Plotly radar showing emotion distribution — hover, zoom, explore."),
        ("⚠️","Negative Word ID","Every negative word is individually listed and highlighted in your text."),
        ("✅","Positive Word ID","Positive words are detected and color-coded green for easy review."),
        ("🔑","Secure Auth","Sign-in required. Analyses are session-scoped and private to your account."),
    ]
    cols = st.columns(2)
    for i,(icon,title,desc) in enumerate(services):
        with cols[i%2]:
            st.markdown(f'<div class="card"><div style="display:flex;align-items:flex-start;gap:1rem"><div style="font-size:2rem;min-width:2.5rem">{icon}</div><div><h4 style="margin:0 0 .4rem;color:#4e54c8">{title}</h4><p style="margin:0;color:#6b7280;font-size:.9rem">{desc}</p></div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PAGE: SUPPORT
# ─────────────────────────────────────────────────────────────
def page_support():
    st.markdown('<div class="page-hero"><h1>💬 Support</h1><p>Get help with any issue or question</p></div>', unsafe_allow_html=True)
    c1,c2 = st.columns([3,2])
    with c1:
        st.markdown("### ❓ Frequently Asked Questions")
        faqs = [
            ("What file formats are supported?", "**PDF** (.pdf) and **Word** (.docx). Legacy .doc files must be converted to .docx first."),
            ("Why is my score 0?", "Your text may not contain AFINN-scored words. Try more expressive language, or positive and negative words may be cancelling out."),
            ("What does log-normalized mean?", "Score = log₁₀(1 + |raw|). Values above 0.3 = Positive, below −0.3 = Negative."),
            ("Why are some words not highlighted?", "Only words in the AFINN-165 lexicon (3,382 English words) are scored. Proper nouns and technical terms aren't included."),
            ("Is my document stored?", "No. All processing is in-session. Nothing is saved to any server."),
        ]
        for q,a in faqs:
            with st.expander(q): st.markdown(a)
    with c2:
        st.markdown("""
        <div class="card"><p>📧 <b>Email</b><br>
        <a href="mailto:support@sentimentpro.com" style="color:#4e54c8">support@sentimentpro.com</a></p>
        <hr style="border-color:#f0f0f5"><p>⏱️ <b>Response time</b><br>Within 24 hours</p></div>
        """, unsafe_allow_html=True)
        st.markdown("### 📩 Send a Message")
        with st.form("support_form"):
            nm  = st.text_input("Your Name"); em = st.text_input("Your Email")
            sub = st.selectbox("Subject",["General Question","Bug Report","Feature Request","Account Issue"])
            msg = st.text_area("Message", height=100)
            if st.form_submit_button("Send Message", type="primary", use_container_width=True):
                if nm and em and msg: st.success("✅ Message sent! We'll reply within 24 hours.")
                else: st.error("Please fill in all fields.")
    st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PAGE: CONTACT
# ─────────────────────────────────────────────────────────────
def page_contact():
    st.markdown('<div class="page-hero"><h1>📞 Contact</h1><p>Stay connected with Sentiment Analyzer Pro</p></div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card" style="text-align:center"><div style="font-size:2.5rem">🐙</div>
        <h3 style="color:#4e54c8">GitHub</h3>
        <p style="color:#6b7280;font-size:.9rem">Star the project, report issues, or contribute!</p>
        <a href="https://github.com/Hemanthram0205/Sentiment-Analysis" target="_blank"
           style="display:inline-block;background:#4e54c8;color:white;padding:.6rem 1.5rem;
           border-radius:8px;text-decoration:none;font-weight:600;margin-top:.5rem">View on GitHub</a></div>
        <div class="card" style="text-align:center"><div style="font-size:2.5rem">📧</div>
        <h3 style="color:#4e54c8">Email</h3>
        <a href="mailto:support@sentimentpro.com"
           style="display:inline-block;background:#4e54c8;color:white;padding:.6rem 1.5rem;
           border-radius:8px;text-decoration:none;font-weight:600;margin-top:.5rem">Send Email</a></div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("### 📰 Stay Updated")
        with st.form("newsletter_form"):
            nl_name=st.text_input("Name"); nl_email=st.text_input("Email address")
            if st.form_submit_button("Subscribe", type="primary", use_container_width=True):
                if nl_email: st.success(f"✅ {nl_name or 'You'} are now subscribed!")
                else: st.error("Please enter your email.")
    st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# PAGE: HELP
# ─────────────────────────────────────────────────────────────
def page_help():
    st.markdown('<div class="page-hero"><h1>❓ Help Center</h1><p>Step-by-step guides to get the most out of Sentiment Analyzer Pro</p></div>', unsafe_allow_html=True)
    c1,c2 = st.columns([3,2])
    with c1:
        st.markdown("### 🚀 Quick Start Guide")
        steps = [
            ("1️⃣","Sign In","Log in with your credentials. Use demo/demo123 to try the app."),
            ("2️⃣","Choose Input","Click Analyzer in the sidebar. Choose file upload or paste text."),
            ("3️⃣","Upload or Paste","Drag & drop a PDF/DOCX file, or type/paste text directly."),
            ("4️⃣","Run Analysis","Click the Analyze button. Results appear instantly."),
            ("5️⃣","Read Results","Review the Sentiment Score cards and positive/negative word lists."),
            ("6️⃣","Explore Emotions","The radar chart and bars show your 8-emotion breakdown."),
            ("7️⃣","Highlighted Text","Expand 'View Highlighted Text' to see green/red word highlights."),
        ]
        for icon,title,desc in steps:
            st.markdown(f'<div class="card" style="display:flex;align-items:flex-start;gap:1rem"><div style="font-size:1.8rem;min-width:2.5rem">{icon}</div><div><h4 style="margin:0 0 .3rem;color:#4e54c8">{title}</h4><p style="margin:0;color:#6b7280;font-size:.9rem">{desc}</p></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("### 📖 Score Guide")
        st.markdown("""
        <div class="card"><h4 style="color:#2ed573">😀 Positive (> 0.3)</h4>
        <p style="font-size:.85rem;color:#6b7280">More positive words. Common in praise and optimistic writing.</p></div>
        <div class="card"><h4 style="color:#9ca3af">😐 Neutral (−0.3 to 0.3)</h4>
        <p style="font-size:.85rem;color:#6b7280">Balanced or flat text. Common in formal writing and reports.</p></div>
        <div class="card"><h4 style="color:#ff4757">😡 Negative (< −0.3)</h4>
        <p style="font-size:.85rem;color:#6b7280">More negative words. Common in complaints and criticism.</p></div>
        """, unsafe_allow_html=True)
        st.markdown("### 🧠 8 Emotions")
        for e,m in EMOTION_META.items():
            st.markdown(f'<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.4rem"><span style="font-size:1.2rem">{m["emoji"]}</span><b style="font-size:.85rem">{m["label"]}</b></div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated"):
    page_login()
else:
    show_sidebar()
    current = st.session_state.get("page", "Home")
    if   current == "Home":     page_home()
    elif current == "Analyzer": page_analyzer()
    elif current == "Services": page_services()
    elif current == "Support":  page_support()
    elif current == "Contact":  page_contact()
    elif current == "Help":     page_help()
    else:                       page_home()
