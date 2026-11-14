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