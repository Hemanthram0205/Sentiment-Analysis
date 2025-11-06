import streamlit as st
from textblob import TextBlob
import pdfplumber
from docx import Document
import re

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Document Sentiment Analyzer",
    page_icon="📘",
    layout="wide"
)

# =========================
# CUSTOM STYLING
# =========================
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {padding-top: 0rem !important; margin-top: -2rem !important;}
    body {background-color: #f8f9fa;}
    .navbar {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 12px 25px;
        border-radius: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 40px;
        margin-bottom: 30px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    }
    .nav-title {
        color: #003366;
        font-size: 20px;
        font-weight: 700;
        font-family: 'Segoe UI', sans-serif;
        margin-right: 30px;
    }
    .nav-button {
        background-color: white;
        color: #004080;
        border: 1px solid #004080;
        padding: 6px 18px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .nav-button:hover {
        background-color: #004080;
        color: white;
    }
    .highlight-positive {background-color: #d4edda;}
    .highlight-negative {background-color: #f8d7da;}
    .highlight-neutral {background-color: #fdfd96;}
    </style>
""", unsafe_allow_html=True)

# =========================
# SESSION MANAGEMENT
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"

# =========================
# NAVIGATION BAR
# =========================
def navbar():
    st.markdown("<div class='navbar'>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    with col1:
        st.markdown("<div class='nav-title'>📘 Document Sentiment Analyzer</div>", unsafe_allow_html=True)
    with col2:
        if st.button("🏠 Home"): st.session_state.page = "home"
    with col3:
        if st.button("🧠 Analyze"): st.session_state.page = "analyze"
    with col4:
        if st.button("ℹ️ About"): st.session_state.page = "about"
    with col5:
        if st.button("✉️ Contact"): st.session_state.page = "contact"
    st.markdown("</div>", unsafe_allow_html=True)

navbar()

# =========================
# HELPER FUNCTIONS
# =========================
def read_docx(file):
    """Extract text safely from .docx file"""
    try:
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception:
        return ""

def read_pdf(file):
    """Extract text safely from PDF file"""
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except Exception:
        pass
    return text

def get_sentiment(text):
    """Compute sentiment score and classify"""
    sentiment = TextBlob(text).sentiment.polarity
    if sentiment > 0.2:
        category = "Positive 😊"
    elif sentiment < -0.2:
        category = "Negative 😔"
    else:
        category = "Neutral 😐"
    return sentiment, category

def highlight_text(text):
    """Highlight positive/negative words in text preview"""
    words = text.split()
    highlighted = []
    for word in words:
        polarity = TextBlob(word).sentiment.polarity
        if polarity > 0.3:
            highlighted.append(f"<span class='highlight-positive'>{word}</span>")
        elif polarity < -0.3:
            highlighted.append(f"<span class='highlight-negative'>{word}</span>")
        else:
            highlighted.append(word)
    return " ".join(highlighted)

# =========================
# PAGE ROUTES
# =========================
page = st.session_state.page

if page == "home":
    st.title("Welcome to the Document Sentiment Analyzer 👋")
    st.subheader("Analyze your documents for emotional tone instantly.")
    st.write("""
    This app uses **Natural Language Processing (NLP)** to determine whether your  
    PDF or Word document expresses a **Positive**, **Negative**, or **Neutral** sentiment.
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/4781/4781517.png", width=250)
    st.markdown("---")
    st.info("Use the navigation bar above to begin your analysis or learn more.")

elif page == "analyze":
    st.title("🧠 Document Sentiment Analysis")
    uploaded_file = st.file_uploader("📁 Upload a PDF or Word file", type=["pdf", "docx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".docx"):
            text = read_docx(uploaded_file)
        else:
            text = read_pdf(uploaded_file)

        if not text.strip():
            st.error("No readable text found in this file. Please upload a text-based PDF or Word document.")
        else:
            with st.spinner("Analyzing sentiment..."):
                score, category = get_sentiment(text)

            st.success("✅ Analysis Complete!")

            st.subheader("📊 Sentiment Results")
            st.metric("Sentiment Score", f"{score:.4f}", delta=None)
            st.write(f"**Overall Sentiment:** {category}")

            # Sentiment visualization
            st.progress((score + 1) / 2)
            st.caption("← Negative | Neutral | Positive →")

            st.subheader("📝 Document Preview (Highlighted)")
            highlighted_text = highlight_text(text[:1000])
            st.markdown(highlighted_text, unsafe_allow_html=True)

elif page == "about":
    st.title("ℹ️ About This App")
    st.write("""
    The **Document Sentiment Analyzer** was built by **Hemanth Ram. S**,  
    a Business Analytics student at **PES University, Bengaluru**.
    
    ### 🎯 Objective  
    Apply *Natural Language Processing (NLP)* to real-world text data  
    for sentiment classification and tone detection.
    
    ### ⚙️ Tech Stack
    - 🐍 Python  
    - 🧠 TextBlob for sentiment analysis  
    - 📄 pdfplumber & python-docx for text extraction  
    - 🎨 Streamlit for UI and deployment
    """)

elif page == "contact":
    st.title("✉️ Contact & Connect")
    st.write("Reach out for collaborations, research, or academic discussions:")
    st.markdown("""
    - 📧 **Email:** [hemanthramhrs@gmail.com](mailto:hemanthramhrs@gmail.com)  
    - 💼 **LinkedIn:** [linkedin.com/in/hemanth-ram-9a6a53247](https://www.linkedin.com/in/hemanth-ram-9a6a53247/)  
    - 🐙 **GitHub:** [github.com/Hemanthram0205](https://github.com/Hemanthram0205)
    """)
    st.caption("© 2025 Hemanth Ram. S | PES University | Built with ❤️ in Streamlit")
