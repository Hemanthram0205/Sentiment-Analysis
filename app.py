import streamlit as st
from textblob import TextBlob
import pdfplumber
from docx import Document
import io

# --- Page Config ---
st.set_page_config(page_title="Document Sentiment Analyzer", page_icon="📊", layout="wide")

# --- CSS for Top Navigation ---
st.markdown("""
    <style>
    .nav {
        background-color: #2b2b2b;
        overflow: hidden;
        padding: 15px 10px;
        border-radius: 8px;
        margin-bottom: 30px;
    }
    .nav button {
        background-color: transparent;
        color: white;
        border: none;
        outline: none;
        padding: 12px 20px;
        font-size: 16px;
        font-weight: 500;
        cursor: pointer;
    }
    .nav button:hover {
        background-color: #575757;
        border-radius: 5px;
    }
    .nav-title {
        float: left;
        font-size: 20px;
        color: #00BFFF;
        font-weight: bold;
        padding: 10px 20px;
    }
    .nav-right {
        float: right;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session State for Navigation ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- Navigation Bar Buttons ---
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([3, 1, 1, 1, 1])
with nav_col1:
    st.markdown('<div class="nav-title">📘 Document Sentiment Analyzer</div>', unsafe_allow_html=True)
with nav_col2:
    if st.button("🏠 Home"):
        st.session_state.page = "home"
with nav_col3:
    if st.button("🧠 Analyze"):
        st.session_state.page = "analyze"
with nav_col4:
    if st.button("ℹ️ About Us"):
        st.session_state.page = "about"
with nav_col5:
    if st.button("✉️ Contact"):
        st.session_state.page = "contact"

st.markdown("<br>", unsafe_allow_html=True)

# --- Original Function Definitions (Unchanged) ---
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
    Upload your **PDF** or **Word (.docx)** documents to analyze their sentiment using  
    **Natural Language Processing (NLP)** powered by *TextBlob*.
    
    Get an instant breakdown of whether the content is **Positive**, **Negative**, or **Neutral**.
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/4781/4781517.png", width=250)
    st.markdown("---")
    st.info("Use the top menu to start analyzing your document or learn more about this app.")

# --- PAGE 2: ANALYZE DOCUMENT (Your Original Code, Unchanged) ---
elif st.session_state.page == "analyze":
    st.title("🧠 Analyze Your Document")
    st.write("Upload a **PDF** or **Word (.docx)** document to analyze its overall sentiment.")

    uploaded_file = st.file_uploader("📁 Choose a PDF or Word file", type=["pdf", "docx"])

    if uploaded_file is not None:
        # Extract text
        if uploaded_file.name.endswith(".docx"):
            text_data = read_docx(uploaded_file)
        elif uploaded_file.name.endswith(".pdf"):
            text_data = read_pdf(uploaded_file)
        else:
            st.error("Unsupported file format.")
            st.stop()

        # Perform sentiment analysis
        with st.spinner("Analyzing sentiment..."):
            sentiment_score, sentiment_category = get_sentiment(text_data)

        # Display results
        st.subheader("📊 Sentiment Analysis Results")
        st.write(f"**Sentiment Score:** {sentiment_score:.4f}")
        st.write(f"**Overall Sentiment:** {sentiment_category}")

        # Optional: Show a small preview of the document
        st.subheader("📝 Document Preview")
        st.text_area("Extracted Text (First 1000 characters):", text_data[:1000])

# --- PAGE 3: ABOUT US ---
elif st.session_state.page == "about":
    st.title("ℹ️ About This App")
    st.write("""
    This app was created by **Hemanth Ram S**,  
    a Business Analytics student at **PES University, Bengaluru**.

    It uses:
    - 🧠 **TextBlob** for sentiment analysis  
    - 📄 **pdfplumber** & **python-docx** for text extraction  
    - 🎨 **Streamlit** for a simple, interactive interface  

    The purpose of this app is to help users instantly detect the tone of any text-based document.
    """)

# --- PAGE 4: CONTACT ---
elif st.session_state.page == "contact":
    st.title("✉️ Connect With Me")
    st.write("""
    I'd love to hear your feedback or discuss collaboration opportunities!  
    Reach out through the following:
    """)
    st.markdown("""
    - 📧 **Email:** [hemanthramhrs@gmail.com](mailto:hemanthramhrs@gmail.com)  
    - 💼 **LinkedIn:** [linkedin.com/in/hemanth-ram-9a6a53247](https://www.linkedin.com/in/hemanth-ram-9a6a53247/)  
    - 🐙 **GitHub:** [github.com/Hemanthram0205](https://github.com/Hemanthram0205)
    """)
    st.markdown("---")
    st.caption("💡 Built with Streamlit | Version 2.0 | Designed by Hemanth Ram S")
