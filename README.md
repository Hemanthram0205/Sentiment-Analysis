🧠 Document Analyzer – Advanced Text & Sentiment Analysis Platform

🔗 Live Demo (Streamlit):
(Add your Streamlit Cloud link here if deployed)

📄 Overview

Document Analyzer is a comprehensive Streamlit-based web application designed for document-level text analysis and sentiment evaluation.
The platform allows users to upload documents or input text, automatically extracts content, and performs multiple Natural Language Processing (NLP) tasks including sentiment analysis, entity extraction, keyword identification, language detection, emotion analysis, and summarization.

Unlike basic sentiment apps, this system includes user authentication, role-based dashboards (Admin/User), persistent storage using SQLite, batch processing, and API-style integration concepts, making it suitable for academic projects, demos, and analytics prototypes.

🎯 Key Features
📁 Input Support

✅ Text input via browser
✅ File uploads:

PDF

DOCX

TXT

CSV

XLS / XLSX

🧠 NLP & Text Analysis

😊 Sentiment Analysis — Positive / Negative / Neutral classification
🏷️ Named Entity Recognition — People, Organizations, Locations, Emails, URLs
🔑 Keyword Extraction — Frequency-based relevance scoring
🌍 Language Detection — Auto-detects supported languages
❤️ Emotion Analysis — Joy, Sadness, Anger, Fear, Surprise, Disgust
📄 Text Summarization — Automatic condensed summaries

👤 User & Admin System

🔐 Secure login & registration
🔑 Password hashing (SHA-256)
👑 Role-based access:

User: Personal dashboard & history

Admin: System-wide analytics & monitoring
📊 Persistent analysis history (SQLite database)
🔄 API key generation & regeneration

📊 Dashboards

User sentiment statistics overview

Recent analysis history

Admin dashboard with:

Total users

Total analyses

Global sentiment distribution

⚙️ How It Works

User Authentication

Users log in or register via the Streamlit interface.

Demo accounts are auto-created on first run.

Text Input / File Upload

Users can paste text or upload documents.

Supported files are automatically parsed and converted into plain text.

Analysis Selection

Users select one or more analysis types (sentiment, entities, keywords, etc.).

NLP Processing

Rule-based NLP logic processes the text.

Sentiment scores and classifications are computed.

Additional insights (entities, emotions, summary) are generated.

Results & Storage

Results are displayed instantly on the dashboard.

All analyses are saved in an SQLite database for later access.

🧮 Sentiment Analysis Logic

Polarity-based scoring using curated positive & negative word dictionaries

Score normalization and confidence calculation

Classification rules:

Positive 😊

Neutral 😐

Negative 😔

This lightweight, rule-based approach ensures fast execution without heavy ML models, ideal for demonstrations and coursework.

🧰 Tech Stack
Component	Technology
Language	Python
Framework	Streamlit
Database	SQLite
NLP Approach	Rule-based NLP
File Processing	PyPDF2, python-docx, pandas, openpyxl
UI Styling	Custom CSS (Inter font)
Deployment	Streamlit Cloud / Local
🚀 Installation & Usage
1️⃣ Install Dependencies
pip install streamlit pandas PyPDF2 python-docx openpyxl mammoth

2️⃣ Run the Application
streamlit run app.py

3️⃣ Open in Browser
http://localhost:8501

🔑 Demo Credentials
Role	Email	Password
Admin	admin@demo.com
	admin123
User	user@demo.com
	user123

These accounts are automatically created when the app runs for the first time.

🗄️ Database

SQLite database: document_analyzer.db

Automatically initialized on first run

Stores:

User accounts

API keys

Analysis metadata

Sentiment & NLP results

🌐 Deployment

Fully compatible with Streamlit Cloud

Works locally and in hosted environments

No external backend required

🎯 Use Cases

Academic NLP projects

Sentiment analysis of documents

Business analytics demos

Text intelligence prototypes

NLP coursework & capstone projects

📌 Notes

This is a pure Streamlit application (no Flask backend).

Designed for educational and demonstration purposes.

Uses lightweight NLP logic instead of heavy ML models for speed and clarity.

📄 License

This project is intended for learning, academic, and demonstration use.
You are free to modify and extend it.
