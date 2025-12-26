"""
Document Analyzer - Advanced Text Analysis Platform
Flask Backend with SQLAlchemy Database

To run this application:
1. Install dependencies: pip install flask flask-sqlalchemy flask-cors werkzeug PyJWT textblob
2. Run the app: python app.py
3. Open http://localhost:5000 in your browser

Database: SQLite (Document Analyzer.db) - automatically created on first run
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import uuid
import os
import re
from functools import wraps

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production-' + str(uuid.uuid4())
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Document Analyzer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to analyses
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'isAdmin': self.is_admin,
            'apiKey': self.api_key,
            'createdAt': self.created_at.isoformat()
        }
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Analysis(db.Model):
    """Analysis model for storing text analysis results"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source = db.Column(db.String(255), nullable=False)  # filename or "Text Input"
    text_preview = db.Column(db.Text)  # First 500 chars of analyzed text
    word_count = db.Column(db.Integer, default=0)
    
    # Analysis types performed
    analysis_types = db.Column(db.String(255))  # comma-separated list
    
    # Sentiment results
    sentiment_score = db.Column(db.Float)
    sentiment_label = db.Column(db.String(50))
    sentiment_positive = db.Column(db.Float)
    sentiment_negative = db.Column(db.Float)
    sentiment_neutral = db.Column(db.Float)
    
    # Language detection
    language_code = db.Column(db.String(10))
    language_name = db.Column(db.String(50))
    language_confidence = db.Column(db.Float)
    
    # Emotions (stored as JSON string)
    emotions_json = db.Column(db.Text)
    
    # Entities (stored as JSON string)
    entities_json = db.Column(db.Text)
    
    # Keywords (stored as JSON string)
    keywords_json = db.Column(db.Text)
    
    # Summary
    summary_text = db.Column(db.Text)
    summary_words = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'userName': self.user.name if self.user else 'Unknown',
            'userEmail': self.user.email if self.user else 'Unknown',
            'source': self.source,
            'textPreview': self.text_preview,
            'wordCount': self.word_count,
            'types': self.analysis_types,
            'sentiment': self.sentiment_label,
            'sentimentScore': self.sentiment_score,
            'sentimentPositive': self.sentiment_positive,
            'sentimentNegative': self.sentiment_negative,
            'sentimentNeutral': self.sentiment_neutral,
            'languageCode': self.language_code,
            'languageName': self.language_name,
            'languageConfidence': self.language_confidence,
            'emotions': self.emotions_json,
            'entities': self.entities_json,
            'keywords': self.keywords_json,
            'summary': self.summary_text,
            'summaryWords': self.summary_words,
            'date': self.created_at.isoformat()
        }


# ==================== HELPER FUNCTIONS ====================

def generate_api_key():
    """Generate a unique API key"""
    return str(uuid.uuid4())


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'success': False, 'message': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def api_key_required(f):
    """Decorator to require valid API key"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = None
        
        # Get API key from header
        if 'X-API-Key' in request.headers:
            api_key = request.headers['X-API-Key']
        elif 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                api_key = auth_header[7:]
        
        if not api_key:
            return jsonify({'success': False, 'message': 'API key is missing'}), 401
        
        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({'success': False, 'message': 'Invalid API key'}), 401
        
        return f(user, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated


# ==================== TEXT ANALYSIS FUNCTIONS ====================

# Word lists for sentiment analysis
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
    'en': {'name': 'English', 'words': ['the', 'is', 'are', 'was', 'were', 'have', 'has', 'been', 'being', 'and', 'or', 'but', 'with', 'for', 'that', 'this']},
    'es': {'name': 'Spanish', 'words': ['el', 'la', 'los', 'las', 'de', 'en', 'que', 'es', 'por', 'con', 'para', 'como', 'pero', 'más', 'este', 'esta']},
    'fr': {'name': 'French', 'words': ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'est', 'que', 'qui', 'dans', 'pour', 'pas', 'sur', 'avec', 'plus']},
    'de': {'name': 'German', 'words': ['der', 'die', 'das', 'und', 'ist', 'von', 'mit', 'für', 'auf', 'nicht', 'auch', 'als', 'eine', 'aber', 'oder']},
    'it': {'name': 'Italian', 'words': ['il', 'la', 'di', 'che', 'non', 'per', 'una', 'sono', 'con', 'come', 'anche', 'più', 'del', 'della']},
    'pt': {'name': 'Portuguese', 'words': ['o', 'a', 'os', 'as', 'de', 'que', 'em', 'para', 'com', 'não', 'uma', 'por', 'mais', 'como']},
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
        entities.append({'text': p, 'type': 'PERSON', 'confidence': round(0.7 + 0.25 * uuid.uuid4().int % 100 / 100, 2)})
    
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
    detected = {'code': 'en', 'name': 'English'}
    
    for code, lang in LANGUAGE_PATTERNS.items():
        score = sum(1 for w in lang['words'] if w in words)
        if score > max_score:
            max_score = score
            detected = {'code': code, 'name': lang['name']}
    
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


# ==================== ROUTES ====================

# Serve the frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')


# ==================== AUTH ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate input
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Name, email and password are required'}), 400
    
    if len(data['password']) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    # Create new user
    user = User(
        name=data['name'],
        email=data['email'],
        is_admin=data.get('isAdmin', False),
        api_key=generate_api_key()
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Account created successfully',
        'user': user.to_dict()
    })


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    })


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current logged in user"""
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    })


