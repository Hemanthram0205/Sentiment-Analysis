import streamlit as st
from auth import require_auth, show_nav

st.set_page_config(page_title="Connect — Sentiment Pro", page_icon="🔗", layout="wide")
require_auth()
show_nav("Connect")

st.markdown("""
<div class="page-hero">
  <h1>🔗 Connect</h1>
  <p>Stay connected with Sentiment Analyzer Pro</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card" style="text-align:center">
      <div style="font-size:2.5rem">🐙</div>
      <h3 style="color:#4e54c8">GitHub</h3>
      <p style="color:#6b7280;font-size:0.9rem">Star the project, report issues, or contribute!</p>
      <a href="https://github.com/Hemanthram0205/Sentiment-Analysis" target="_blank"
         style="display:inline-block;background:#4e54c8;color:white;padding:0.6rem 1.5rem;
                border-radius:8px;text-decoration:none;font-weight:600;margin-top:0.5rem">
        View on GitHub
      </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="text-align:center">
      <div style="font-size:2.5rem">📧</div>
      <h3 style="color:#4e54c8">Email</h3>
      <p style="color:#6b7280;font-size:0.9rem">Reach out directly for partnerships or custom solutions.</p>
      <a href="mailto:support@sentimentpro.com"
         style="display:inline-block;background:#4e54c8;color:white;padding:0.6rem 1.5rem;
                border-radius:8px;text-decoration:none;font-weight:600;margin-top:0.5rem">
        Send Email
      </a>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📰 Stay Updated")
    with st.form("newsletter_form"):
        nl_name  = st.text_input("Name")
        nl_email = st.text_input("Email address")
        if st.form_submit_button("Subscribe", type="primary", use_container_width=True):
            if nl_email:
                st.success(f"✅ {nl_name or 'You'} are now subscribed!")
            else:
                st.error("Please enter your email.")

    st.markdown("""
    <div class="card" style="margin-top:1rem">
      <h4 style="color:#4e54c8">🌟 What You'll Get</h4>
      <ul style="color:#6b7280;font-size:0.9rem">
        <li>Product updates and new features</li>
        <li>NLP research highlights</li>
        <li>Tips for better sentiment analysis</li>
        <li>Early access to new tools</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro</div>', unsafe_allow_html=True)
