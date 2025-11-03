import streamlit as st
from textblob import TextBlob
import pdfplumber
from docx import Document
import io

# --- Page Config ---
st.set_page_config(page_title="Document Sentiment Analyzer", page_icon="📊", layout="wide")

# --- Elegant Professional Navbar Styling ---
st.markdown("""
    <style>
    body {
        background-color: #f8f9fa;
    }
    .navbar {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        padding: 14px 25px;
        border-radius: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        margin-bottom: 35px;
        box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.05);
    }
    .nav-title {
        color: #004080;
        font-size: 20px;
        font-weight: 700;
        margin-right: 30px;
        font-family: 'Segoe UI', sans-serif;
    }
    .nav-item {
        color: #004080;
        text-decoration: none;
        font-weight: 500;
        padding: 6px 16px;
        border-radius: 5px;
        transition: all 0.3s ease;
        font-family: 'Segoe UI', sans-serif;
    }
    .nav-item:hover {
        background-color: #e6f0ff;
        color: #003366;
    }
    .active {
        background-color: #004080;
        color: white !important;
    }
    .separator {
        color: #999;
        font-weight: bold;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session State for Navigation ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Navigation Bar ---
def navbar():
    st.markdown(f"""
        <div class="navbar">
            <div class="nav-title">📘 Document Sentiment Analyzer</div>
            <a class="nav-item {'active' if st.session_state.page=='home' else ''}" href="#" onclick="window.parent.postMessage('home', '*')">🏠 Home</a>
            <span class="separator">|</span>
            <a class="nav-item {'active' if st.session_state.page=='analyze' else ''}" href="#" onclick="window.parent.postMessage('analyze', '*')">🧠 Analyze</a>
            <span class="separator">|</span>
            <a class="nav-item {'active' if st.session_state.page=='about' else ''}" href="#" onclick="window.parent.postMessage('about', '*')">ℹ️ About Us</a>
            <span class="separator">|</span>
            <a class="nav-item {'active' if st.session_state.page=='contact' else ''}" href="#" onclick="window.parent.postMessage('contact', '*')">✉️ Contact</a>
        </div>
    """, unsafe_allow_html=True)

navbar()

# --- Buttons for Navigation (Preserves Streamlit State) ---
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

# --- Function Definitions (Your Original Code Unchanged) ---
def read_docx(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text

def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def get_sentiment(text):
    sentiment_score = TextBlob(text).sentiment.polarity
    if sentiment_score > 0.2:
        sentiment_category = "Positive 😊"
    elif sentiment_score < -0.2:
        sentiment_category = "Negative 😔"
    else:
        sentiment_category = "Neutral 😐"
    return sentiment_score, sentiment_category

# --- PAGE 1: HOME ---
if st.session_state.page == "home":
    st.title("Welcome to the Document Sentiment Analyzer 👋")
    st.subheader("Understand the tone of your documents instantly!")
    st.write("""
    This web application uses **Natural Language Processing (NLP)** to analyze  
    the emotional tone of any **PDF** or **Word (.docx)** document.  
    It identifies whether the overall sentiment is **Positive**, **Negative**, or **Neutral**.
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/4781/4781517.png", width=250)
    st.markdown("---")
    st.info("Use the navigation bar above to start analyzing your document or learn more about the app.")

# --- PAGE 2: ANALYZE DOCUMENT ---
elif st.session_state.page == "analyze":
    st.title("🧠 Analyze Your Document")
    uploaded_file = st.file_uploader("📁 Upload a PDF or Word file", type=["pdf", "docx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".docx"):
            text_data = read_docx(uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            text_data = read_pdf(uploaded_file)
        else:
            st.error("Unsupported file format.")
            st.stop()

        with st.spinner("Analyzing sentiment..."):
            sentiment_score, sentiment_category = get_sentiment(text_data)

        st.subheader("📊 Sentiment Analysis Results")
        st.write(f"**Sentiment Score:** {sentiment_score:.4f}")
        st.write(f"**Overall Sentiment:** {sentiment_category}")

        st.subheader("📝 Document Preview")
        st.text_area("Extracted Text (First 1000 characters):", text_data[:1000])

# --- PAGE 3: ABOUT ---
elif st.session_state.page == "about":
    st.title("ℹ️ About This App")
    st.write("""
    The **Document Sentiment Analyzer** was developed by **Hemanth Ram S**,  
    a Business Analytics student at **PES University, Bengaluru**.

    **Objective:**  
    To apply *Natural Language Processing (NLP)* and *Machine Learning* techniques  
    in real-world scenarios for sentiment classification.

    **Tech Stack Used:**
    - 🐍 Python  
    - 🧠 TextBlob (Sentiment Analysis)  
    - 📄 pdfplumber & python-docx (Text Extraction)  
    - 🎨 Streamlit (Web Deployment)
    """)

# --- PAGE 4: CONTACT ---
elif st.session_state.page == "contact":
    st.title("✉️ Connect With Me")
    st.write("""
    For collaborations or academic discussions, feel free to reach out:
    """)
    st.markdown("""
    - 📧 **Email:** [hemanthramhrs@gmail.com](mailto:hemanthramhrs@gmail.com)  
    - 💼 **LinkedIn:** [linkedin.com/in/hemanth-ram-9a6a53247](https://www.linkedin.com/in/hemanth-ram-9a6a53247/)  
    - 🐙 **GitHub:** [github.com/Hemanthram0205](https://github.com/Hemanthram0205)
    """)
    st.caption("💡 Built with Streamlit | Version 2.0 | Designed by Hemanth Ram S")
