# Smart-Compliance-Copilot
📄 Smart Compliance Copilot

An AI-powered compliance analysis system that extracts clauses from documents, evaluates risk levels using AWS NLP services, generates intelligent summaries, and produces automated PDF risk reports.

🚀 Problem Statement

Compliance documents are long, complex, and difficult to manually analyze.
Organizations face risk due to overlooked clauses, penalties, and ambiguous terms.

Smart Compliance Copilot automates:

Clause extraction
Risk detection
Sentiment analysis
AI summarization
Report generation

🛠 Key Features

📑 PDF & text file processing
🔎 Clause-based parsing using regex
⚠️ Risk classification (High / Medium / Low)
🧠 Sentiment & entity detection using AWS Comprehend
✨ AI-powered summarization using AWS Bedrock (Titan model)
📊 Risk distribution pie chart (Matplotlib)
📄 Structured PDF compliance report (ReportLab)
🔁 OCR fallback using Tesseract if text extraction fails

🧰 Tech Stack

Backend:
Python
Flask

Cloud & AI:
AWS Comprehend
AWS Bedrock (Titan Text Express)
AWS Textract (client initialized)

Document Processing:
PyMuPDF
Tesseract OCR

Visualization & Reporting:
Matplotlib
ReportLab

🏗 System Architecture

User Upload
⬇
Text Extraction (PyMuPDF → OCR fallback)
⬇
Clause Parsing (Regex-based detection)
⬇
Risk Analysis
• Keyword-based rule engine
• Sentiment analysis (Comprehend)
• Entity detection
⬇
AI Summary Generation (Bedrock)
⬇
Risk Chart Generation
⬇
Automated PDF Report Export

⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/RidaMD/Smart-Compliance-Copilot.git
cd Smart-Compliance-Copilot
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Configure AWS Credentials

This project requires valid AWS credentials.

Run:

aws configure

Or set environment variables:

export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-west-2

⚠️ Never commit AWS keys to GitHub.

▶️ Run the Application
python backend.py

Server runs at:

http://localhost:5000
📄 API Endpoints

POST /process
Processes uploaded document and returns:

Summary

Clause-based risk analysis

Risk counts

Base64 pie chart

POST /download_report
Generates structured PDF compliance report.

🧠 Engineering Decisions

Implemented fallback text extraction (PDF text → OCR)
Combined rule-based keyword detection with AWS NLP services
Encoded chart images in base64 for frontend transfer
Used structured PDF generation with tables and dynamic pagination

🔐 Security Considerations

AWS credentials handled via environment variables
No hardcoded secrets in source code
Temporary file cleanup using secure directory deletion

📈 Future Improvements

Frontend dashboard (React-based UI)
Authentication & user accounts
Cloud deployment (Docker + AWS EC2)
ML-based risk scoring instead of keyword-based rules
Multi-language document support
