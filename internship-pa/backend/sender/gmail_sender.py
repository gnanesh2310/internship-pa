"""
Gmail sender — sends emails via Gmail API using OAuth refresh tokens.
Uses random delays between sends to avoid spam detection.
"""
import os
import time
import random
import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from database.queries import get_profile, log_action

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _get_gmail_service(refresh_token: str):
    """Build Gmail API service from refresh token."""
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GMAIL_CLIENT_ID"],
        client_secret=os.environ["GMAIL_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


def _build_message(sender: str, to: str, subject: str, body: str) -> dict:
    """Encode email as base64 for Gmail API."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.attach(MIMEText(body, "plain"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def send_email(
    to: str,
    subject: str,
    body: str,
    account: str = "company",  # "company" | "professor"
    delay: bool = True,
) -> bool:
    """
    Send a single email.
    Returns True on success, False on failure.
    account = "company"   → uses kgnanesh98@gmail.com
    account = "professor" → uses kgnanesh52@gmail.com
    """
    profile = get_profile()
    delay_min = profile.get("delay_min_minutes", 4)
    delay_max = profile.get("delay_max_minutes", 6)

    if account == "professor":
        refresh_token = os.environ["GMAIL_RESEARCH_REFRESH_TOKEN"]
        sender_email = profile["research_email"]
    else:
        refresh_token = os.environ["GMAIL_COMPANY_REFRESH_TOKEN"]
        sender_email = profile["primary_email"]

    try:
        service = _get_gmail_service(refresh_token)
        message = _build_message(sender_email, to, subject, body)
        service.users().messages().send(userId="me", body=message).execute()
        logger.info(f"✓ Sent to {to} from {sender_email}")
        log_action("email_sent", f"Email sent to {to}", "success", {"from": sender_email, "subject": subject})

        if delay:
            wait = random.uniform(delay_min * 60, delay_max * 60)
            logger.info(f"  Waiting {wait:.0f}s before next email...")
            time.sleep(wait)

        return True

    except Exception as e:
        logger.error(f"✗ Failed to send to {to}: {e}")
        log_action("email_failed", f"Failed to send to {to}: {str(e)}", "error", {"to": to})
        return False


def send_followup(app: dict, subject: str, body: str) -> bool:
    """Send a follow-up email for an existing application."""
    account = "professor" if app["type"] == "professor" else "company"
    return send_email(app["contact_email"], subject, body, account=account)