@app.route('/api/auth/regenerate-api-key', methods=['POST'])
@token_required
def regenerate_api_key(current_user):
    """Regenerate user's API key"""
    current_user.api_key = generate_api_key()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'apiKey': current_user.api_key
    })


# ==================== ANALYSIS ROUTES ====================

@app.route('/api/analyze', methods=['POST'])
@token_required
def analyze_text(current_user):
    """Analyze text and save results"""
    data = request.get_json()
    
    if not data.get('text'):
        return jsonify({'success': False, 'message': 'Text is required'}), 400
    
    text = data['text']
    source = data.get('source', 'Text Input')
    analysis_types = data.get('types', ['sentiment'])
    
    results = {}
    
    # Perform requested analyses
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
    
    # Save analysis to database
    analysis = Analysis(
        user_id=current_user.id,
        source=source,
        text_preview=text[:500],
        word_count=len(text.split()),
        analysis_types=', '.join(analysis_types),
        sentiment_score=results.get('sentiment', {}).get('score'),
        sentiment_label=results.get('sentiment', {}).get('label'),
        sentiment_positive=results.get('sentiment', {}).get('positive'),
        sentiment_negative=results.get('sentiment', {}).get('negative'),
        sentiment_neutral=results.get('sentiment', {}).get('neutral'),
        language_code=results.get('language', {}).get('code'),
        language_name=results.get('language', {}).get('name'),
        language_confidence=results.get('language', {}).get('confidence'),
        emotions_json=str(results.get('emotions', {})),
        entities_json=str(results.get('entities', [])),
        keywords_json=str(results.get('keywords', [])),
        summary_text=results.get('summary', {}).get('summary'),
        summary_words=results.get('summary', {}).get('summaryWords')
    )
    
    db.session.add(analysis)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'results': results,
        'analysis': analysis.to_dict()
    })


@app.route('/api/analyses', methods=['GET'])
@token_required
def get_user_analyses(current_user):
    """Get all analyses for current user"""
    analyses = Analysis.query.filter_by(user_id=current_user.id)\
        .order_by(Analysis.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'analyses': [a.to_dict() for a in analyses]
    })


@app.route('/api/analyses/stats', methods=['GET'])
@token_required
def get_user_stats(current_user):
    """Get analysis statistics for current user"""
    analyses = Analysis.query.filter_by(user_id=current_user.id).all()
    
    total = len(analyses)
    positive = sum(1 for a in analyses if a.sentiment_label and 'Positive' in a.sentiment_label)
    negative = sum(1 for a in analyses if a.sentiment_label and 'Negative' in a.sentiment_label)
    neutral = sum(1 for a in analyses if a.sentiment_label and 'Neutral' in a.sentiment_label)
    
    return jsonify({
        'success': True,
        'stats': {
            'total': total,
            'positive': positive,
            'negative': negative,
            'neutral': neutral
        }
    })


@app.route('/api/analyses/<int:analysis_id>', methods=['DELETE'])
@token_required
def delete_analysis(current_user, analysis_id):
    """Delete a specific analysis"""
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
    
    if not analysis:
        return jsonify({'success': False, 'message': 'Analysis not found'}), 404
    
    db.session.delete(analysis)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Analysis deleted'})


