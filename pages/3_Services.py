import streamlit as st
from auth import require_auth, show_nav

st.set_page_config(page_title="Services — Sentiment Pro", page_icon="🛠️", layout="wide")
require_auth()
show_nav("Services")

st.markdown("""
<div class="page-hero">
  <h1>🛠️ Services</h1>
  <p>Everything Sentiment Analyzer Pro offers</p>
</div>
""", unsafe_allow_html=True)

services = [
    ("📄", "Document Analysis", "Upload PDF or Word documents up to 200MB. Our engine extracts text automatically and delivers instant sentiment scores."),
    ("✏️", "Text Analysis", "Paste any raw text — emails, reviews, feedback, speeches — and get results in under a second."),
    ("😀😡😐", "Sentiment Scoring", "AFINN-165 scoring with log-normalization classifies text as Positive, Negative, or Neutral with a precise numeric score."),
    ("🧠", "Emotion Detection", "NRC-based 8-emotion breakdown: Joy, Sadness, Anger, Fear, Disgust, Surprise, Trust, and Anticipation."),
    ("🕸️", "Radar Chart Visualization", "Interactive Plotly radar chart shows your emotion distribution at a glance. Fully interactive — hover, zoom, and export."),
    ("⚠️", "Negative Word Identification", "Every negative word is individually identified, listed, and highlighted in your text for easy review."),
    ("✅", "Positive Word Identification", "Positive words are also detected and color-coded so you can see the balance of sentiment in your writing."),
    ("🔑", "Secure Authentication", "Sign-in required. Your analyses are session-scoped and private to your account."),
]

cols = st.columns(2)
for i, (icon, title, desc) in enumerate(services):
    with cols[i % 2]:
        st.markdown(f"""
        <div class="card">
          <div style="display:flex;align-items:flex-start;gap:1rem">
            <div style="font-size:2rem;min-width:2.5rem">{icon}</div>
            <div>
              <h4 style="margin:0 0 0.4rem;color:#4e54c8">{title}</h4>
              <p style="margin:0;color:#6b7280;font-size:0.92rem">{desc}</p>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro</div>', unsafe_allow_html=True)
