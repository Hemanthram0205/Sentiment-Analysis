# 🧠 Document Sentiment Analysis App  

🔗 **Live Demo:** [Try it here → Sentiment Analysis Streamlit App](https://sentimentanalysis18.streamlit.app/)  

---

## 📄 Overview  

**Document Sentiment Analysis App** is a Streamlit-based web application that performs **sentiment analysis** on uploaded PDF or Word (`.docx`) documents.  
It extracts text automatically, analyzes the tone using Natural Language Processing (NLP) techniques, and classifies the content as **Positive**, **Negative**, or **Neutral**.  

---

## 🎯 Features  

✅ **File Upload Support** — Upload `.pdf` or `.docx` files directly through the browser.  
⚙️ **Automatic Text Extraction** — Uses `pdfplumber` for PDFs and `python-docx` for Word files.  
🧮 **Sentiment Computation** — Calculates polarity score using `TextBlob` (range: -1 to +1).  
💬 **Live Results** — Displays text preview and real-time sentiment classification.  
🌐 **Streamlit Cloud Ready** — Works both locally and in the cloud with a smooth UI.  

---

## ⚙️ How It Works  

1. Upload a document (`.pdf` or `.docx`) through the Streamlit interface.  
2. The app extracts text content using:  
   - `pdfplumber` → for PDF documents  
   - `python-docx` → for Word files  
3. `TextBlob` performs sentiment analysis to compute:  
   - **Sentiment Score:** from `-1` (negative) to `+1` (positive)  
   - **Overall Category:** *Positive*, *Neutral*, or *Negative*  
4. Results are displayed instantly on the dashboard.  

---

## 🧰 Tech Stack  

| Component | Technology Used |
|------------|-----------------|
| **Language** | Python |
| **Framework** | Streamlit |
| **NLP Library** | TextBlob |
| **File Processing** | pdfplumber, python-docx |
| **Deployment** | Streamlit Cloud |

---

