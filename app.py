import streamlit as st
from textblob import TextBlob
import pdfplumber
from docx import Document

# --- Page Config ---
st.set_page_config(page_title="Document Sentiment Analyzer", page_icon="📘", layout="wide")

# --- Light & Professional Navigation Styling ---
st.markdown("""
    <style>
    .navbar {
        background-color: #f5f5f5;
        padding: 14px 25px;
        border-radius: 8px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 25px;
        margin-bottom: 25px;
        border: 1px solid #ddd;
    }
    .nav-title {
        color: #004080;
        font-size: 20px;
        font-weight: 700;
        margin-right: 40px;
        font-family: 'Segoe UI', sans-serif;
    }
    .nav-item {
        color: #004080;
        text-decoration: none;
        font-weight: 500;
        font-size: 16px;
        font-family: 'Segoe UI', sans-serif;
        padding: 8px 16px;
        border-radius: 6px;
        transition: 0.3s ease;
    }
    .nav-item:hover {
        background-color: #e6f0ff;
        color: #003366;
    }
    .active {
        background-color: #cce0ff;
        color: #002b80;
        font-weight: 600;
    }
    .separator {
        color: #888;
        font-weight: 400;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Page in Session ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Navigation Bar ---
def nav_button(label, key, icon=""):
    active_class = "active" if st.session_state.page == key else ""
    button_html = f"<a class='nav-item {active_class}' href='#' onclick=\"window.parent.postMessage('{key}', '*')\">{icon} {label}</a>"
    return button_html

st.markdown(f"""
    <div class="navbar">
        <div class="nav-title">📘 Document Sentiment Analyzer</div>
        {nav_button('Home', 'home', '🏠')}
        <span class="separator">|</span>
        {nav_button('Analyze', 'analyze', '🧠')}
        <span class="separator">|</span>
        {nav_button('About Us', 'about', 'ℹ️')}
        <span class="separator">|</span>
        {nav_button('Contact', 'contact', '✉️')}
    </div>
""", unsafe_allow_html=True)

# --- Button-Based Navigation ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🏠 Home"):
        st.session_state.page = "home"
with col2:
    if st.button("🧠 Analyze"):
        st.session_state.page = "analyze"
with col3:
    if st.button("ℹ️ About Us"):
        st.session_state.page = "about"
with col4:
    if st.button("✉️ Contact"):
        st.session_state.page = "contact"

st.markdown("<br>", unsafe_allow_html=True)

# --- Core Functions (Original Code) ---
def read_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def get_sentiment(text):
    score = TextBlob(text).sentiment.polarity
    if score > 0.2:
        category = "Positive 😊"
    elif score < -0.2:
        category = "Negative 😔"
    else:
        category = "Neutral 😐"
    return score, category

# --- PAGE: HOME ---
if st.session_state.page == "home":
    st.title("Welcome to the Document Sentiment Analyzer 👋")
    st.subheader("Understand the tone of your documents instantly")
    st.write("""
    This web app helps you analyze the **sentiment** of any document — academic papers, reports, reviews, or essays —  
    by detecting whether the tone is **positive**, **negative**, or **neutral** using **Natural Language Processing (NLP)** techniques.
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/4781/4781517.png", width=220)
    st.info("Use the top menu to start analyzing your document or learn more about this project.")

# --- PAGE: ANALYZE ---
elif st.session_state.page == "analyze":
    st.title("🧠 Document Sentiment Analysis")
    st.write("Upload a **PDF** or **Word (.docx)** document to analyze its overall sentiment.")
    
    uploaded_file = st.file_uploader("📁 Choose a file", type=["pdf", "docx"])
    if uploaded_file:
        text_data = read_docx(uploaded_file) if uploaded_file.name.endswith(".docx") else read_pdf(uploaded_file)
        with st.spinner("Analyzing sentiment..."):
            sentiment_score, sentiment_category = get_sentiment(text_data)
        st.subheader("📊 Sentiment Analysis Results")
        st.write(f"**Sentiment Score:** {sentiment_score:.4f}")
        st.write(f"**Overall Sentiment:** {sentiment_category}")
        st.subheader("📝 Document Preview")
        st.text_area("Extracted Text (First 1000 characters):", text_data[:1000])

# --- PAGE: ABOUT US ---
elif st.session_state.page == "about":
    st.title("ℹ️ About This Project")
    st.write("""
    This project was developed by **Hemanth Ram. S**,  
    a BBA (Hons) Business Analytics student at **PES University, Bengaluru**.
    
    **Technologies Used**
    - 🧠 *TextBlob* – Sentiment Analysis  
    - 📄 *pdfplumber* & *python-docx* – Text Extraction  
    - 🎨 *Streamlit* – Web App Interface  
    
    The goal is to make sentiment analysis tools accessible for educational and analytical purposes.
    """)

# --- PAGE: CONTACT ---
elif st.session_state.page == "contact":
    st.title("✉️ Contact")
    st.write("""
    For collaborations or academic discussions, feel free to reach out:
    """)
    st.markdown("""
    - 📧 **Email:** [hemanthramhrs@gmail.com](mailto:hemanthramhrs@gmail.com)  
    - 💼 **LinkedIn:** [linkedin.com/in/hemanth-ram-9a6a53247](https://www.linkedin.com/in/hemanth-ram-9a6a53247/)  
    - 🐙 **GitHub:** [github.com/Hemanthram0205](https://github.com/Hemanthram0205)
    """)
    st.caption("💡 Built with Streamlit | Version 2.0 | Designed by Hemanth Ram. S")
