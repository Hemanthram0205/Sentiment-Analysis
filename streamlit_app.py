import streamlit as st
from textblob import TextBlob
# Note: fitz is the primary module name for PyMuPDF
import fitz  # PyMuPDF for PDF reading
from docx import Document
import io

# Set page configuration must be the first Streamlit command
st.set_page_config(page_title="Document Sentiment Analyzer", page_icon="🧠", layout="wide")

st.title("🧠 Document Sentiment Analysis App")
st.markdown("---")
st.info("Upload a **PDF** or **Word (.docx)** document to analyze its overall sentiment.")

# Function to read .docx files
def read_docx(file):
    """Extracts text from a .docx file."""
    try:
        doc = Document(file)
        # Join paragraphs, filtering out empty ones
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text
    except Exception as e:
        st.error(f"Error reading DOCX file: {e}")
        return ""

# Function to read .pdf files
def read_pdf(file):
    """Extracts text from a .pdf file using PyMuPDF (fitz)."""
    try:
        # Read the file object content into bytes
        pdf_bytes = file.read()
        # Open the document stream
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        # Extract text from all pages
        text = "\n".join([page.get_text("text") for page in doc if page.get_text("text").strip()])
        doc.close() # Close the document
        return text
    except Exception as e:
        st.error(f"Error reading PDF file. Ensure the PDF is not encrypted or corrupted: {e}")
        return ""

# Function for sentiment analysis
def get_sentiment(text):
    """Calculates sentiment polarity and categorizes it."""
    if not text:
        return 0, "N/A"
        
    sentiment_score = TextBlob(text).sentiment.polarity
    
    # Define thresholds for categorization
    if sentiment_score > 0.15:
        sentiment_category = "Positive 😊"
        color = "green"
    elif sentiment_score < -0.15:
        sentiment_category = "Negative 😔"
        color = "red"
    else:
        sentiment_category = "Neutral 😐"
        color = "blue"
        
    return sentiment_score, sentiment_category, color

# --- Main Application Logic ---

uploaded_file = st.file_uploader("📁 **Upload Document**", type=["pdf", "docx"], help="Files are processed in memory and not saved.")

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    text_data = ""

    # Ensure the file pointer is at the start for reading
    uploaded_file.seek(0)
    
    # Extract text based on file type
    if file_extension == "docx":
        text_data = read_docx(uploaded_file)
    elif file_extension == "pdf":
        # We must re-read the file bytes for PyMuPDF
        text_data = read_pdf(uploaded_file)
    else:
        st.error("Unsupported file format.")
        st.stop()

    if text_data:
        # Perform sentiment analysis
        with st.spinner("Analyzing document content..."):
            sentiment_score, sentiment_category, color = get_sentiment(text_data)

        st.markdown("## 📊 Analysis Results")
        
        # Display results with styling
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric(label="Overall Polarity Score", value=f"{sentiment_score:.4f}")
            st.markdown(f"**Overall Sentiment:** <span style='color:{color}; font-size: 1.2em; font-weight: bold;'>{sentiment_category}</span>", unsafe_allow_html=True)
            
        with col2:
            # Visualization: simple progress bar to represent polarity
            if sentiment_score >= 0:
                 st.progress(sentiment_score, text="Positive Range")
            else:
                 st.progress(1.0 + sentiment_score, text="Negative Range")
            st.caption("Score range: -1.0 (Most Negative) to 1.0 (Most Positive)")


        # Optional: Show a small preview of the document
        st.markdown("---")
        st.subheader("📝 Document Preview")
        
        preview_text = text_data[:1000] + ("..." if len(text_data) > 1000 else "")
        st.text_area("Extracted Text Sample:", preview_text, height=250)
        st.caption(f"Total characters extracted: {len(text_data):,}")
    else:
        # Handles case where read_docx or read_pdf returned an empty string due to error
        st.warning("Could not extract any meaningful text from the document.")
