import streamlit as st
from textblob import TextBlob
import pdfplumber   # instead of fitz / PyMuPDF
from docx import Document
import io

# --- Page Config ---
st.set_page_config(page_title="Document Sentiment Analyzer", page_icon="📊")

# --- Sidebar Navigation ---
st.sidebar.title("📚 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "🧠 Analyze Document", "ℹ️ About Us", "✉️ Connect With Me"])

# --- Function Definitions (original code, unchanged) ---
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
if page == "🏠 Home":
    st.title("📘 Document Sentiment Analyzer")
    st.subheader("Understand the tone of your documents instantly!")
    st.write("""
    Welcome to the **Document Sentiment Analyzer App** —  
    a simple tool that uses **Natural Language Processing (NLP)**  
    to detect the emotional tone of your documents.

    You can upload a **PDF or Word (.docx)** file and get a quick  
    classification of the overall sentiment:  
    **Positive**, **Negative**, or **Neutral**.
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/4781/4781517.png", width=250)
    st.markdown("---")
    st.markdown("👈 Use the sidebar to start analyzing your documents!")

# --- PAGE 2: ANALYZE DOCUMENT (Your Original Code) ---
elif page == "🧠 Analyze Document":
    st.title("Document Sentiment Analysis App")
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
elif page == "ℹ️ About Us":
    st.title("ℹ️ About This App")
    st.write("""
    This app was created by **Hemanth Ram S**,  
    a Business Analytics student at **PES University, Bengaluru**.

    It combines:
    - 🧠 **TextBlob** for Sentiment Analysis  
    - 📄 **pdfplumber** & **python-docx** for text extraction  
    - 🎨 **Streamlit** for an interactive user experience  

    The goal of this project is to make sentiment analysis accessible  
    for any text-based document — from reports to essays.
    """)

# --- PAGE 4: CONNECT / CONTACT ---
elif page == "✉️ Connect With Me":
    st.title("✉️ Let's Connect!")
    st.write("""
    Feel free to reach out for collaborations, discussions, or feedback!
    """)
    st.markdown("""
    - 📧 **Email:** [hemanthramhrs@gmail.com](mailto:hemanthramhrs@gmail.com)  
    - 💼 **LinkedIn:** [linkedin.com/in/hemanth-ram-9a6a53247](https://www.linkedin.com/in/hemanth-ram-9a6a53247/)  
    - 🐙 **GitHub:** [github.com/Hemanthram0205](https://github.com/Hemanthram0205)
    """)
    st.markdown("---")
    st.caption("💡 Built with Streamlit | Version 2.0")
