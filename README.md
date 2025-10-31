# 🧠 Document Sentiment Analysis App

🔗 Live Demo
Try it here → [Sentiment Analysis Streamlit App](https://sentimentanalysis18.streamlit.app/)



📄 Overview
This Streamlit-based application performs sentiment analysis on uploaded PDF or Word (.docx) documents.  
It extracts text from the uploaded file, analyzes the overall tone using NLP techniques, and classifies it as Positive, Negative, or Neutral.



🎯 Features
- 📁 Upload `.pdf` or `.docx` files directly from the browser.  
- ⚙️ Automatically extracts and processes text.  
- 🧮 Computes a sentiment polarity score and sentiment category.  
- 💬 Displays a text preview and live sentiment results on the app interface.  
- 🌐 Works locally or deployed online via Streamlit Cloud.  



⚙️ How It Works
1. Upload your document through the Streamlit web interface.  
2. The app extracts text using `pdfplumber` for PDFs or `python-docx` for Word files.  
3. TextBlob calculates the sentiment polarity of the extracted text.  
4. Results include:
   - Sentiment Score (range: -1 to +1)  
   - Overall Sentiment Category (Positive / Neutral / Negative)



🧰 Tech Stack
- Language: Python  
- Framework: Streamlit  
- Libraries: `textblob`, `pdfplumber`, `python-docx`  
- Deployment: Streamlit Cloud  
