import streamlit as st
from textblob import TextBlob
import pdfplumber
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import io
from datetime import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Document Sentiment Analyzer", page_icon="📘", layout="wide")

# =========================
# CUSTOM STYLING
# =========================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {
    padding-top: 0.5rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1400px;
}
body {
    background-color: #f7f9fc;
}

/* Topbar */
.topbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding: 10px 0;
    margin-bottom: 0px;
}
.brand {
    display:flex;
    align-items:center;
    gap:10px;
    font-size:24px;
    font-weight:700;
    color:#08306b;
}
.stButton>button {
    border-radius:10px;
    padding:8px 14px;
    font-weight:600;
    border: 1px solid rgba(0,64,160,0.12);
}
.pill-active .stButton>button {
    background-color:#0d6efd;
    color:white;
    border-color:#0d6efd;
    box-shadow:0 4px 12px rgba(13,110,253,0.12);
}

/* Card */
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

/* Metrics */
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

/* Preview box */
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
.highlight-positive {background-color: #d4edda; padding:2px 4px; border-radius:4px;}
.highlight-negative {background-color: #f8d7da; padding:2px 4px; border-radius:4px;}
.highlight-neutral {background-color: #fff3cd; padding:2px 4px; border-radius:4px;}
.small-note {font-size:13px; color:#6b7280; margin-top:6px;}
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "text" not in st.session_state:
    st.session_state.text = ""
if "sentiment_score" not in st.session_state:
    st.session_state.sentiment_score = None
if "sentiment_category" not in st.session_state:
    st.session_state.sentiment_category = None
if "word_count" not in st.session_state:
    st.session_state.word_count = 0
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

# =========================
# NAVBAR
# =========================
def render_navbar():
    left, right = st.columns([1, 2])
    with left:
        st.markdown("<div class='brand'>📘 Document Sentiment Analyzer</div>", unsafe_allow_html=True)
    with right:
        c1, c2, c3, c4 = st.columns([1,1,1,1])
        with c1:
            if st.button("🏠 Home"):
                st.session_state.page = "home"
        with c2:
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

# Remove ALL white boxes and spacing
st.markdown("""
<style>
.element-container:has(.stButton) {
    margin-bottom: 0 !important;
}
div[data-testid="column"] {
    padding-bottom: 0 !important;
}
.element-container {
    margin-bottom: 0 !important;
}
div[data-testid="stVerticalBlock"] > div {
    gap: 0 !important;
}
.stMarkdown {
    margin-bottom: 0 !important;
}
/* Hide empty containers */
.element-container:empty {
    display: none !important;
}
div.row-widget.stButton {
    margin-bottom: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
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
    score = TextBlob(text).sentiment.polarity
    if score > 0.2:
        category = "Positive 😊"
    elif score < -0.2:
        category = "Negative 😔"
    else:
        category = "Neutral 😐"
    return score, category

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
    return " ".join(highlighted)

def generate_pdf_report(filename, text, sentiment_score, sentiment_category, word_count):
    """Generate a PDF report for sentiment analysis"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0b3b73'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#0b3b73'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # Title
    story.append(Paragraph("📘 Document Sentiment Analysis Report", title_style))
    story.append(Spacer(1, 20))
    
    # Document Information
    story.append(Paragraph("Document Information", heading_style))
    
    # Create a table for document info
    doc_info_data = [
        ['File Name:', filename],
        ['Analysis Date:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ['Word Count:', str(word_count)]
    ]
    
    doc_info_table = Table(doc_info_data, colWidths=[2*inch, 4*inch])
    doc_info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONT', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(doc_info_table)
    story.append(Spacer(1, 20))
    
    # Sentiment Analysis Results
    story.append(Paragraph("Sentiment Analysis Results", heading_style))
    
    # Determine color based on sentiment
    if sentiment_score > 0.2:
        score_color = colors.green
        sentiment_text = "Positive"
    elif sentiment_score < -0.2:
        score_color = colors.red
        sentiment_text = "Negative"
    else:
        score_color = colors.orange
        sentiment_text = "Neutral"
    
    # Results table
    results_data = [
        ['Sentiment Score:', f'{sentiment_score:.4f}'],
        ['Overall Sentiment:', sentiment_category.replace('😊', '').replace('😔', '').replace('😐', '').strip()],
        ['Polarity Range:', '-1.0 (Most Negative) to +1.0 (Most Positive)']
    ]
    
    results_table = Table(results_data, colWidths=[2*inch, 4*inch])
    results_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONT', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
        ('TEXTCOLOR', (1, 0), (1, 0), score_color),
        ('TEXTCOLOR', (1, 1), (1, 1), score_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(results_table)
    story.append(Spacer(1, 20))
    
    # Document Preview (First 200 words)
    story.append(Paragraph("Document Preview (First 200 Words)", heading_style))
    
    # Get first 200 words
    words = text.split()[:200]
    preview_text = ' '.join(words)
    if len(text.split()) > 200:
        preview_text += "..."
    
    # Clean the text for PDF (remove special characters that might cause issues)
    preview_text = preview_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    story.append(Paragraph(preview_text, normal_style))
    story.append(Spacer(1, 20))
    
    # Interpretation Guide
    story.append(Paragraph("Interpretation Guide", heading_style))
    interpretation_text = """
    • <b>Positive Sentiment (Score > 0.2):</b> The document contains predominantly positive language, expressing favorable opinions, satisfaction, or optimism.<br/>
    • <b>Negative Sentiment (Score < -0.2):</b> The document contains predominantly negative language, expressing dissatisfaction, criticism, or pessimism.<br/>
    • <b>Neutral Sentiment (-0.2 ≤ Score ≤ 0.2):</b> The document maintains a balanced or objective tone without strong emotional language.
    """
    story.append(Paragraph(interpretation_text, normal_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# =========================
# PAGES
# =========================
if st.session_state.page == "home":
    st.markdown("<div class='card' style='text-align:center'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:#0b3b73;'>Welcome to Document Sentiment Analyzer 👋</h1>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Understand the tone of your documents instantly!</div>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/4781/4781517.png", width=150)
    st.markdown("<div class='muted'>This app uses <b>Natural Language Processing (NLP)</b> to analyze the tone of PDF or Word (.docx) files and determine if they are <b>Positive</b>, <b>Negative</b>, or <b>Neutral</b>.</div>", unsafe_allow_html=True)
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("Get Started ➜"):
        st.session_state.page = "analyze"
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "analyze":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>🧠 Analyze Your Document</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Upload a PDF or Word file</div>", unsafe_allow_html=True)
    with st.form("upload_form"):
        file = st.file_uploader("Choose File", type=["pdf", "docx"])
        analyze_clicked = st.form_submit_button("🧪 Analyze Sentiment")

    if file:
        st.session_state.uploaded_filename = file.name
    if analyze_clicked and file:
        if file.name.lower().endswith(".docx"):
            text = read_docx(file)
        else:
            text = read_pdf(file)
        st.session_state.text = text or ""
        st.session_state.word_count = len(st.session_state.text.split())
        score, category = get_sentiment(st.session_state.text)
        st.session_state.sentiment_score = score
        st.session_state.sentiment_category = category
        st.session_state.analyzed = True
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.analyzed:
        # Results
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>📊 Sentiment Analysis Results</div>", unsafe_allow_html=True)
        st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='metric'>
                <div class='title'>Sentiment Score</div>
                <div class='value'>{st.session_state.sentiment_score:.4f}</div>
            </div>
            <div class='metric'>
                <div class='title'>Overall Sentiment</div>
                <div class='value'>{st.session_state.sentiment_category}</div>
            </div>
            <div class='metric'>
                <div class='title'>Word Count</div>
                <div class='value'>{st.session_state.word_count}</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Download Report Button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            pdf_buffer = generate_pdf_report(
                st.session_state.uploaded_filename,
                st.session_state.text,
                st.session_state.sentiment_score,
                st.session_state.sentiment_category,
                st.session_state.word_count
            )
            
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_buffer,
                file_name=f"sentiment_analysis_{st.session_state.uploaded_filename.split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                help="Download the complete sentiment analysis report as PDF"
            )
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Preview
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='card-header'>📄 Document Preview <span style='font-weight:400; font-size:13px; color:#6b7280;'>({st.session_state.uploaded_filename})</span></div>", unsafe_allow_html=True)
        st.markdown("<div class='muted'>Full extracted text from the uploaded document. Positive/negative words are highlighted.</div>", unsafe_allow_html=True)
        highlighted = highlight_text(st.session_state.text)
        highlighted = highlighted.replace("\n\n", "</p><p>").replace("\n", " ")
        st.markdown(f"<div class='preview'><div class='preview-scroll'><p>{highlighted}</p></div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small-note'>Showing full extracted text — Total: {st.session_state.word_count} words</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "about":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>ℹ️ About This App</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='muted'>
    <b>Document Sentiment Analyzer</b> was developed by <b>Hemanth Ram. S</b>, a Business Analytics student at PES University, Bengaluru.<br><br>
    <b>Objective:</b> Apply NLP and Machine Learning techniques for sentiment classification.<br><br>
    <b>Tech Stack Used:</b><br>
    • Python<br>
    • TextBlob (Sentiment Analysis)<br>
    • pdfplumber & python-docx (Text Extraction)<br>
    • Streamlit (Web Deployment)<br>
    • ReportLab (PDF Report Generation)
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "contact":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>✉️ Connect With Me</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='muted'>
    For collaborations or academic discussions:<br><br>
    📧 <a href='mailto:hemanthramhrs@gmail.com'>hemanthramhrs@gmail.com</a><br>
    💼 <a href='https://www.linkedin.com/in/hemanth-ram-9a6a53247' target='_blank'>LinkedIn Profile</a><br>
    🐙 <a href='https://github.com/Hemanthram0205' target='_blank'>GitHub Profile</a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
