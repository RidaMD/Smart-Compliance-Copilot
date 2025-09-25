# backend.py
import os, io, tempfile, base64, shutil, json, re, traceback
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

import boto3
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import datetime

app = Flask(__name__)
CORS(app)

AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
boto_kwargs = {"region_name": AWS_REGION}
textract = boto3.client("textract", **boto_kwargs)
comprehend = boto3.client("comprehend", **boto_kwargs)
bedrock = boto3.client("bedrock-runtime", **boto_kwargs)

# ==================== TEXT EXTRACTION ====================
def extract_text_with_pymupdf(file_path):
    try:
        doc = fitz.open(file_path)
        text = "\n".join([p.get_text("text") for p in doc])
        return text.strip()
    except:
        return ""

def extract_text_with_tesseract_from_pdf(file_path):
    text = []
    try:
        doc = fitz.open(file_path)
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            mode = "RGB" if pix.n < 4 else "RGBA"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            text.append(pytesseract.image_to_string(img))
        return "\n".join(text).strip()
    except:
        return ""

def extract_text_from_file(file_path, ext):
    ext = ext.lower()
    if ext == "pdf":
        text = extract_text_with_pymupdf(file_path)
        if not text:
            text = extract_text_with_tesseract_from_pdf(file_path)
        return text
    else:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except:
            return ""

# ==================== CLAUSE PARSING ====================
def split_into_clauses(text):
    clauses = []
    current_number = None
    buffer = []
    for line in text.splitlines():
        match = re.match(r"^(\d+(\.\d+)+)\s", line.strip())
        if match:
            if current_number and buffer:
                clauses.append((current_number, " ".join(buffer).strip()))
            current_number = match.group(1)
            buffer = [line.strip()]
        else:
            if line.strip():
                buffer.append(line.strip())
    if current_number and buffer:
        clauses.append((current_number, " ".join(buffer).strip()))
    return clauses

# ==================== RISK ANALYSIS ====================
def analyze_clause(clause_text):
    try:
        sentiment = comprehend.detect_sentiment(Text=clause_text, LanguageCode="en")
        entities_resp = comprehend.detect_entities(Text=clause_text, LanguageCode="en")
        entities = [e["Text"].lower() for e in entities_resp.get("Entities", [])]

        risk = "Low"
        reason = "Neutral clause"

        lowered = clause_text.lower()
        high_keywords = ["penalty", "fine", "breach", "liability", "indemnify",
                         "waive", "forfeit", "retroactive", "termination", "charge"]
        if any(k in lowered for k in high_keywords):
            risk = "High"
            reason = "Contains high-risk keywords"
        elif sentiment.get("Sentiment") in ("NEGATIVE", "MIXED"):
            risk = "Medium"
            reason = f"Negative tone ({sentiment.get('Sentiment')})"

        if any(e in lowered for e in entities):
            risk = "High"
            reason += "; flagged entity"

        return {"clause": clause_text, "risk_level": risk, "reason": reason}
    except:
        return {"clause": clause_text, "risk_level": "Unknown", "reason": "Error"}

def analyze_clauses(clauses):
    results = []
    for num, text in clauses:
        res = analyze_clause(text)
        res["clause_number"] = num
        results.append(res)
    return results

# ==================== PIE CHART ====================
def render_pie_base64(risk_list):
    counts = {"High": 0, "Medium": 0, "Low": 0}
    for r in risk_list:
        lvl = r.get("risk_level", "Low")
        if lvl in counts:
            counts[lvl] += 1
    if sum(counts.values()) == 0:
        return None, counts
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(counts.values(), labels=counts.keys(), autopct="%1.1f%%")
    ax.set_title("Compliance Risk Distribution")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return img_b64, counts

# ==================== SUMMARY ====================
def summarize_text_bedrock(text):
    try:
        payload = {
            "inputText": f"Summarize this compliance document in 3 sentences. List major risks as bullets:\n\n{text}",
            "textGenerationConfig": {"temperature": 0.2, "maxTokenCount": 250}
        }
        resp = bedrock.invoke_model(
            modelId="amazon.titan-text-express-v1",
            body=json.dumps(payload),
            accept="application/json",
            contentType="application/json",
        )
        result = json.loads(resp["body"].read())
        return result.get("results", [{}])[0].get("outputText", "").strip()
    except:
        return "⚠️ Failed to summarize"

