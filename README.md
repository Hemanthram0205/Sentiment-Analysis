🧠 Document Analyzer – Advanced Text & Sentiment Analysis Platform

🔗 Live Demo:
(Add your Streamlit Cloud link here)

📄 Overview

Document Analyzer is a Streamlit-based web application for performing advanced text and document analysis using Natural Language Processing (NLP) techniques.

The application supports text input and document uploads, automatically extracts content, performs sentiment analysis, and provides additional insights such as named entities, keywords, language detection, emotion analysis, and text summarization.

This project is designed for academic use, NLP demonstrations, analytics prototypes, and capstone projects.

🎯 Key Features
📁 Input Capabilities
Feature	Supported
Text Input	✅ Yes
PDF Files	✅ Yes
DOCX Files	✅ Yes
TXT Files	✅ Yes
CSV Files	✅ Yes
Excel (XLS / XLSX)	✅ Yes
🧠 NLP & Analysis Modules
Analysis Type	Description
Sentiment Analysis	Classifies text as Positive, Negative, or Neutral
Named Entity Recognition	Extracts People, Organizations, Locations, Emails, URLs
Keyword Extraction	Identifies high-relevance keywords
Language Detection	Auto-detects document language
Emotion Analysis	Detects Joy, Sadness, Anger, Fear, Surprise, Disgust
Text Summarization	Generates a concise summary
👤 User & Admin Features
Feature	User	Admin
Login / Register	✅	✅
Sentiment Analysis	✅	✅
Analysis History	✅	✅ (All Users)
Dashboard Stats	✅	✅ (Global)
API Key Access	✅	✅
User Monitoring	❌	✅
⚙️ How the Application Works

1️⃣ User Authentication

Secure login and registration

Password hashing using SHA-256

2️⃣ Text Input or File Upload

Upload supported documents or paste text

3️⃣ Analysis Selection

Choose one or more NLP tasks

4️⃣ Processing Engine

Rule-based NLP logic analyzes the content

Sentiment scores and insights are generated

5️⃣ Results & Storage

Results displayed instantly

All analyses stored in SQLite database

🧮 Sentiment Analysis Logic
Component	Details
Approach	Rule-based NLP
Score Range	−1.0 to +1.0
Output Labels	Positive 😊 / Neutral 😐 / Negative 😔
Confidence	Percentage-based

✔ Lightweight
✔ Fast execution
✔ No heavy ML models

🧰 Tech Stack
Layer	Technology
Language	Python
Framework	Streamlit
Database	SQLite
NLP Method	Rule-based
File Parsing	PyPDF2, python-docx, pandas
Styling	Custom CSS (Inter Font)
Deployment	Streamlit Cloud / Local
🚀 Installation & Setup
1️⃣ Install Dependencies
pip install streamlit pandas PyPDF2 python-docx openpyxl mammoth

2️⃣ Run the Application
streamlit run app.py

3️⃣ Access in Browser
http://localhost:8501

🔑 Demo Credentials
Role	Email	Password
Admin	admin@demo.com
	admin123
User	user@demo.com
	user123

📌 Demo accounts are automatically created on first run.

🗄️ Database Information
Item	Details
Database Type	SQLite
File Name	document_analyzer.db
Initialization	Automatic
Stored Data	Users, Analyses, NLP Results
🌐 Deployment
Platform	Supported
Local Machine	✅
Streamlit Cloud	✅
External Backend	❌ Not Required
🎯 Use Cases

Academic NLP Projects

Sentiment Analysis of Documents

Text Analytics Demonstrations

Business Analytics Prototypes

Final Year / Capstone Projects

📌 Important Notes

This is a pure Streamlit application

No Flask or external backend is used

Optimized for education and demonstration

Designed for clarity, performance, and usability

📄 License

This project is released for educational and academic use.
You are free to modify, extend, and reuse it with proper attribution.
