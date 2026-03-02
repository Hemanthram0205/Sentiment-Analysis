import streamlit as st
from auth import require_auth, show_nav

st.set_page_config(page_title="About — Sentiment Pro", page_icon="ℹ️", layout="wide")
require_auth()
show_nav("About")

st.markdown("""
<div class="page-hero">
  <h1>ℹ️ About Us</h1>
  <p>The story behind Sentiment Analyzer Pro</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
    <div class="card">
      <h3 style="color:#4e54c8">🎯 Our Mission</h3>
      <p>Sentiment Analyzer Pro empowers individuals, researchers, and businesses to instantly understand the emotional tone of any text — from customer reviews to academic documents.</p>
    </div>
    <div class="card">
      <h3 style="color:#4e54c8">🔬 How It Works</h3>
      <p>We use two proven NLP methods:</p>
      <ul>
        <li><b>AFINN-165 Lexicon</b> — 3,382 words rated from −5 (most negative) to +5 (most positive), with log normalization for balanced scoring.</li>
        <li><b>NRC Emotion Lexicon</b> — maps words to 8 basic emotions developed by the National Research Council of Canada.</li>
      </ul>
    </div>
    <div class="card">
      <h3 style="color:#4e54c8">📂 Supported Formats</h3>
      <p>Upload <b>PDF</b> or <b>Word (.docx)</b> documents, or simply paste text directly into the analyzer. All processing happens in real-time.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card" style="text-align:center">
      <div style="font-size:3rem">📊</div>
      <h3 style="color:#4e54c8">Sentiment Analyzer Pro</h3>
      <p style="color:#6b7280;font-size:0.9rem">Version 2.0</p>
      <hr style="border-color:#f0f0f5">
      <p style="font-size:0.85rem">Built with Python, Streamlit, AFINN-165, NRC Lexicon, and Plotly.</p>
    </div>
    <div class="card" style="text-align:center">
      <h4 style="color:#4e54c8">🏆 Key Stats</h4>
      <p><b>3,382</b> AFINN words</p>
      <p><b>8</b> Emotion categories</p>
      <p><b>300+</b> Emotion-mapped words</p>
      <p><b>PDF & DOCX</b> support</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro</div>', unsafe_allow_html=True)
