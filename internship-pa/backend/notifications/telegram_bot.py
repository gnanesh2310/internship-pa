"""
Telegram bot — sends all notification types to your Telegram.
Every important PA event gets a message.
"""
import os
import logging
import requests
from datetime import date

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8394802242")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def _send(text: str, parse_mode: str = "HTML") -> bool:
    if not BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set — skipping notification")
        return False
    try:
        res = requests.post(
            f"{BASE_URL}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text, "parse_mode": parse_mode},
            timeout=10,
        )
        return res.ok
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


def send_morning_report(sent_today: int, total: int, manual_pending: int, prof_sent: int):
    """Daily morning summary — sent at the start of each run."""
    today = date.today().strftime("%A, %d %b %Y")
    text = f"""🌅 <b>Good Morning! PA Daily Report</b>
📅 {today}

📨 <b>Emails sent today:</b> {sent_today}
📊 <b>Total all time:</b> {total}
🎓 <b>Professor emails:</b> {prof_sent}
⚠️ <b>Manual pending:</b> {manual_pending}

🤖 PA is running. Emails will go out now."""
    return _send(text)


def send_email_success(company: str, role: str, email: str, provider: str):
    """Notify on each successful send."""
    text = f"""✅ <b>Email Sent!</b>

🏢 <b>{company}</b>
💼 {role}
📧 {email}
🤖 AI: {provider}"""
    return _send(text)


def send_manual_alert(org: str, role: str, url: str, reason: str, deadline: str = None):
    """Alert when a manual application is needed — highest priority."""
    deadline_str = f"\n⏰ <b>Deadline: {deadline}</b>" if deadline else ""
    text = f"""🔴 <b>MANUAL ACTION NEEDED</b>
{deadline_str}

🏛️ <b>{org}</b>
💼 {role}
❓ Why: {reason}

🔗 <a href="{url}">Open Application Portal</a>

<i>Tap the link above and apply manually. Takes ~10 mins.</i>"""
    return _send(text)


def send_reply_alert(company: str, role: str, sender_email: str):
    """Alert when someone replies to your email."""
    text = f"""📬 <b>Reply Received!</b>

🏢 <b>{company}</b>
💼 {role}
📧 From: {sender_email}

Check your Gmail inbox and respond promptly! 🎯"""
    return _send(text)


def send_followup_notice(company: str, role: str, days: int):
    """Notify that a follow-up was sent."""
    text = f"""🔄 <b>Follow-up Sent</b>

🏢 {company} — {role}
⏱️ {days} days since original email"""
    return _send(text)


def send_error_alert(error_msg: str, module: str):
    """Alert on errors."""
    text = f"""⚠️ <b>PA Error — {module}</b>

<code>{error_msg[:400]}</code>

Check Railway logs for details."""
    return _send(text)


def send_daily_summary(sent: int, failed: int, manual: int, followups: int, providers_used: list):
    """End-of-day summary."""
    providers_str = ", ".join(set(providers_used)) if providers_used else "none"
    text = f"""🌙 <b>PA Daily Summary</b>

✅ Emails sent: {sent}
❌ Failed: {failed}
🔄 Follow-ups: {followups}
⚠️ Manual queue: {manual}
🤖 AI used: {providers_str}

See full dashboard for details."""
    return _send(text)


def send_api_warning(provider: str, pct: float):
    """Warn when approaching API limits."""
    text = f"""⚠️ <b>API Limit Warning</b>

Provider: <b>{provider}</b>
Usage: {pct:.1f}% of daily limit

PA will switch to backup provider automatically."""
    return _send(text)
