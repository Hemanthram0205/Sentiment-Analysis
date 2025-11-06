import streamlit as st
from textblob import TextBlob
import pdfplumber
from docx import Document
import os

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Document Sentiment Analyzer", page_icon="📘", layout="wide")

# =========================
# CSS / THEME
# =========================
st.markdown(
    """
    <style>
    /* Hide default streamlit header and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Body & container */
    .block-container {
        padding-top: 1.5rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1400px;
    }
    body {
        background-color: #f7f9fc;
    }

    /* Top navbar container */
    .topbar {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap: 1rem;
        padding: 10px 8px;
        margin-bottom: 18px;
    }

    .brand {
        display:flex;
        align-items:center;
        gap:12px;
        font-size:18px;
        font-weight:700;
        color:#08306b;
    }

    .nav-pills {
        display:flex;
        gap:10px;
        align-items:center;
    }

    /* Buttons (Streamlit renders its own button elements inside .stButton) */
    .stButton>button, .stDownloadButton>button {
        border-radius:10px;
        padding:8px 14px;
        font-weight:600;
        border: 1px solid rgba(0,64,160,0.12);
    }

    /* Make the active "pill" appear filled */
    .pill-active .stButton>button {
        background-color:#0d6efd;
        color:white;
        border-color: #0d6efd;
        box-shadow: 0 4px 12px rgba(13,110,253,0.12);
    }

    /* Card styling */
    .card {
        background: white;
        border-radius: 10px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(16,24,40,0.06);
        border: 1px solid rgba(15,20,30,0.03);
        margin-bottom: 20px;
    }

    .card-header {
        font-size:18px;
        font-weight:700;
        color:#0b3b73;
        margin-bottom:8px;
    }

    .muted {
        color: #6b7280;
        font-size:14px;
    }

    /* Result metric boxes */
    .metric-row {
        display:flex;
        gap:18px;
    }
    .metric {
        flex:1;
        background: #fbfdff;
        border-radius:8px;
        padding:14px;
        border: 1px solid rgba(13,110,253,0.04);
    }
    .metric .title {
        font-size:13px;
        color:#6b7280;
    }
    .metric .value {
        font-size:20px;
        font-weight:700;
        margin-top:8px;
        color: #0b3b73;
    }

    /* Preview styling */
    .preview {
        background: #fff;
        border-radius: 8px;
        padding: 18px;
        border-left: 5px solid #cfe2ff;
        color: #0b3b73;
    }
    .preview-scroll {
        max-height: 420px;
        overflow-y: auto;
        padding-right: 6px;
    }

    /* highlight classes */
    .highlight-positive { background-color: #d4edda; padding:2px 4px; border-radius:4px; }
    .highlight-negative { background-color: #f8d7da; padding:2px 4px; border-radius:4px; }
    .highlight-neutral { background-color: #fff3cd; padding:2px 4px; border-radius:4px; }

    /* small footers/notes */
    .small-note { font-size:13px; color:#6b7280; margin-top:6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# SESSION STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None
if "text" not in st.session_state:
    st.session_state.text = ""
if "sentiment_score" not in st.session_state:
    st.session_state.sentiment_score = None
if "sentiment_category" not in st.session_state:
    st.session_state.sentiment_category = None
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "word_count" not in st.session_state:
    st.session_state.word_count = 0

# =========================
# NAVBAR (visual)
# =========================
def render_navbar():
    left_col, right_col = st.columns([1, 2])
    with left_col:
        st.markdown(
            "<div class='brand'>📘 &nbsp; Document Sentiment Analyzer</div>",
            unsafe_allow_html=True,
        )
    with right_col:
        # create pill-like buttons using columns to keep layout similar to screenshot
        c1, c2, c3, c4 = st.columns([1,1,1,1])
        with c1:
            if st.button("🏠 Home"):
                st.session_state.page = "home"
        with c2:
            # style this button as active if analyze page
            if st.session_state.page == "analyze":
                st.markdown("<div class='pill-active'>", unsafe_allow_html=True)
                if st.button("🧠 Analyze"):
                    st.session_state.page = "analyze"
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                if st.button("🧠 Analyze"):
                    st.session_state.page = "analyze"
        with c3:
            if st.button("ℹ️ About"):
                st.session_state.page = "about"
        with c4:
            if st.button("✉️ Contact"):
                st.session_state.page = "contact"

render_navbar()
st.write("")  # small spacer

# =========================
# HELPER: Text extraction (unchanged behavior)
# =========================
def read_docx(file):
    try:
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text
    except Exception:
        return ""

def read_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        pass
    return text

# =========================
# SENTIMENT (KEEP EXACT LOGIC)
# =========================
def get_sentiment(text):
    sentiment_score = TextBlob(text).sentiment.polarity
    if sentiment_score > 0.2:
        sentiment_category = "Positive 😊"
    elif sentiment_score < -0.2:
        sentiment_category = "Negative 😔"
    else:
        sentiment_category = "Neutral 😐"
    return sentiment_score, sentiment_category

# word-level highlighting using TextBlob (kept as-is)
def highlight_text(text):
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
    # preserve simple whitespace
    return " ".join(highlighted)

# =========================
# PAGES
# =========================

# HOME PAGE
if st.session_state.page == "home":
    st.markdown("<div class='card' style='text-align:center'>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin-bottom:6px; color:#0b3b73;'>Welcome to Document Sentiment Analyzer 👋</h1>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Understand the tone of your documents instantly!</div>", unsafe_allow_html=True)
    st.markdown("<br/>")
    st.image("https://cdn-icons-png.flaticon.com/512/4781/4781517.png", width=160)
    st.markdown("<br/>")
    st.markdown("<div class='muted'>This web application uses <b>Natural Language Processing (NLP)</b> to analyze the emotional tone of any PDF or Word (.docx) document. It identifies whether the overall sentiment is <b>Positive</b>, <b>Negative</b>, or <b>Neutral</b>.</div>", unsafe_allow_html=True)
    st.markdown("<br/>")
    get_started_col1, get_started_col2, get_started_col3 = st.columns([1,1,1])
    with get_started_col2:
        if st.button("Get Started ➜"):
            st.session_state.page = "analyze"
    st.markdown("</div>", unsafe_allow_html=True)


# ANALYZE PAGE
elif st.session_state.page == "analyze":
    # Upload card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>🧠 Analyze Your Document</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Upload a PDF or Word file</div>", unsafe_allow_html=True)
    st.markdown("<br/>")

    # Use a form so user chooses file then presses a clear "Analyze Sentiment" button (matches screenshots)
    with st.form("upload_form"):
        file = st.file_uploader("Choose File", type=["pdf", "docx"], key="uploader")
        st.write("")  # spacer
        submit_col1, submit_col2 = st.columns([1,4])
        with submit_col1:
            analyze_clicked = st.form_submit_button("🧪 Analyze Sentiment")
        with submit_col2:
            st.write("")  # spacing
        st.markdown("</div>", unsafe_allow_html=True)

    # If a file is chosen, show name
    if file is not None:
        st.session_state.uploaded_filename = file.name

    # If analyze button clicked, process file and compute sentiment (TextBlob logic unchanged)
    if 'analyze_clicked' not in locals():
        analyze_clicked = False

    if analyze_clicked and file is not None:
        # extract text using previous helpers
        if file.name.lower().endswith(".docx"):
            text = read_docx(file)
        else:
            text = read_pdf(file)

        st.session_state.text = text or ""
        st.session_state.word_count = len(st.session_state.text.split())
        # compute sentiment using kept logic
        score, category = get_sentiment(st.session_state.text)
        st.session_state.sentiment_score = score
        st.session_state.sentiment_category = category
        st.session_state.analyzed = True

    # If previously analyzed, show selected filename and offer analysis result cards
    if st.session_state.uploaded_filename:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='muted'>Selected file: <b>{st.session_state.uploaded_filename}</b></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Results section (only show after analysis)
    if st.session_state.analyzed:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>📊 Sentiment Analysis Results</div>", unsafe_allow_html=True)

        # metrics row
        st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
        # Sentiment Score
        score_val = st.session_state.sentiment_score if st.session_state.sentiment_score is not None else 0.0
        st.markdown(f"""
            <div class='metric'>
                <div class='title'>Sentiment Score</div>
                <div class='value'>{score_val:.4f}</div>
                <div class='small-note muted'>Range: -1.0 to +1.0</div>
            </div>
        """, unsafe_allow_html=True)

        # Overall Sentiment
        cat = st.session_state.sentiment_category or "Neutral 😐"
        st.markdown(f"""
            <div class='metric'>
                <div class='title'>Overall Sentiment</div>
                <div class='value'>{cat}</div>
            </div>
        """, unsafe_allow_html=True)

        # Word Count
        wc = st.session_state.word_count
        st.markdown(f"""
            <div class='metric'>
                <div class='title'>Word Count</div>
                <div class='value'>{wc}</div>
                <div class='small-note muted'>Total words analyzed</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)  # close metric-row
        st.markdown("</div>", unsafe_allow_html=True)  # close card

        # Document Preview Card
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-header'>📄 Document Preview <span style='font-weight:400; font-size:13px; color:#6b7280;'>( {st.session_state.uploaded_filename or 'Uploaded Document'} )</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='muted'>Full extracted text from the uploaded document. Positive/negative words are highlighted.</div>", unsafe_allow_html=True)
        st.markdown("<br/>")

        # highlighted entire document
        if st.session_state.text.strip():
            highlighted = highlight_text(st.session_state.text)
            st.markdown(
                "<div class='preview'><div class='preview-scroll'>"
                + highlighted.replace("\n", "<br/>")
                + "</div></div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"<div class='small-note'>Showing full extracted text — Total: {st.session_state.word_count} words</div>", unsafe_allow_html=True)
        else:
            st.info("No readable text could be extracted from this file.")
        st.markdown("</div>", unsafe_allow_html=True)

    # If not analyzed yet, show a placeholder card to guide user
    if not st.session_state.analyzed:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>📄 Document Preview</div>", unsafe_allow_html=True)
        st.markdown("<div class='muted'>No analysis yet. Upload a document and click <b>Analyze Sentiment</b> to see results and a full document preview.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ABOUT PAGE
elif st.session_state.page == "about":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>ℹ️ About This App</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='muted'>
        The <b>Document Sentiment Analyzer</b> was developed by <b>Hemanth Ram. S</b>, a Business Analytics student at PES University, Bengaluru.<br><br>
        <b>Objective:</b> Apply Natural Language Processing (NLP) techniques in real-world scenarios for sentiment classification.<br><br>
        <b>Tech Stack Used:</b><br>
        • Python<br>
        • TextBlob (Sentiment Analysis)<br>
        • pdfplumber & python-docx (Text Extraction)<br>
        • Streamlit (Web Deployment)
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# CONTACT PAGE
elif st.session_state.page == "contact":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>✉️ Connect With Me</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='muted'>
        For collaborations or academic discussions, feel free to reach out:<br><br>
        📧 <a href='mailto:hemanthramhrs@gmail.com'>hemanthramhrs@gmail.com</a><br>
        💼 <a href='https://www.linkedin.com/in/hemanth-ram-9a6a53247' target='_blank'>LinkedIn Profile</a><br>
        🐙 <a href='https://github.com/Hemanthram0205' target='_blank'>GitHub Profile</a>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