@app.route('/api/analyses/clear', methods=['DELETE'])
@token_required
def clear_user_analyses(current_user):
    """Clear all analyses for current user"""
    Analysis.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'All analyses cleared'})


# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/stats', methods=['GET'])
@token_required
@admin_required
def get_admin_stats(current_user):
    """Get admin dashboard statistics"""
    total_users = User.query.count()
    total_analyses = Analysis.query.count()
    
    analyses = Analysis.query.all()
    positive = sum(1 for a in analyses if a.sentiment_label and 'Positive' in a.sentiment_label)
    negative = sum(1 for a in analyses if a.sentiment_label and 'Negative' in a.sentiment_label)
    
    return jsonify({
        'success': True,
        'stats': {
            'totalUsers': total_users,
            'totalAnalyses': total_analyses,
            'positive': positive,
            'negative': negative
        }
    })


@app.route('/api/admin/analyses', methods=['GET'])
@token_required
@admin_required
def get_all_analyses(current_user):
    """Get all analyses (admin only)"""
    analyses = Analysis.query.order_by(Analysis.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'analyses': [a.to_dict() for a in analyses]
    })


@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    """Get all users (admin only)"""
    users = User.query.order_by(User.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'users': [u.to_dict() for u in users]
    })


# ==================== PUBLIC API ROUTES ====================

@app.route('/api/v1/analyze', methods=['POST'])
@api_key_required
def public_api_analyze(user):
    """Public API endpoint for text analysis"""
    data = request.get_json()
    
    if not data.get('text'):
        return jsonify({'success': False, 'error': 'Text is required'}), 400
    
    text = data['text']
    analyses = data.get('analyses', ['sentiment'])
    
    results = {}
    
    if 'sentiment' in analyses:
        results['sentiment'] = analyze_sentiment(text)
    
    if 'entities' in analyses:
        results['entities'] = extract_entities(text)
    
    if 'keywords' in analyses:
        results['keywords'] = extract_keywords(text)
    
    if 'language' in analyses:
        results['language'] = detect_language(text)
    
    if 'emotions' in analyses:
        results['emotions'] = analyze_emotions(text)
    
    if 'summary' in analyses:
        results['summary'] = summarize_text(text)
    
    # Save to database
    analysis = Analysis(
        user_id=user.id,
        source='API Request',
        text_preview=text[:500],
        word_count=len(text.split()),
        analysis_types=', '.join(analyses),
        sentiment_score=results.get('sentiment', {}).get('score'),
        sentiment_label=results.get('sentiment', {}).get('label'),
        sentiment_positive=results.get('sentiment', {}).get('positive'),
        sentiment_negative=results.get('sentiment', {}).get('negative'),
        sentiment_neutral=results.get('sentiment', {}).get('neutral'),
        language_code=results.get('language', {}).get('code'),
        language_name=results.get('language', {}).get('name'),
        language_confidence=results.get('language', {}).get('confidence'),
        emotions_json=str(results.get('emotions', {})),
        entities_json=str(results.get('entities', [])),
        keywords_json=str(results.get('keywords', [])),
        summary_text=results.get('summary', {}).get('summary'),
        summary_words=results.get('summary', {}).get('summaryWords')
    )
    
    db.session.add(analysis)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': results
    })


# ==================== DATABASE INITIALIZATION ====================

def init_db():
    """Initialize database and create demo accounts"""
    with app.app_context():
        db.create_all()
        
        # Create demo accounts if they don't exist
        if not User.query.filter_by(email='admin@demo.com').first():
            admin = User(
                name='Admin User',
                email='admin@demo.com',
                is_admin=True,
                api_key='admin-' + generate_api_key()
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        if not User.query.filter_by(email='user@demo.com').first():
            user = User(
                name='Regular User',
                email='user@demo.com',
                is_admin=False,
                api_key='user-' + generate_api_key()
            )
            user.set_password('user123')
            db.session.add(user)
        
        db.session.commit()
        print("Database initialized with demo accounts!")
        print("Admin: admin@demo.com / admin123")
        print("User: user@demo.com / user123")


# ==================== MAIN ====================

if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("Document Analyzer - Advanced Text Analysis Platform")
    print("="*50)
    print("Server running at: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
