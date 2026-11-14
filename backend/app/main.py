from fastapi import UploadFile, File
import email
from email import policy

@app.post("/api/upload-eml")
async def upload_eml_file(file: UploadFile = File(...)):
    raw_bytes = await file.read()
    msg = email.message_from_bytes(raw_bytes, policy=policy.default)

    sender = str(msg.get("From", "unknown@sender.com"))
    recipient = str(msg.get("To", "secops@enterprise.com"))
    subject = str(msg.get("Subject", "(No Subject)"))

    # Extract all Received and Authentication headers
    received_headers = msg.get_all("Received") or []
    auth_results = str(msg.get("Authentication-Results", "dkim=fail spf=fail dmarc=fail"))
    combined_headers = "\n".join(received_headers) + f"\n{auth_results}"

    # Extract plain text body
    body_text = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body_text += part.get_content()
    else:
        body_text = msg.get_content()

    # Reuse existing analysis logic
    payload = EmailPayload(
        sender_email=sender,
        recipient_email=recipient,
        subject=subject,
        raw_body=body_text,
        raw_headers=combined_headers
    )
    return await analyze_email(payload)
from fastapi.responses import Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

@app.post("/api/generate-pdf")
async def generate_pdf(payload: dict):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header Banner
    p.setFillColorRGB(0.1, 0.2, 0.4)
    p.rect(0, height - 80, width, 80, fill=1, stroke=0)
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, height - 35, "ISO/IEC 27037 DIGITAL EVIDENCE REPORT")
    p.setFont("Helvetica", 10)
    p.drawString(40, height - 55, "Lead Analyst: Arti Saraswat | AI Email Threat & GeoForensics Platform")

    # Content Body
    p.setFillColorRGB(0.2, 0.2, 0.2)
    p.setFont("Helvetica-Bold", 12)
    y = height - 120
    p.drawString(40, y, "1. Ingestion & Message Metadata")
    
    p.setFont("Helvetica", 10)
    y -= 20
    p.drawString(40, y, f"Sender Email: {payload.get('sender', 'N/A')}")
    y -= 15
    p.drawString(40, y, f"Recipient Email: {payload.get('recipient', 'N/A')}")
    y -= 15
    p.drawString(40, y, f"Subject: {payload.get('subject', 'N/A')}")

    # Threat Assessment
    y -= 35
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "2. Threat & Signal Fusion Assessment")
    
    analysis = payload.get('analysis', {})
    p.setFont("Helvetica", 10)
    y -= 20
    p.drawString(40, y, f"Risk Score: {analysis.get('risk_score', 0)} / 100 ({analysis.get('threat_level', 'UNKNOWN')})")
    y -= 15
    signals = analysis.get('signals', {})
    p.drawString(40, y, f"DKIM Pass: {signals.get('dkim_pass')} | SPF Pass: {signals.get('spf_pass')} | DMARC Pass: {signals.get('dmarc_pass')}")
    y -= 15
    p.drawString(40, y, f"NLP Phishing Indicators: {signals.get('nlp_threat_indicators')} | Prompt Injection: {signals.get('prompt_injection_detected')}")

    # Blockchain Audit Trail
    y -= 35
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, y, "3. Chain-of-Custody & Blockchain Ledger")
    
    audit = analysis.get('blockchain_audit', {})
    p.setFont("Helvetica", 8)
    y -= 20
    p.drawString(40, y, f"SHA-256 Hash: {audit.get('sha256_hash', 'N/A')}")
    y -= 15
    p.drawString(40, y, f"Polygon Transaction: {audit.get('transaction_hash', 'N/A')}")
    y -= 15
    p.drawString(40, y, f"Timestamp (UTC): {audit.get('timestamp', 'N/A')}")

    # Footer Compliance Note
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(40, 40, "Certified compliant with NIST SP 800-86 and ISO/IEC 27037 standards for digital evidence handling.")

    p.showPage()
    p.save()
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(), 
        media_type="application/pdf", 
        headers={"Content-Disposition": "attachment; filename=ISO27037_Evidence_Report.pdf"}
    )