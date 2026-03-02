import streamlit as st
from auth import require_auth, show_nav

st.set_page_config(page_title="Help — Sentiment Pro", page_icon="❓", layout="wide")
require_auth()
show_nav("Help")

st.markdown("""
<div class="page-hero">
  <h1>❓ Help Center</h1>
  <p>Step-by-step guides to get the most out of Sentiment Analyzer Pro</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### 🚀 Quick Start Guide")

    steps = [
        ("1️⃣", "Sign In", "Log in with your credentials from the Sign In page. Use demo/demo123 to try the app."),
        ("2️⃣", "Choose Input Method", "Click **Analyzer** in the sidebar. Choose between uploading a file (PDF/DOCX) or pasting text directly."),
        ("3️⃣", "Upload or Paste", "Drag & drop your file into the upload area, or paste your text into the text box."),
        ("4️⃣", "Run Analysis", "Click the **Analyze** button. Results appear in under a second for most inputs."),
        ("5️⃣", "Read Your Results", "Review the Sentiment Score cards, positive/negative word lists, and the Emotion Breakdown section."),
        ("6️⃣", "Explore Emotions", "The radar chart and progress bars show your 8-emotion distribution. Expand 'Words by Emotion' to see which words triggered each emotion."),
        ("7️⃣", "View Highlighted Text", "Expand 'View Highlighted Text' to see your document with positive words in green and negative words in red."),
    ]

    for icon, title, desc in steps:
        st.markdown(f"""
        <div class="card" style="display:flex;align-items:flex-start;gap:1rem">
          <div style="font-size:1.8rem;min-width:2.5rem">{icon}</div>
          <div>
            <h4 style="margin:0 0 0.3rem;color:#4e54c8">{title}</h4>
            <p style="margin:0;color:#6b7280;font-size:0.9rem">{desc}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📖 Understanding Your Score")
    st.markdown("""
    <div class="card">
      <h4 style="color:#2ed573">😀 Positive</h4>
      <p style="font-size:0.88rem;color:#6b7280">Score <b>&gt; 0.3</b> — Text contains more positive sentiment than negative. Common in praise, satisfaction, and optimistic writing.</p>
    </div>
    <div class="card">
      <h4 style="color:#9ca3af">😐 Neutral</h4>
      <p style="font-size:0.88rem;color:#6b7280">Score between <b>−0.3 and +0.3</b> — Balanced or emotionally flat text. Common in formal writing, instructions, and factual reports.</p>
    </div>
    <div class="card">
      <h4 style="color:#ff4757">😡 Negative</h4>
      <p style="font-size:0.88rem;color:#6b7280">Score <b>&lt; −0.3</b> — More negative words detected. Common in complaints, criticism, or distressed writing.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🧠 The 8 Emotions")
    emotions = [("😊","Joy","Happiness, delight, pleasure"),("😢","Sadness","Grief, unhappiness, loss"),("😡","Anger","Rage, frustration, hostility"),("😨","Fear","Terror, anxiety, dread"),("🤢","Disgust","Revulsion, distaste"),("😮","Surprise","Shock, astonishment"),("🤝","Trust","Confidence, reliability"),("⏳","Anticipation","Expectation, excitement")]
    for emoji, name, desc in emotions:
        st.markdown(f'<div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem"><span style="font-size:1.3rem">{emoji}</span><div><b style="font-size:0.88rem">{name}</b><div style="font-size:0.78rem;color:#9ca3af">{desc}</div></div></div>', unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro</div>', unsafe_allow_html=True)
