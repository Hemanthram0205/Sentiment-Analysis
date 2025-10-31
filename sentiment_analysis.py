import fitz  # PyMuPDF for PDF reading
from docx import Document
from textblob import TextBlob
import tkinter as tk
from tkinter import filedialog

# Function to read .docx files
def read_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])  # Extract non-empty lines
    return text

# Function to read .pdf files
def read_pdf(file_path):
    doc = fitz.open(file_path)
    text = "\n".join([page.get_text("text") for page in doc if page.get_text("text").strip()])  # Extract non-empty lines
    return text

# Function for sentiment analysis (entire document)
def get_sentiment(text):
    sentiment_score = TextBlob(text).sentiment.polarity
    if sentiment_score > 0.2:
        sentiment_category = "Positive"
    elif sentiment_score < -0.2:
        sentiment_category = "Negative"
    else:
        sentiment_category = "Neutral"
    return sentiment_score, sentiment_category

# Open file dialog to select file
root = tk.Tk()
root.withdraw()  # Hide the root window
file_path = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx"), ("PDF Files", "*.pdf")])

if not file_path:
    print("No file selected. Exiting.")
    exit()

# Determine file type and extract text
if file_path.endswith(".docx"):
    text_data = read_docx(file_path)
elif file_path.endswith(".pdf"):
    text_data = read_pdf(file_path)
else:
    print("Unsupported file format.")
    exit()

# Perform sentiment analysis on the entire document
sentiment_score, sentiment_category = get_sentiment(text_data)

# Print results in console
print("\nSentiment Analysis Results for the Entire Document:")
print(f"Sentiment Score: {sentiment_score:.6f}")
print(f"Sentiment Category: {sentiment_category}")
