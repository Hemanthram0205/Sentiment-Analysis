import streamlit as st
from textblob import TextBlob
import pdfplumber
from docx import Document
import os

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Document Sentiment Analyzer",
                   page_icon="📘",
                   layout="wide",
                   initial_sidebar_state="collapsed")

# -------------------------
# CSS / Styling (match screenshots)
# -------------------------
st.markdown(
    """
    <style>
    /* Reset streamlit header/footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Page background */
    .stApp {
        background-color: #f7f9fb;
        color: #0f1724;
        font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }

    /* Top nav bar */
    .topbar {
        display:flex;
        align-items:center;
        justify-content:space-between;
        padding: 14px 28px;
        background: #ffffff;
        border-bottom: 1px solid rgba(15,23,36,0.06);
        box-shadow: 0 1px 2px rgba(15,23,36,0.03);
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .brand {
        display:flex;
        align-items:center;
        gap:12px;
        font-weight:600;
        color:#0b2236;
    }
    .brand img {height:28px;}
    .nav-items {display:flex; gap:8px; align-items:center;}
    .nav-btn {
        background: transparent;
        border: 1px solid rgba(11,34,54,0.12);
        color: #0b4bd6;
        padding: 8px 14px;
        border-radius: 10px;
        font-weight:600;
        cursor: pointer;
    }
    .nav-btn.active {
        background: linear-gradient(180deg,#2563eb,#1e40af);
        color: white;
        border-color: transparent;
        box-shadow: 0 6px 18px rgba(37,99,235,0.12);
    }

    /* Page container */
    .container {
        max-width: 1150px;
        margin: 28px auto;
        padding: 0 20px;
    }

    /* Hero */
    .hero {
        background: transparent;
        padding: 40px 0;
        text-align: center;
    }
    .hero h1 {
        font-size:36px;
        margin-bottom:6px;
        color:#0b2236;
    }
    .hero p {
        margin-top:0;
        color:#3b4a57;
        max-width:900px;
        margin-left:auto;
        margin-right:auto;
        font-size:16px;
    }
    .cta {
        margin-top:22px;
    }
    .cta .btn-primary {
        background: linear-gradient(180deg,#2563eb,#1e40af);
        color:white;
        padding:10px 18px;
        border-radius:9px;
        border: none;
        font-weight:600;
        cursor:pointer;
    }

    /* Card */
    .card {
        background: #fff;
        border-radius: 10px;
        padding: 18px;
        border: 1px solid rgba(11,34,54,0.06);
        box-shadow: 0 6px 20px rgba(2,6,23,0.03);
        margin-bottom: 18px;
    }

    /* Results metrics row */
    .metrics {
        display:flex;
        gap:16px;
        align-items:stretch;
        justify-content: flex-start;
    }
    .metric {
        flex:1;
        padding:14px;
        border-radius:8px;
        background: #fbfdff;
        border:1px solid rgba(11,34,54,0.03);
    }
    .metric h3 {margin:0; font-size:14px; color:#0b2236;}
    .metric .value {font-size:28px; margin-top:8px; font-weight:700; color:#0b2236;}

    /* Preview area */
    .preview-box {
        max-height:420px;
        overflow:auto;
        padding:18px;
        border-radius:8px;
        border-left: 4px solid #cfe2ff;
        background: #fbfdff;
        color:#0b2236;
        line-height:1.6;
    }

    /* small caption */
    .muted {color:#6b7280; font-size:13px;}

    /* Buttons inside cards */
    .card-btn {
        background: #2563eb;
        color: white;
        padding:10px 14px;
        border-radius:8px;
        border:none;
        font-weight:600;
        cursor:pointer;
    }

    /* Highlight colors for words (kept same semantics) */
    .highlight-positive { background-color: #d4edda; padding:2px 4px; border-radius:4px; }
    .highlight-negative { background-color: #f8d7da; padding:2px 4px; border-radius:4px; }
    .highlight-neutral { background-color: #fff3cd; padding:2px 4px; border-radius:4px; }

    /* Small footer */
    .footer {
        text-align:center;
        color:#6b7280;
        margin:36px 0 72px 0;
    }

    /* Responsive tweaks */
    @media (max-width:900px){
        .metrics {flex-direction:column;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Helper: include local hero image if exists
# -------------------------
def get_local_image_path(name):
    # use developer-provided images if present
    path = os.path.join("/mnt/data", name)
    return path if os.path.exists(path) else None

# -------------------------
# Session state for page
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# -------------------------
# NAVBAR (rendered via markdown + small buttons)
# -------------------------
def render_navbar(active="home"):
    logo = get_local_image_path("11fa2720-12a8-4c8b-9c3b-c028fdcbb4cc.png")
    if logo:
        brand_img_html = f"<img src='file://{logo}' />"
    else:
        # fallback icon emoji
        brand_img_html = "📘"

    left_html = f"""
    <div class="topbar">
        <div class="brand">
            {brand_img_html}
            <div>Document Sentiment Analyzer</div>
        </div>
        <div class="nav-items">
            <div class="nav-btn {'active' if active=='home' else ''}" onclick="window.streamlit.setComponentValue('nav_home')">Home</div>
            <div class="nav-btn {'active' if active=='analyze' else ''}" onclick="window.streamlit.setComponentValue('nav_analyze')">Analyze</div>
            <div class="nav-btn {'active' if active=='about' else ''}" onclick="window.streamlit.setComponentValue('nav_about')">About</div>
            <div class="nav-btn {'active' if active=='contact' else ''}" onclick="window.streamlit.setComponentValue('nav_contact')">Contact</div>
        </div>
    </div>
    """

    # Streamlit can't directly capture onclick to python, but we will render buttons below to set session state.
    st.markdown(left_html, unsafe_allow_html=True)

# Because the custom clickable divs won't actually call Python, render real st.buttons (invisible) next to the navbar for accessibility:
def render_nav_buttons():
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    with col1:
        if st.button("Home", key="nav_home_btn"):
            st.session_state.page = "home"
    with col2:
        if st.button("Analyze", key="nav_analyze_btn"):
            st.session_state.page = "analyze"
    with col3:
        if st.button("About", key="nav_about_btn"):
            st.session_state.page = "about"
    with col4:
        if st.button("Contact", key="nav_contact_btn"):
            st.session_state.page = "contact"

# Render navbar (visual) then invisible buttons
render_navbar(active=st.session_state.get("page", "home"))
render_nav_buttons()

# -------------------------
# Helper functions (TEXT extraction & sentiment) <--- DO NOT CHANGE logic as requested
# -------------------------
def read_docx(file):
    try:
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
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

def get_sentiment(text):
    # Original TextBlob-based sentiment logic preserved (unchanged)
    sentiment_score = TextBlob(text).sentiment.polarity
    if sentiment_score > 0.2:
        sentiment_category = "Positive 😊"
    elif sentiment_score < -0.2:
        sentiment_category = "Negative 😔"
    else:
        sentiment_category = "Neutral 😐"
    return sentiment_score, sentiment_category

def highlight_text(text):
    # Keep the same TextBlob-based per-word highlighting logic (unchanged)
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
    return " ".join(highlighted)

# -------------------------
# PAGES
# -------------------------
page = st.session_state.page

# ---------- HOME ----------
if page == "home":
    # container for alignment & spacing
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<h1>Welcome to Document Sentiment Analyzer 👋</h1>', unsafe_allow_html=True)
    st.markdown(
        "<p>Understand the tone of your documents instantly!<br><br>"
        "This web application uses <strong>Natural Language Processing (NLP)</strong> to analyze the emotional tone of any PDF or Word (.docx) document. "
        "It identifies whether the overall sentiment is <strong>Positive</strong>, <strong>Negative</strong>, or <strong>Neutral</strong>.</p>",
        unsafe_allow_html=True,
    )

    # show hero image if available
    hero_img = get_local_image_path("e6b66a95-d24a-4e23-b6ec-6a3e8a458ae4.png")  # developer provided image
    if hero_img:
        st.image(hero_img, width=210)

    # CTA
    st.markdown(
        '<div class="cta"><button class="btn-primary" onclick="window.scrollTo(0, document.body.scrollHeight);">Get Started ▶</button></div>',
        unsafe_allow_html=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- ANALYZE ----------
elif page == "analyze":
    st.markdown('<div class="container">', unsafe_allow_html=True)

    # Upload card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="margin:0 0 8px 0;">🧠 Analyze Your Document</h2>', unsafe_allow_html=True)
    st.markdown('<div class="muted" style="margin-bottom:12px;">Upload a PDF or Word (.docx) file</div>', unsafe_allow_html=True)

    # file uploader and analyze button arrangement
    uploaded_file = st.file_uploader("", type=["pdf", "docx"], key="uploader")
    analyze_clicked = False
    # show chosen file name & analyze button as in screenshot
    if uploaded_file:
        st.markdown(f"<div class='muted' style='margin-top:10px;'>Selected file: <strong>{uploaded_file.name}</strong></div>", unsafe_allow_html=True)
        analyze_clicked = st.button("🧠 Analyze Sentiment", key="analyze_btn", help="Click to analyze the uploaded file")
    else:
        # keep button disabled (visual) by showing instruction
        st.markdown("<div class='muted' style='margin-top:10px;'>Choose a file to enable analysis</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # end card

    # If file uploaded and analyze clicked -> perform extraction & sentiment (logic unchanged)
    if uploaded_file and analyze_clicked:
        # read the file according to extension
        if uploaded_file.name.lower().endswith(".docx"):
            text_data = read_docx(uploaded_file)
        elif uploaded_file.name.lower().endswith(".pdf"):
            text_data = read_pdf(uploaded_file)
        else:
            text_data = ""

        # If no text extracted, show error
        if not text_data.strip():
            st.error("No readable text found in this file. Please upload a text-based PDF or Word document.")
        else:
            # compute sentiment (kept unchanged)
            with st.spinner("Analyzing sentiment..."):
                sentiment_score, sentiment_category = get_sentiment(text_data)

            # Results card with metrics (score, overall sentiment, word count)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin:0 0 8px 0;">📊 Sentiment Analysis Results</h3>', unsafe_allow_html=True)
            st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

            # metrics row - three columns
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                st.markdown('<div class="metric">', unsafe_allow_html=True)
                st.markdown('<h3>Sentiment Score</h3>', unsafe_allow_html=True)
                st.markdown(f'<div class="value">{sentiment_score:.3f}</div>', unsafe_allow_html=True)
                st.markdown('<div class="muted">Range: -1.0 to +1.0</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric">', unsafe_allow_html=True)
                st.markdown('<h3>Overall Sentiment</h3>', unsafe_allow_html=True)
                st.markdown(f'<div class="value">{sentiment_category}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="metric">', unsafe_allow_html=True)
                st.markdown('<h3>Word Count</h3>', unsafe_allow_html=True)
                wc = len(text_data.split())
                st.markdown(f'<div class="value">{wc}</div>', unsafe_allow_html=True)
                st.markdown('<div class="muted">Total words analyzed</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # end results card

            # Preview card (full document highlighted inside scrollable preview)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<h3 style="margin:0 0 8px 0;">📝 Document Preview <span style="color:#6b7280; font-size:13px;">({uploaded_file.name})</span></h3>', unsafe_allow_html=True)
            st.markdown('<div class="muted" style="margin-bottom:8px;">Full extracted text is shown below. Use the scroll bar to read long documents.</div>', unsafe_allow_html=True)

            # Keep highlight_text logic unchanged (uses TextBlob for per-word polarity)
            highlighted_html = highlight_text(text_data)
            # wrap into preview box
            preview_html = f"<div class='preview-box'>{highlighted_html}</div>"
            st.markdown(preview_html, unsafe_allow_html=True)

            # small footer line under preview similar to screenshot
            st.markdown("<div style='margin-top:10px; text-align:center;' class='muted'>Showing full extracted text · Total words: {}</div>".format(wc), unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)  # end preview card

    # If file uploaded but analyze not clicked yet: show lightweight preview of top portion and count
    elif uploaded_file and not analyze_clicked:
        # show a lightweight card telling user to click analyze
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin:0 0 8px 0;">📄 Ready to Analyze</h3>', unsafe_allow_html=True)
        st.markdown(f'<div class="muted">Selected file: <strong>{uploaded_file.name}</strong></div>', unsafe_allow_html=True)
        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="muted">Click <strong>Analyze Sentiment</strong> to compute the sentiment for the entire document.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # end container

# ---------- ABOUT ----------
elif page == "about":
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="margin:0 0 8px 0;">ℹ️ About This App</h2>', unsafe_allow_html=True)
    st.markdown("""
        <div class="muted" style="margin-bottom:10px;">
        The <strong>Document Sentiment Analyzer</strong> was developed by <strong>Hemanth Ram. S</strong>, a Business Analytics student at <strong>PES University, Bengaluru</strong>.
        </div>
        <h4 style="margin-top:6px;">Objective</h4>
        <div class="muted">To apply Natural Language Processing (NLP) and Machine Learning techniques in real-world scenarios for sentiment classification.</div>
        <h4 style="margin-top:14px;">Tech Stack</h4>
        <ul style="margin-top:6px;">
            <li>Python</li>
            <li>TextBlob (Sentiment Analysis)</li>
            <li>pdfplumber & python-docx (Text Extraction)</li>
            <li>Streamlit (UI)</li>
        </ul>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- CONTACT ----------
elif page == "contact":
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="margin:0 0 8px 0;">✉️ Connect With Me</h2>', unsafe_allow_html=True)
    st.markdown("""
        <div class="muted" style="margin-bottom:12px;">
        For collaborations or academic discussions, feel free to reach out:
        </div>
        <div style="margin-top:6px;">
            <div style="background:#eff6ff;padding:12px;border-radius:8px;margin-bottom:8px;"><strong>📧</strong> hemanthramhrs@gmail.com</div>
            <div style="background:#eff6ff;padding:12px;border-radius:8px;margin-bottom:8px;"><strong>💼</strong> LinkedIn Profile</div>
            <div style="background:#eff6ff;padding:12px;border-radius:8px;"><strong>🐙</strong> GitHub Profile</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown('<div class="footer">© 2025 Hemanth Ram. S | PES University | Built with Streamlit</div>', unsafe_allow_html=True)
