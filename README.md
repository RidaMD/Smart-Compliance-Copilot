# Smart Compliance Copilot

An AI-powered compliance analysis system that extracts clauses from documents, evaluates risk levels using AWS NLP services, generates intelligent summaries, and produces automated PDF risk reports.

Built as a backend system demonstrating NLP integration, document intelligence, and automated compliance risk scoring.

---

## Problem Statement

Compliance documents are long, complex, and difficult to manually analyze.  
Organizations face risk due to overlooked clauses, penalties, and ambiguous terms.

Smart Compliance Copilot automates:

- Clause extraction  
- Risk detection  
- Sentiment analysis  
- AI summarization  
- Automated report generation  

---

## Key Features

- PDF & text file processing  
- Clause-based parsing using regex  
- Risk classification (High / Medium / Low)  
- Sentiment & entity detection using AWS Comprehend  
- AI-powered summarization using AWS Bedrock (Titan model)  
- Risk distribution pie chart (Matplotlib)  
- Structured PDF compliance report (ReportLab)  
- OCR fallback using Tesseract if text extraction fails  

---

## Tech Stack

### Backend
- Flask (Python)

### Cloud & AI
- AWS Comprehend  
- AWS Bedrock (Titan Text Express)  
- AWS Textract  

### Document Processing
- PyMuPDF  
- Tesseract OCR  

### Visualization & Reporting
- Matplotlib  
- ReportLab  

---

## System Architecture

User Upload  
↓  
Text Extraction (PyMuPDF → OCR fallback)  
↓  
Clause Parsing (Regex-based detection)  
↓  
Risk Analysis  
• Keyword-based rule engine  
• Sentiment analysis (Comprehend)  
• Entity detection  
↓  
AI Summary Generation (Bedrock)  
↓  
Risk Chart Generation  
↓  
Automated PDF Report Export  

---

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/RidaMD/Smart-Compliance-Copilot.git
cd Smart-Compliance-Copilot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

This project requires valid AWS credentials.

Run:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-west-2
```

⚠️ Never commit AWS keys to GitHub.

---

## Run the Application

```bash
python backend.py
```

Server runs at:

```
http://localhost:5000
```

---

## API Endpoints

### POST /process
Processes uploaded document and returns:
- Summary  
- Clause-based risk analysis  
- Risk counts  
- Base64 pie chart  

### POST /download_report
Generates structured PDF compliance report.

---

## Security Considerations

- AWS credentials handled via environment variables  
- No hardcoded secrets in source code  
- Temporary files securely deleted after processing  

---

## Future Improvements

- Frontend dashboard (React-based UI)  
- Authentication & user accounts  
- Cloud deployment (Docker + AWS EC2)  
- ML-based risk scoring instead of keyword-based rules  
- Multi-language document support  
