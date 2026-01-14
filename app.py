"""
Document Analyzer - Advanced Text Analysis Platform
Streamlit Application

To run this application:
1. Install dependencies: pip install streamlit pandas PyPDF2 python-docx openpyxl mammoth
2. Run the app: streamlit run app.py
3. Open http://localhost:8501 in your browser

Database: SQLite (document_analyzer.db) - automatically created on first run
"""

import streamlit as st
import sqlite3
import hashlib
import uuid
import re
import json
from datetime import datetime
import io
import base64

# Page config
st.set_page_config(
    page_title="Document Analyzer - Advanced Text Analysis Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match original design
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container styling */
    .main {
        background-color: #f9fafb;
    }
    
    /* Card styling */
    .card-shadow {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    /* Stat card */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    /* Highlight classes */
    .highlight-positive {
        background-color: #d4edda;
        padding: 2px 4px;
        border-radius: 4px;
    }
    
    .highlight-negative {
        background-color: #f8d7da;
        padding: 2px 4px;
        border-radius: 4px;
    }
    
    .highlight-neutral {
        background-color: #fff3cd;
        padding: 2px 4px;
        border-radius: 4px;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 0.5rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    /* Remove streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f3f4f6;
        border-radius: 0.5rem;
        padding: 0.25rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 0.375rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        color: #2563eb;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATABASE ====================

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('document_analyzer.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  is_admin INTEGER DEFAULT 0,
                  api_key TEXT UNIQUE NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Analyses table
    c.execute('''CREATE TABLE IF NOT EXISTS analyses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  source TEXT NOT NULL,
                  text_preview TEXT,
                  word_count INTEGER DEFAULT 0,
                  analysis_types TEXT,
                  sentiment_score REAL,
                  sentiment_label TEXT,
                  sentiment_positive REAL,
                  sentiment_negative REAL,
                  sentiment_neutral REAL,
                  language_code TEXT,
                  language_name TEXT,
                  language_confidence REAL,
                  emotions_json TEXT,
                  entities_json TEXT,
                  keywords_json TEXT,
                  summary_text TEXT,
                  summary_words INTEGER,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Create demo accounts if they don't exist
    c.execute("SELECT COUNT(*) FROM users WHERE email='admin@demo.com'")
    if c.fetchone()[0] == 0:
        admin_api_key = 'admin-' + str(uuid.uuid4())
        admin_pass = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (name, email, password_hash, is_admin, api_key) VALUES (?, ?, ?, ?, ?)",
                  ('Admin User', 'admin@demo.com', admin_pass, 1, admin_api_key))
    
    c.execute("SELECT COUNT(*) FROM users WHERE email='user@demo.com'")
    if c.fetchone()[0] == 0:
        user_api_key = 'user-' + str(uuid.uuid4())
        user_pass = hashlib.sha256('user123'.encode()).hexdigest()
        c.execute("INSERT INTO users (name, email, password_hash, is_admin, api_key) VALUES (?, ?, ?, ?, ?)",
                  ('Regular User', 'user@demo.com', user_pass, 0, user_api_key))
    
    conn.commit()
    conn.close()

def get_user(email, password):
    """Authenticate user"""
    conn = sqlite3.connect('document_analyzer.db')
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE email=? AND password_hash=?", (email, password_hash))
    user = c.fetchone()
    conn.close()
    if user:
        return {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'is_admin': bool(user[4]),
            'api_key': user[5]
        }
    return None

def create_user(name, email, password, is_admin=False):
    """Create new user"""
    conn = sqlite3.connect('document_analyzer.db')
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    api_key = str(uuid.uuid4())
    try:
        c.execute("INSERT INTO users (name, email, password_hash, is_admin, api_key) VALUES (?, ?, ?, ?, ?)",
                  (name, email, password_hash, int(is_admin), api_key))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def save_analysis(user_id, source, text, analysis_types, results):
    """Save analysis to database"""
    conn = sqlite3.connect('document_analyzer.db')
    c = conn.cursor()
    
    sentiment = results.get('sentiment', {})
    language = results.get('language', {})
    
    c.execute("""INSERT INTO analyses 
                 (user_id, source, text_preview, word_count, analysis_types,
                  sentiment_score, sentiment_label, sentiment_positive, sentiment_negative, sentiment_neutral,
                  language_code, language_name, language_confidence,
                  emotions_json, entities_json, keywords_json, summary_text, summary_words)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (user_id, source, text[:500], len(text.split()), ', '.join(analysis_types),
               sentiment.get('score'), sentiment.get('label'), sentiment.get('positive'),
               sentiment.get('negative'), sentiment.get('neutral'),
               language.get('code'), language.get('name'), language.get('confidence'),
               json.dumps(results.get('emotions', {})), json.dumps(results.get('entities', [])),
               json.dumps(results.get('keywords', [])), 
               results.get('summary', {}).get('summary'),
               results.get('summary', {}).get('summaryWords')))
    
    conn.commit()
    conn.close()

def get_user_analyses(user_id):
    """Get all analyses for a user"""
    conn = sqlite3.connect('document_analyzer.db')
    c = conn.cursor()
    c.execute("SELECT * FROM analyses WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    analyses = c.fetchall()
    conn.close()
    return analyses

def get_all_analyses():
    """Get all analyses (admin only)"""
    conn = sqlite3.connect('document_analyzer.db')
    c = conn.cursor()
    c.execute("""SELECT a.*, u.name, u.email FROM analyses a 
                 JOIN users u ON a.user_id = u.id 
                 ORDER BY a.created_at DESC""")
    analyses = c.fetchall()
    conn.close()
    return analyses

def get_user_stats(user_id):
    """Get statistics for user"""
    conn = sqlite3.connect('document_analyzer.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM analyses WHERE user_id=?", (user_id,))
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM analyses WHERE user_id=? AND sentiment_label LIKE '%Positive%'", (user_id,))
    positive = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM analyses WHERE user_id=? AND sentiment_label LIKE '%Negative%'", (user_id,))
    negative = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM analyses WHERE user_id=? AND sentiment_label LIKE '%Neutral%'", (user_id,))
    neutral = c.fetchone()[0]
    conn.close()
    return {'total': total, 'positive': positive, 'negative': negative, 'neutral': neutral}

def get_admin_stats():
    """Get admin statistics"""
    conn = sqlite3.connect('document_analyzer.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM analyses")
    total_analyses = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM analyses WHERE sentiment_label LIKE '%Positive%'")
    positive = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM analyses WHERE sentiment_label LIKE '%Negative%'")
    negative = c.fetchone()[0]
    conn.close()
    return {'totalUsers': total_users, 'totalAnalyses': total_analyses, 
            'positive': positive, 'negative': negative}

def clear_user_analyses(user_id):
    """Clear all analyses for a user"""
    conn = sqlite3.connect('document_analyzer.db')
    c = conn.cursor()
    c.execute("DELETE FROM analyses WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def regenerate_api_key(user_id):
    """Regenerate API key for user"""
    conn = sqlite3.connect('document_analyzer.db')
    c = conn.cursor()
    new_key = str(uuid.uuid4())
    c.execute("UPDATE users SET api_key=? WHERE id=?", (new_key, user_id))
    conn.commit()
    conn.close()
    return new_key

# ==================== TEXT ANALYSIS FUNCTIONS ====================

POSITIVE_WORDS = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome', 
                  'love', 'happy', 'joy', 'beautiful', 'best', 'perfect', 'brilliant', 'outstanding',
                  'superb', 'terrific', 'delightful', 'pleasant', 'positive', 'success', 'successful',
                  'win', 'winning', 'benefit', 'helpful', 'useful', 'effective', 'impressive',
                  'remarkable', 'exceptional', 'incredible', 'fabulous', 'magnificent', 'satisfying',
                  'pleased', 'glad', 'fortunate', 'lucky', 'favorable', 'promising', 'exciting',
                  'thrilled', 'grateful', 'proud', 'confident', 'optimistic']

NEGATIVE_WORDS = ['bad', 'terrible', 'awful', 'horrible', 'poor', 'worst', 'hate', 'sad', 
                  'angry', 'ugly', 'fail', 'failure', 'wrong', 'error', 'mistake', 'problem',
                  'issue', 'difficult', 'hard', 'negative', 'loss', 'lose', 'damage', 'harm',
                  'harmful', 'hurt', 'pain', 'painful', 'suffer', 'unfortunate', 'disappointing',
                  'frustrated', 'annoying', 'boring', 'useless', 'worthless', 'weak', 'inferior',
                  'mediocre', 'inadequate', 'dreadful', 'miserable', 'tragic', 'hopeless',
                  'worried', 'anxious', 'scared', 'afraid']

EMOTION_WORDS = {
    'joy': ['happy', 'joy', 'excited', 'delighted', 'pleased', 'thrilled', 'ecstatic', 
            'cheerful', 'elated', 'jubilant', 'love', 'wonderful', 'amazing', 'fantastic'],
    'sadness': ['sad', 'unhappy', 'depressed', 'miserable', 'heartbroken', 'grief', 
                'sorrow', 'melancholy', 'gloomy', 'disappointed', 'hopeless', 'lonely', 'hurt'],
    'anger': ['angry', 'furious', 'rage', 'irritated', 'annoyed', 'frustrated', 
              'outraged', 'hostile', 'bitter', 'resentful', 'hate', 'mad', 'livid'],
    'fear': ['afraid', 'scared', 'fearful', 'terrified', 'anxious', 'worried', 
             'nervous', 'panicked', 'frightened', 'alarmed', 'dread', 'horror'],
    'surprise': ['surprised', 'amazed', 'astonished', 'shocked', 'stunned', 
                 'startled', 'unexpected', 'incredible', 'unbelievable', 'wow'],
    'disgust': ['disgusted', 'revolted', 'repulsed', 'sickened', 'gross', 
                'nasty', 'awful', 'terrible', 'horrible', 'offensive']
}

LANGUAGE_PATTERNS = {
    'en': {'name': 'English', 'flag': '🇬🇧', 'words': ['the', 'is', 'are', 'was', 'were', 'have', 'has', 'been', 'being', 'and', 'or', 'but', 'with', 'for', 'that', 'this']},
    'es': {'name': 'Spanish', 'flag': '🇪🇸', 'words': ['el', 'la', 'los', 'las', 'de', 'en', 'que', 'es', 'por', 'con', 'para', 'como', 'pero', 'más', 'este', 'esta']},
    'fr': {'name': 'French', 'flag': '🇫🇷', 'words': ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'est', 'que', 'qui', 'dans', 'pour', 'pas', 'sur', 'avec', 'plus']},
    'de': {'name': 'German', 'flag': '🇩🇪', 'words': ['der', 'die', 'das', 'und', 'ist', 'von', 'mit', 'für', 'auf', 'nicht', 'auch', 'als', 'eine', 'aber', 'oder']},
    'it': {'name': 'Italian', 'flag': '🇮🇹', 'words': ['il', 'la', 'di', 'che', 'non', 'per', 'una', 'sono', 'con', 'come', 'anche', 'più', 'del', 'della']},
    'pt': {'name': 'Portuguese', 'flag': '🇵🇹', 'words': ['o', 'a', 'os', 'as', 'de', 'que', 'em', 'para', 'com', 'não', 'uma', 'por', 'mais', 'como']},
}

def analyze_sentiment(text):
    """Analyze sentiment of text"""
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    pos_count = sum(1 for word in words if word in POSITIVE_WORDS)
    neg_count = sum(1 for word in words if word in NEGATIVE_WORDS)
    
    total = pos_count + neg_count or 1
    score = (pos_count - neg_count) / total
    
    positive = pos_count / total
    negative = neg_count / total
    neutral = max(0, 1 - positive - negative)
    
    if score > 0.2:
        label = 'Positive 😊'
    elif score < -0.2:
        label = 'Negative 😔'
    else:
        label = 'Neutral 😐'
    
    confidence = abs(score) * 100
    
    return {
        'score': round(score, 4),
        'label': label,
        'confidence': round(confidence, 0),
        'positive': round(positive * 100, 0),
        'negative': round(negative * 100, 0),
        'neutral': round(neutral * 100, 0)
    }

def extract_entities(text):
    """Extract named entities from text"""
    entities = []
    
    # Person names (two capitalized words)
    persons = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text)
    for p in persons[:5]:
        entities.append({'text': p, 'type': 'PERSON', 'confidence': round(0.7 + 0.25 * (uuid.uuid4().int % 100) / 100, 2)})
    
    # Organizations
    orgs = ['Google', 'Microsoft', 'Apple', 'Amazon', 'Facebook', 'Meta', 'Tesla', 'IBM', 
            'Intel', 'Netflix', 'Twitter', 'LinkedIn', 'Uber', 'Airbnb', 'Spotify']
    for org in orgs:
        if org.lower() in text.lower():
            entities.append({'text': org, 'type': 'ORGANIZATION', 'confidence': 0.92})
    
    # Locations
    locations = ['New York', 'Los Angeles', 'London', 'Paris', 'Tokyo', 'Beijing', 
                 'Shanghai', 'Mumbai', 'Dubai', 'Singapore', 'Sydney', 'Toronto',
                 'USA', 'UK', 'China', 'India', 'Japan', 'Germany', 'France']
    for loc in locations:
        if loc.lower() in text.lower():
            entities.append({'text': loc, 'type': 'LOCATION', 'confidence': 0.88})
    
    # Emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    for email in emails[:3]:
        entities.append({'text': email, 'type': 'EMAIL', 'confidence': 0.99})
    
    # URLs
    urls = re.findall(r'https?://[^\s]+', text)
    for url in urls[:3]:
        entities.append({'text': url, 'type': 'URL', 'confidence': 0.99})
    
    return entities[:20]

def extract_keywords(text):
    """Extract keywords from text"""
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    
    stop_words = ['this', 'that', 'with', 'from', 'have', 'been', 'were', 'they', 
                  'their', 'what', 'when', 'where', 'which', 'while', 'about',
                  'would', 'there', 'could', 'other', 'after', 'first', 'also',
                  'made', 'many', 'before', 'being', 'through', 'just', 'over',
                  'such', 'into', 'year', 'some', 'them', 'than', 'then', 'only']
    
    freq = {}
    for word in words:
        if word not in stop_words:
            freq[word] = freq.get(word, 0) + 1
    
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:15]
    total_words = len(words) or 1
    
    return [{'text': word, 'relevance': round(count / total_words * 100, 1)} 
            for word, count in sorted_words]

def detect_language(text):
    """Detect language of text"""
    words = text.lower().split()
    
    max_score = 0
    detected = {'code': 'en', 'name': 'English', 'flag': '🇬🇧'}
    
    for code, lang in LANGUAGE_PATTERNS.items():
        score = sum(1 for w in lang['words'] if w in words)
        if score > max_score:
            max_score = score
            detected = {'code': code, 'name': lang['name'], 'flag': lang['flag']}
    
    confidence = min(95, 60 + max_score * 5)
    
    return {**detected, 'confidence': confidence}

def analyze_emotions(text):
    """Analyze emotions in text"""
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    emotions = {}
    total = 0
    
    for emotion, emotion_words in EMOTION_WORDS.items():
        count = sum(1 for word in words if word in emotion_words)
        emotions[emotion] = count
        total += count
    
    total = total or 1
    
    return {emotion: round((count / total) * 100, 0) 
            for emotion, count in emotions.items()}

def summarize_text(text):
    """Generate a summary of text"""
    sentences = re.findall(r'[^.!?]+[.!?]+', text) or [text]
    num_sentences = max(2, int(len(sentences) * 0.3))
    
    summary = ' '.join(sentences[:num_sentences]).strip()
    
    return {
        'summary': summary,
        'originalWords': len(text.split()),
        'summaryWords': len(summary.split())
    }

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file"""
    try:
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        if file_type == 'txt':
            return uploaded_file.read().decode('utf-8')
        elif file_type == 'pdf':
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
            except:
                return "Error: Could not extract text from PDF"
        elif file_type == 'docx':
            try:
                import docx
                doc = docx.Document(uploaded_file)
                return '\n'.join([para.text for para in doc.paragraphs])
            except:
                return "Error: Could not extract text from DOCX"
        elif file_type in ['xlsx', 'xls']:
            try:
                import pandas as pd
                df = pd.read_excel(uploaded_file)
                return df.to_string()
            except:
                return "Error: Could not extract text from Excel file"
        elif file_type == 'csv':
            try:
                import pandas as pd
                df = pd.read_csv(uploaded_file)
                return df.to_string()
            except:
                return "Error: Could not extract text from CSV"
        else:
            return "Unsupported file type"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def get_file_icon(filename):
    """Get emoji icon for file type"""
    ext = filename.split('.')[-1].lower()
    icons = {
        'pdf': '📕',
        'docx': '📘',
        'xlsx': '📗',
        'xls': '📗',
        'txt': '📄',
        'csv': '📊'
    }
    return icons.get(ext, '📄')

# ==================== INITIALIZE ====================

# Initialize database
init_db()

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# ==================== LOGIN PAGE ====================

def show_login_page():
    st.markdown("<div style='text-align: center; padding: 2rem;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 3rem;'>🔬</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='color: #1e293b;'>Document Analyzer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b;'>Advanced Text Analysis Platform</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                user = get_user(email, password)
                if user:
                    st.session_state.user = user
                    st.session_state.page = 'home'
                    st.rerun()
                else:
                    st.error("Invalid email or password")
        
        st.info("**Demo Credentials:**\n\nAdmin: admin@demo.com / admin123\n\nUser: user@demo.com / user123")
    
    with tab2:
        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="Enter your name")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Min 6 characters")
            is_admin = st.checkbox("Register as Admin")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                if len(password) < 6:
                    st.error("Password must be at least 6 characters")
                elif create_user(name, email, password, is_admin):
                    st.success("Account created! Please login.")
                else:
                    st.error("Email already registered")

# ==================== MAIN APP ====================

def show_main_app():
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user['name']}")
        st.markdown(f"**{st.session_state.user['email']}**")
        st.markdown("---")
        
        menu_items = [
            ("🏠 Home", "home"),
            ("🧠 Analyze", "analyze"),
            ("📦 Batch", "batch"),
            ("🔌 API", "api"),
            ("📜 History", "history")
        ]
        
        if st.session_state.user['is_admin']:
            menu_items.append(("👑 Admin", "admin"))
        
        for label, page in menu_items:
            if st.button(label, use_container_width=True, key=f"nav_{page}"):
                st.session_state.page = page
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = 'login'
            st.rerun()
    
    # Main content
    if st.session_state.page == 'home':
        show_home_page()
    elif st.session_state.page == 'analyze':
        show_analyze_page()
    elif st.session_state.page == 'batch':
        show_batch_page()
    elif st.session_state.page == 'api':
        show_api_page()
    elif st.session_state.page == 'history':
        show_history_page()
    elif st.session_state.page == 'admin' and st.session_state.user['is_admin']:
        show_admin_page()

# ==================== HOME PAGE ====================

def show_home_page():
    st.markdown(f"# Welcome back, {st.session_state.user['name'].split()[0]}! 👋")
    st.markdown("Here's your analysis dashboard overview")
    
    # Stats
    stats = get_user_stats(st.session_state.user['id'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 My Analyses", stats['total'])
    with col2:
        st.metric("😊 Positive", stats['positive'])
    with col3:
        st.metric("😔 Negative", stats['negative'])
    with col4:
        st.metric("😐 Neutral", stats['neutral'])
    
    # Recent analyses
    st.markdown("---")
    st.markdown("### 📋 Recent Analyses")
    analyses = get_user_analyses(st.session_state.user['id'])[:5]
    
    if not analyses:
        st.info("No analyses yet. Start by analyzing some text!")
    else:
        for analysis in analyses:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{get_file_icon(analysis[2])} {analysis[2]}**")
                    st.caption(datetime.fromisoformat(analysis[18]).strftime('%Y-%m-%d %H:%M:%S'))
                with col2:
                    sentiment_class = ""
                    if analysis[7] and 'Positive' in analysis[7]:
                        sentiment_class = "🟢"
                    elif analysis[7] and 'Negative' in analysis[7]:
                        sentiment_class = "🔴"
                    else:
                        sentiment_class = "🟡"
                    st.markdown(f"{sentiment_class} {analysis[7] or 'N/A'}")
                st.divider()

# ==================== ANALYZE PAGE ====================

def show_analyze_page():
    st.markdown("# 🧠 Text Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Input")
        input_type = st.radio("", ["📝 Enter Text", "📁 Upload File"], horizontal=True, label_visibility="collapsed")
        
        text = ""
        source = "Text Input"
        
        if input_type == "📝 Enter Text":
            text = st.text_area("Enter or paste your text here", height=300, 
                               placeholder="Enter or paste your text here for analysis...")
        else:
            uploaded_file = st.file_uploader("Upload a file", 
                                            type=['pdf', 'docx', 'xlsx', 'xls', 'txt', 'csv'])
            if uploaded_file:
                source = uploaded_file.name
                with st.spinner("Extracting text from file..."):
                    text = extract_text_from_file(uploaded_file)
                    if text:
                        st.success(f"✓ Extracted {len(text.split())} words")
                        with st.expander("Preview extracted text"):
                            st.text(text[:500] + "..." if len(text) > 500 else text)
        
        st.markdown("### Select Analysis Types")
        sentiment = st.checkbox("😊 Sentiment Analysis", value=True)
        entities = st.checkbox("🏷️ Named Entities")
        keywords = st.checkbox("🔑 Keywords")
        language = st.checkbox("🌍 Language Detection")
        emotions = st.checkbox("❤️ Emotion Detection")
        summary = st.checkbox("📄 Summarization")
        
        if st.button("🔬 Run Analysis", use_container_width=True, type="primary"):
            if not text.strip():
                st.error("Please enter text or upload a file")
            else:
                analysis_types = []
                if sentiment: analysis_types.append('sentiment')
                if entities: analysis_types.append('entities')
                if keywords: analysis_types.append('keywords')
                if language: analysis_types.append('language')
                if emotions: analysis_types.append('emotions')
                if summary: analysis_types.append('summary')
                
                if not analysis_types:
                    st.error("Please select at least one analysis type")
                else:
                    with st.spinner("Analyzing text..."):
                        results = {}
                        
                        if 'sentiment' in analysis_types:
                            results['sentiment'] = analyze_sentiment(text)
                        if 'entities' in analysis_types:
                            results['entities'] = extract_entities(text)
                        if 'keywords' in analysis_types:
                            results['keywords'] = extract_keywords(text)
                        if 'language' in analysis_types:
                            results['language'] = detect_language(text)
                        if 'emotions' in analysis_types:
                            results['emotions'] = analyze_emotions(text)
                        if 'summary' in analysis_types:
                            results['summary'] = summarize_text(text)
                        
                        # Save to database
                        save_analysis(st.session_state.user['id'], source, text, analysis_types, results)
                        
                        # Store results in session state
                        st.session_state.analysis_results = results
                        st.session_state.analysis_text = text
                        st.success("✓ Analysis complete!")
                        st.rerun()
    
    with col2:
        st.markdown("### Results")
        
        if 'analysis_results' not in st.session_state:
            st.info("Run an analysis to see results here")
        else:
            results = st.session_state.analysis_results
            text = st.session_state.analysis_text
            
            # Sentiment
            if 'sentiment' in results:
                with st.expander("😊 Sentiment Analysis", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Score", results['sentiment']['score'])
                    with col2:
                        st.metric("Sentiment", results['sentiment']['label'])
                    with col3:
                        st.metric("Confidence", f"{results['sentiment']['confidence']}%")
                    
                    st.progress(int(results['sentiment']['positive']) / 100, text=f"Positive: {results['sentiment']['positive']}%")
                    st.progress(int(results['sentiment']['negative']) / 100, text=f"Negative: {results['sentiment']['negative']}%")
                    st.progress(int(results['sentiment']['neutral']) / 100, text=f"Neutral: {results['sentiment']['neutral']}%")
            
            # Entities
            if 'entities' in results and results['entities']:
                with st.expander("🏷️ Named Entities", expanded=True):
                    entity_colors = {
                        'PERSON': '🔵',
                        'ORGANIZATION': '🟣',
                        'LOCATION': '🟢',
                        'DATE': '🟡',
                        'EMAIL': '🔴',
                        'URL': '🟠'
                    }
                    for entity in results['entities']:
                        icon = entity_colors.get(entity['type'], '⚪')
                        st.markdown(f"{icon} **{entity['text']}** ({entity['type']}) - {entity['confidence']}")
            
            # Keywords
            if 'keywords' in results and results['keywords']:
                with st.expander("🔑 Keywords", expanded=True):
                    for kw in results['keywords']:
                        st.markdown(f"**{kw['text']}** - {kw['relevance']}%")
            
            # Language
            if 'language' in results:
                with st.expander("🌍 Language Detection", expanded=True):
                    st.markdown(f"## {results['language']['flag']} {results['language']['name']}")
                    st.markdown(f"Confidence: **{results['language']['confidence']}%**")
            
            # Emotions
            if 'emotions' in results:
                with st.expander("❤️ Emotion Analysis", expanded=True):
                    emotion_emojis = {
                        'joy': '😊',
                        'sadness': '😢',
                        'anger': '😠',
                        'fear': '😨',
                        'surprise': '😮',
                        'disgust': '🤢'
                    }
                    for emotion, value in results['emotions'].items():
                        st.progress(int(value) / 100, text=f"{emotion_emojis.get(emotion, '😐')} {emotion.title()}: {value}%")
            
            # Summary
            if 'summary' in results:
                with st.expander("📄 Summary", expanded=True):
                    st.info(results['summary']['summary'])
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Original", f"{results['summary']['originalWords']} words")
                    with col2:
                        st.metric("Summary", f"{results['summary']['summaryWords']} words")
                    with col3:
                        reduction = int((1 - results['summary']['summaryWords'] / results['summary']['originalWords']) * 100)
                        st.metric("Reduction", f"{reduction}%")
            
            # Text preview
            with st.expander("📄 Analyzed Text", expanded=True):
                st.text_area("", text[:5000], height=200, disabled=True)

# ==================== BATCH PAGE ====================

def show_batch_page():
    st.markdown("# 📦 Batch Analysis")
    st.markdown("Upload multiple files for bulk analysis")
    
    uploaded_files = st.file_uploader("Upload files", 
                                     type=['pdf', 'docx', 'xlsx', 'xls', 'txt', 'csv'],
                                     accept_multiple_files=True)
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) selected")
        
        if st.button("🔬 Analyze All Files", use_container_width=True, type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_container = st.container()
            
            for idx, file in enumerate(uploaded_files):
                progress = (idx + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                status_text.text(f"Processing {file.name}...")
                
                text = extract_text_from_file(file)
                if text and not text.startswith("Error"):
                    sentiment = analyze_sentiment(text)
                    save_analysis(st.session_state.user['id'], file.name, text, ['sentiment'], {'sentiment': sentiment})
                    
                    with results_container:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{get_file_icon(file.name)} {file.name}**")
                        with col2:
                            st.markdown(f"**{sentiment['label']}** (Score: {sentiment['score']})")
                        st.divider()
            
            status_text.text("✓ All files processed!")
            st.success("Batch analysis complete!")

# ==================== API PAGE ====================

def show_api_page():
    st.markdown("# 🔌 API Documentation")
    st.markdown("Integrate text analysis into your applications")
    
    st.markdown("### Your API Key")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.code(st.session_state.user['api_key'])
    with col2:
        if st.button("🔄 Regenerate", use_container_width=True):
            new_key = regenerate_api_key(st.session_state.user['id'])
            st.session_state.user['api_key'] = new_key
            st.success("API Key regenerated!")
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📍 Endpoint")
    st.code("POST http://localhost:8501/api/v1/analyze")
    
    st.markdown("### 📨 Request Headers")
    st.code("""Content-Type: application/json
Authorization: Bearer YOUR_API_KEY""")
    
    st.markdown("### 📤 Request Body")
    st.code("""{
  "text": "Your text to analyze here...",
  "analyses": ["sentiment", "entities", "keywords", "language", "emotions", "summary"],
  "options": {
    "language": "auto",
    "summaryLength": "short"
  }
}""", language="json")
    
    st.markdown("### 💻 Code Examples")
    
    tab1, tab2, tab3 = st.tabs(["Python", "JavaScript", "cURL"])
    
    with tab1:
        st.code("""import requests

response = requests.post(
    "http://localhost:8501/api/v1/analyze",
    headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    },
    json={
        "text": "Your text here...",
        "analyses": ["sentiment", "entities"]
    }
)

result = response.json()
print(result)""", language="python")
    
    with tab2:
        st.code("""fetch('http://localhost:8501/api/v1/analyze', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer YOUR_API_KEY',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        text: 'Your text here...',
        analyses: ['sentiment', 'entities']
    })
})
.then(res => res.json())
.then(data => console.log(data));""", language="javascript")
    
    with tab3:
        st.code("""curl -X POST http://localhost:8501/api/v1/analyze \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Your text here...", "analyses": ["sentiment", "entities"]}'""", language="bash")

# ==================== HISTORY PAGE ====================

def show_history_page():
    st.markdown("# 📜 Your Analysis History")
    
    analyses = get_user_analyses(st.session_state.user['id'])
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"Showing {len(analyses)} analysis record(s) for {st.session_state.user['name']}")
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            clear_user_analyses(st.session_state.user['id'])
            st.success("History cleared!")
            st.rerun()
    
    st.info("ℹ️ You can only view your own analysis history. Admins can see all users' data in the Admin Dashboard.")
    
    st.markdown("---")
    
    if not analyses:
        st.info("No analysis history yet.")
    else:
        for analysis in analyses:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                with col1:
                    st.markdown(f"**{get_file_icon(analysis[2])} {analysis[2]}**")
                    st.caption(datetime.fromisoformat(analysis[18]).strftime('%Y-%m-%d %H:%M:%S'))
                with col2:
                    st.markdown(f"**Types:** {analysis[5]}")
                with col3:
                    sentiment_emoji = ""
                    if analysis[7] and 'Positive' in analysis[7]:
                        sentiment_emoji = "😊"
                    elif analysis[7] and 'Negative' in analysis[7]:
                        sentiment_emoji = "😔"
                    else:
                        sentiment_emoji = "😐"
                    st.markdown(f"{sentiment_emoji} **{analysis[7] or 'N/A'}**")
                with col4:
                    st.markdown(f"**{analysis[4]} words**")
                st.divider()

# ==================== ADMIN PAGE ====================

def show_admin_page():
    st.markdown("# 👑 Admin Dashboard")
    
    stats = get_admin_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Users", stats['totalUsers'])
    with col2:
        st.metric("📊 Total Analyses", stats['totalAnalyses'])
    with col3:
        st.metric("😊 Positive Results", stats['positive'])
    with col4:
        st.metric("😔 Negative Results", stats['negative'])
    
    st.markdown("---")
    st.markdown("### All User Analyses")
    st.caption("Complete analysis history from all users (SQL Database)")
    
    if st.button("🔄 Refresh Data", use_container_width=False):
        st.rerun()
    
    analyses = get_all_analyses()
    
    if not analyses:
        st.info("No analyses yet. Users will appear here once they start analyzing.")
    else:
        # Create a table
        for analysis in analyses:
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 2])
                with col1:
                    st.markdown(f"**👤 {analysis[20]}**")
                    st.caption(analysis[21])
                with col2:
                    st.markdown(f"{get_file_icon(analysis[2])} {analysis[2]}")
                with col3:
                    st.caption(analysis[5])
                with col4:
                    sentiment_emoji = ""
                    if analysis[7] and 'Positive' in analysis[7]:
                        sentiment_emoji = "😊"
                    elif analysis[7] and 'Negative' in analysis[7]:
                        sentiment_emoji = "😔"
                    else:
                        sentiment_emoji = "😐"
                    st.markdown(f"{sentiment_emoji}")
                with col5:
                    st.markdown(f"{analysis[4]} words")
                with col6:
                    st.caption(datetime.fromisoformat(analysis[18]).strftime('%Y-%m-%d %H:%M'))
                st.divider()

# ==================== MAIN ====================

if __name__ == "__main__":
    if st.session_state.user is None:
        show_login_page()
    else:
        show_main_app()