# ==================== PDF REPORT ====================
def generate_pdf_report(summary, risk_analysis, counts):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "📄 Compliance Risk Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Summary:")
    text_obj = c.beginText(50, height - 100)
    text_obj.setFont("Helvetica", 10)
    for line in summary.split("\n"):
        text_obj.textLine(line)
    c.drawText(text_obj)

    y = height - 180
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Risk Analysis:")
    y -= 20
    c.setFont("Helvetica", 9)
    for r in risk_analysis:
        line = f"{r['clause_number']}: {r['clause']} [{r['risk_level']}] - {r['reason']}"
        c.drawString(50, y, line[:110])  # truncate if too long
        y -= 12
        if y < 100:
            c.showPage()
            y = height - 50

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Risk Counts:")
    c.setFont("Helvetica", 10)
    y -= 15
    for lvl, val in counts.items():
        c.drawString(60, y, f"{lvl}: {val}")
        y -= 12

    c.save()
    buf.seek(0)
    return buf

# ==================== ROUTES ====================
@app.route("/process", methods=["POST"])
def process():
    tmp_dir = None
    try:
        file = request.files.get("file")
        text_field = request.form.get("text", "")
        extracted = ""

        if file:
            filename = file.filename
            ext = filename.split(".")[-1]
            tmp_dir = tempfile.mkdtemp()
            saved = os.path.join(tmp_dir, filename)
            file.save(saved)
            extracted = extract_text_from_file(saved, ext)
        else:
            extracted = text_field or ""

        if not extracted.strip():
            return jsonify({"summary": "⚠️ No text found", "risk_analysis": [], "risk_counts": {}})

        clauses = split_into_clauses(extracted)
        if not clauses:
            clauses = [(str(i+1), p) for i, p in enumerate(extracted.split("\n")) if p.strip()]

        analyzed = analyze_clauses(clauses)
        chart_b64, counts = render_pie_base64(analyzed)
        summary = summarize_text_bedrock(extracted)

        return jsonify({
            "summary": summary,
            "risk_analysis": analyzed,
            "risk_chart_base64": chart_b64,
            "risk_counts": counts
        })
    finally:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import datetime

@app.route("/download_report", methods=["POST"])
def download_report():
    try:
        data = request.get_json()

        summary = data.get("summary", "")
        risk_analysis = data.get("risk_analysis", [])
        risk_counts = data.get("risk_counts", {})
        risk_chart_b64 = data.get("risk_chart_base64", None)

        # Temporary PDF path
        tmp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(tmp_dir, "compliance_report.pdf")

        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        elements.append(Paragraph("<b>📄 Compliance Risk Report</b>", styles['Title']))
        elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Summary
        elements.append(Paragraph("<b>Summary</b>", styles['Heading2']))
        elements.append(Paragraph(summary, styles['Normal']))
        elements.append(Spacer(1, 12))

        # Risk Table
        # Risk Table
        if risk_analysis:
          elements.append(Paragraph("<b>Risk Analysis</b>", styles['Heading2']))

          # Prepare data
          table_data = [["Clause Number", "Clause Text", "Risk Level", "Reason"]]
          for r in risk_analysis:
            table_data.append([
              r.get("clause_number", ""),
              r.get("clause", ""),
              r.get("risk_level", ""),
              r.get("reason", "")
          ])

          # Build table
          table = Table(table_data, repeatRows=1, colWidths=[70, 220, 80, 120])
          table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
          ]))
        elements.append(table)
        elements.append(Spacer(1, 12))


        # Risk Counts
        elements.append(Paragraph("<b>Risk Counts</b>", styles['Heading2']))
        counts_text = f"""
        High: {risk_counts.get('High',0)}<br/>
        Medium: {risk_counts.get('Medium',0)}<br/>
        Low: {risk_counts.get('Low',0)}<br/>
        """
        elements.append(Paragraph(counts_text, styles['Normal']))
        elements.append(Spacer(1, 12))

        # Risk Chart
        if risk_chart_b64:
            chart_path = os.path.join(tmp_dir, "chart.png")
            with open(chart_path, "wb") as f:
                f.write(base64.b64decode(risk_chart_b64))
            elements.append(Paragraph("<b>Risk Chart</b>", styles['Heading2']))
            elements.append(RLImage(chart_path, width=300, height=300))
            elements.append(Spacer(1, 12))

        doc.build(elements)

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        shutil.rmtree(tmp_dir)

        return (
            pdf_bytes,
            200,
            {
                "Content-Type": "application/pdf",
                "Content-Disposition": "attachment; filename=compliance_report.pdf",
            },
        )

    except Exception as e:
        print("Report generation error:", e)
        traceback.print_exc()
        return jsonify({"error": "Failed to generate report"}), 500

@app.route("/")
def home():
    return "Backend running: clause-based risk analysis with AWS Comprehend + Bedrock + PDF export"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
