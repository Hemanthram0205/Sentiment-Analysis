import streamlit as st
from textblob import TextBlob
import pdfplumber
from docx import Document

st.set_page_config(page_title="Document Sentiment Analyzer", page_icon="📘", layout="wide")

# --- Professional Light Navbar ---
st.markdown("""
    <style>
    .navbar {
        background-color: #f9f9f9;
        padding: 14px 40px;
        border-bottom: 2px solid #e0e0e0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 6px;
        margin-bottom: 25px;
    }
    .nav-left {
        color: #003366;
        font-size: 20px;
        font-weight: 700;
        font-family: 'Segoe UI', sans-serif;
    }
    .nav-right {
        display: flex;
        gap: 25px;
        align-items: center;
    }
    .nav-item {
        color: #004080;
        text-decoration: none;
        font-weight: 500;
        font-size: 16px;
        font-family: 'Segoe UI', sans-serif;
        padding: 6px 14px;
        border-radius: 5px;
        transition: 0.3s ease;
    }
    .nav-item:hover {
        background-color: #e6f0ff;
        color: #002b80;
    }
    .active {
        background-color: #cce0ff;
        color: #002b80;
        font-weight: 600;
    }
    .separator {
        color: #999;
        font-weight: 400;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Navbar Layout ---
st.markdown(f"""
    <div class="navbar">
        <div class="nav-left">📘 Document Sentiment Analyzer</div>
        <div class="nav-right">
            <a class="nav-item {'active' if st.session_state.page=='home' else ''}" href="#" onclick="window.parent.postMessage('home', '*')">🏠 Home</a>
            <span class="separator">|</span>
            <a class="nav-item {'active' if st.session_state.page=='analyze' else ''}" href="#" onclick="window.parent.postMessage('analyze', '*')">🧠 Analyze</a>
            <span class="separator">|</span>
            <a class="nav-item {'active' if st.session_state.page=='about' else ''}" href="#" onclick="window.parent.postMessage('about', '*')">ℹ️ About Us</a>
            <span class="separator">|</span>
            <a class="nav-item {'active' if st.session_state.page=='contact' else ''}" href="#" onclick="window.parent.postMessage('contact', '*')">✉️ Contact</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Core Functions ---
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

# --- Page Switching Logic ---
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

# --- HOME PAGE ---
if st.session_state.page == "home":
    st.title("Welcome to the Document Sentiment Analyzer 👋")
    st.write("""
    This tool analyzes the **sentiment** of your uploaded documents — academic papers, reports, or reviews —  
    and classifies them as **Positive**, **Negative**, or **Neutral** using NLP techniques.
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/4781/4781517.png", width=200)
    st.info("Use the navigation bar above to start analyzing your document or learn more about this project.")

# --- ANALYZE PAGE ---
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

# --- ABOUT US PAGE ---
elif st.session_state.page == "about":
    st.title("ℹ️ About This Project")
    st.write("""
    Developed by **Hemanth Ram S**,  
    BBA (Hons) Business Analytics student at **PES University, Bengaluru**.

    **Tech Stack**
    - 🧠 TextBlob – Sentiment Analysis  
    - 📄 pdfplumber / python-docx – Text Extraction  
    - 🌐 Streamlit – Web App Framework
    """)

# --- CONTACT PAGE ---
elif st.session_state.page == "contact":
    st.title("✉️ Contact")
    st.write("""
    For collaborations or academic discussions:
    - 📧 **Email:** [hemanthramhrs@gmail.com](mailto:hemanthramhrs@gmail.com)
    - 💼 **LinkedIn:** [linkedin.com/in/hemanth-ram-9a6a53247](https://linkedin.com/in/hemanth-ram-9a6a53247)
    - 🐙 **GitHub:** [github.com/Hemanthram0205](https://github.com/Hemanthram0205)
    """)
    st.caption("Built with ❤️ using Streamlit | Designed by Hemanth Ram S")
