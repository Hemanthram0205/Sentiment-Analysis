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
    .navbar {
        background-color: #2b2b2b;
        padding: 12px 20px;
        border-radius: 8px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 25px;
        margin-bottom: 25px;
    }
    .nav-title {
        color: #00BFFF;
        font-size: 20px;
        font-weight: bold;
        margin-right: 30px;
    }
    .nav-item {
        color: white;
        text-decoration: none;
        font-weight: 500;
        padding: 8px 16px;
        border-radius: 5px;
        transition: 0.3s;
    }
    .nav-item:hover {
        background-color: #575757;
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

# --- Custom Navbar with Buttons and Separators ---
st.markdown(
    f"""
    <div class="navbar">
        <div class="nav-title">📘 Document Sentiment Analyzer</div>
        <a class="nav-item" href="#" onclick="window.parent.postMessage('home', '*')">🏠 Home</a>
        <span class="separator">|</span>
        <a class="nav-item" href="#" onclick="window.parent.postMessage('analyze', '*')">🧠 Analyze</a>
        <span class="separator">|</span>
        <a class="nav-item" href="#" onclick="window.parent.postMessage('about', '*')">ℹ️ About Us</a>
        <span class="separator">|</span>
        <a class="nav-item" href="#" onclick="window.parent.postMessage('contact', '*')">✉️ Contact</a>
    </div>
    """,
    unsafe_allow_html=True
)

# --- JavaScript listener for click navigation ---
st.markdown("""
    <script>
    const streamlitDoc = window.parent.document;
    window.addEventListener("message", (event) => {
        if (["home", "analyze", "about", "contact"].includes(event.data)) {
            window.parent.postMessage({ type: "streamlit:setComponentValue", value: event.data }, "*");
            window.parent.dispatchEvent(new Event("custom_nav_change_" + event.data));
        }
    });
    </script>
""", unsafe_allow_html=True)

# --- Button-based Navigation (still in Python) ---
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

# --- Function Definitions (unchanged) ---
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

# --- Page Logic (unchanged) ---
if st.session_state.page == "home":
    st.title("Welcome to the Document Sentiment Analyzer 👋")
    st.subheader("Understand the tone of your documents instantly!")
    st.write("""
    Upload your **PDF** or **Word (.docx)** documents to analyze their sentiment using  
    **Natural Language Processing (NLP)** powered by *TextBlob*.
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/4781/4781517.png", width=250)
    st.info("Use the top menu to start analyzing your document or learn more about this app.")

elif st.session_state.page == "analyze":
    st.title("🧠 Analyze Your Document")
    uploaded_file = st.file_uploader("📁 Choose a PDF or Word file", type=["pdf", "docx"])
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

elif st.session_state.page == "about":
    st.title("ℹ️ About This App")
    st.write("""
    This app was created by **Hemanth Ram S**,  
    a Business Analytics student at **PES University, Bengaluru**.

    It uses:
    - 🧠 **TextBlob** for sentiment analysis  
    - 📄 **pdfplumber** & **python-docx** for text extraction  
    - 🎨 **Streamlit** for the interface  
    """)

elif st.session_state.page == "contact":
    st.title("✉️ Connect With Me")
    st.markdown("""
    - 📧 **Email:** [hemanthramhrs@gmail.com](mailto:hemanthramhrs@gmail.com)  
    - 💼 **LinkedIn:** [linkedin.com/in/hemanth-ram-9a6a53247](https://www.linkedin.com/in/hemanth-ram-9a6a53247/)  
    - 🐙 **GitHub:** [github.com/Hemanthram0205](https://github.com/Hemanthram0205)
    """)
    st.caption("💡 Built with Streamlit | Version 2.0 | Designed by Hemanth Ram S")
