import streamlit as st
from auth import require_auth, show_nav

st.set_page_config(page_title="Support — Sentiment Pro", page_icon="💬", layout="wide")
require_auth()
show_nav("Support")

st.markdown("""
<div class="page-hero">
  <h1>💬 Support</h1>
  <p>Get help with any issue or question</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### ❓ Frequently Asked Questions")

    faqs = [
        ("What file formats are supported?", "We support **PDF** (.pdf) and **Word** (.docx) files. Legacy .doc files are not supported — please convert them to .docx first."),
        ("Why is my sentiment score 0?", "Your text may not contain any AFINN-scored words. Try using more expressive language or a longer document. The score is 0 when positive and negative words cancel each other out."),
        ("What does the log-normalized score mean?", "The raw AFINN score is log-normalized (log₁₀(1 + |score|)) to prevent very long texts from producing extreme values. Scores above 0.3 = Positive, below −0.3 = Negative."),
        ("Why are some words not highlighted?", "Only words in the AFINN-165 lexicon (3,382 common English words) are scored. Proper nouns, technical terms, and uncommon words are not included."),
        ("Is my uploaded document stored?", "No. All processing happens in-session in your browser. No documents are saved to any server."),
        ("How do I reset my password?", "Contact support at the email below and we'll reset your credentials."),
    ]

    for q, a in faqs:
        with st.expander(q):
            st.markdown(a)

with col2:
    st.markdown("### 📬 Contact Us")
    st.markdown("""
    <div class="card">
      <p>📧 <b>Email</b><br>
         <a href="mailto:support@sentimentpro.com" style="color:#4e54c8">support@sentimentpro.com</a>
      </p>
      <hr style="border-color:#f0f0f5">
      <p>⏱️ <b>Response time</b><br>Within 24 hours</p>
      <hr style="border-color:#f0f0f5">
      <p>🌐 <b>Documentation</b><br>
         Available in the Help section
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📩 Send a Message")
    with st.form("support_form"):
        name    = st.text_input("Your Name")
        email   = st.text_input("Your Email")
        subject = st.selectbox("Subject", ["General Question", "Bug Report", "Feature Request", "Account Issue"])
        message = st.text_area("Message", height=120)
        if st.form_submit_button("Send Message", type="primary", use_container_width=True):
            if name and email and message:
                st.success("✅ Message sent! We'll reply within 24 hours.")
            else:
                st.error("Please fill in all fields.")

st.markdown('<div class="footer">© 2026 Sentiment Analyzer Pro</div>', unsafe_allow_html=True)
