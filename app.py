import streamlit as st
from textblob import TextBlob
from docx import Document
import pdfplumber
import io

st.set_page_config(page_title="Document Sentiment Analyzer", page_icon="🧠")

st.title("🧠 Document Sentiment Analysis App")
st.write("Upload a **PDF** or **Word (.docx)** document to analyze its overall sentiment using NLP techniques.")

# Function to read .docx files
def read_docx(file_bytes):
    file_bytes.seek(0)
    doc = Document(file_bytes)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text

# Function to read .pdf files
def read_pdf(file_bytes):
    file_bytes.seek(0)
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes.read())) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text

# Function for sentiment analysis
def get_sentiment(text):
    sentiment_score = TextBlob(text).sentiment.polarity
    if sentiment_score > 0.2:
        sentiment_category = "Positive 😊"
    elif sentiment_score < -0.2:
        sentiment_category = "Negative 😔"
    else:
        sentiment_category = "Neutral 😐"
    return sentiment_score, sentiment_category

# File uploader
uploaded_file = st.file_uploader("📁 Choose a PDF or Word file", type=["pdf", "docx"])

if uploaded_file is not None:
    # Read file and extract text
    st.info(f"📄 File selected: {uploaded_file.name}")
    
    if uploaded_file.name.endswith(".docx"):
        text_data = read_docx(uploaded_file)
    elif uploaded_file.name.endswith(".pdf"):
        text_data = read_pdf(uploaded_file)
    else:
        st.error("Unsupported file format.")
        st.stop()

    if not text_data.strip():
        st.warning("⚠️ No readable text found in the document.")
    else:
        with st.spinner("🔍 Analyzing sentiment..."):
            sentiment_score, sentiment_category = get_sentiment(text_data)

        st.success("✅ Analysis complete!")
        st.subheader("📊 Sentiment Analysis Results")
        st.write(f"**Sentiment Score:** `{sentiment_score:.4f}`")
        st.write(f"**Overall Sentiment:** {sentiment_category}")

        st.subheader("📝 Document Preview")
        st.text_area("Extracted Text (First 1000 characters):", text_data[:1000])
