import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from textblob import TextBlob

# --- Helper Functions ---
def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def read_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join([page.get_text("text") for page in doc if page.get_text("text").strip()])

def get_sentiment(text):
    sentiment_score = TextBlob(text).sentiment.polarity
    if sentiment_score > 0.2:
        return sentiment_score, "Positive 😊"
    elif sentiment_score < -0.2:
        return sentiment_score, "Negative 😔"
    else:
        return sentiment_score, "Neutral 😐"

# --- Sidebar Navigation ---
st.sidebar.title("📚 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "🧠 Analyze Document", "ℹ️ About Us", "✉️ Connect With Us"])

# --- PAGE 1: Home ---
if page == "🏠 Home":
    st.title("📘 Document Sentiment Analyzer")
    st.subheader("Understand the tone of your documents instantly!")
    st.write("""
    Upload your **PDF or Word document** and let the app analyze its overall sentiment.  
    Whether it's a report, article, or feedback form — you’ll know if the tone is **positive, neutral, or negative**.
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/4781/4781517.png", width=250)
    st.markdown("---")
    st.markdown("👈 Use the sidebar to start analyzing your documents!")

# --- PAGE 2: Analyze Document ---
elif page == "🧠 Analyze Document":
    st.title("🧠 Sentiment Analysis Tool")
    uploaded_file = st.file_uploader("Upload a PDF or Word Document", type=["pdf", "docx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            text_data = read_pdf("temp.pdf")
        elif uploaded_file.name.endswith(".docx"):
            with open("temp.docx", "wb") as f:
                f.write(uploaded_file.getbuffer())
            text_data = read_docx("temp.docx")
        else:
            st.error("Unsupported file format.")
            st.stop()

        st.subheader("📄 Extracted Text Preview:")
        st.text_area("Document Content", text_data[:2000], height=200)

        sentiment_score, sentiment_category = get_sentiment(text_data)
        st.markdown("---")
        st.subheader("🎯 Sentiment Analysis Result:")
        st.metric("Sentiment Score", f"{sentiment_score:.3f}")
        st.success(f"Overall Sentiment: **{sentiment_category}**")

# --- PAGE 3: About Us ---
elif page == "ℹ️ About Us":
    st.title("ℹ️ About Us")
    st.write("""
    This web app was created by **Hemanth Ram S**, a Business Analytics student at PES University.  
    It uses **Natural Language Processing (NLP)** and **TextBlob** to identify the emotional tone of written documents.
    """)
    st.markdown("""
    **Technologies Used:**
    - 🐍 Python  
    - 🧠 TextBlob for Sentiment Analysis  
    - 📄 PyMuPDF & python-docx for document extraction  
    - 🎨 Streamlit for Web Deployment
    """)

# --- PAGE 4: Contact / Connect ---
elif page == "✉️ Connect With Us":
    st.title("✉️ Connect With Me")
    st.write("""
    I'm always open to collaborations or feedback!  
    Reach out via:
    - 📧 **Email:** hemanthramhrs@gmail.com  
    - 💼 [LinkedIn](https://www.linkedin.com/in/hemanth-ram-9a6a53247/)  
    - 🐙 [GitHub](https://github.com/Hemanthram0205)
    """)
    st.markdown("---")
    st.write("💡 *Built with Streamlit | Version 2.0*")
