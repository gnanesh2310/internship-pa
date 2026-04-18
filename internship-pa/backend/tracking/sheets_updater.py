"""
Google Sheets updater — mirrors all applications to a Google Sheet.
Great for sharing progress or viewing on mobile.

Sheet columns:
Date | Company/Prof | Role | Email Used | Status | Reply | Follow-up | Type
"""
import os
import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from database.supabase_client import get_client

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = ["Date", "Company / Professor", "Role / Paper", "Email Used", "Status", "Reply?", "Follow-up?", "Type", "Subject"]


def _get_sheet():
    """Connect to Google Sheets using service account credentials."""
    creds_path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_JSON", "service_account.json")
    sheet_id = os.environ["GOOGLE_SHEETS_ID"]
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc.open_by_key(sheet_id).sheet1


def sync_all_applications():
    """
    Full sync: pull all applications from Supabase and write to Sheets.
    Clears the sheet and rewrites from scratch.
    """
    try:
        db = get_client()
        res = db.table("applications").select("*").order("date_sent", desc=True).execute()
        apps = res.data or []

        sheet = _get_sheet()
        sheet.clear()
        sheet.append_row(HEADERS)

        # Format date for display
        rows = []
        for app in apps:
            date_str = datetime.fromisoformat(app["date_sent"].replace("Z", "")).strftime("%d %b %Y %H:%M")
            rows.append([
                date_str,
                app["company_or_prof"],
                app["role_or_paper"],
                app["sent_from"],
                app["status"].upper(),
                "Yes" if app["reply_received"] else "No",
                "Yes" if app["follow_up_sent"] else "No",
                app["type"].capitalize(),
                app.get("subject_line", ""),
            ])

        if rows:
            sheet.append_rows(rows)

        logger.info(f"Sheets synced: {len(rows)} applications")

    except Exception as e:
        logger.error(f"Sheets sync failed: {e}")


def append_new_application(app: dict):
    """Append a single new application row to the sheet (faster than full sync)."""
    try:
        sheet = _get_sheet()
        date_str = datetime.utcnow().strftime("%d %b %Y %H:%M")
        sheet.append_row([
            date_str,
            app["company_or_prof"],
            app["role_or_paper"],
            app["sent_from"],
            "SENT",
            "No",
            "No",
            app["type"].capitalize(),
            app.get("subject_line", ""),
        ])
    except Exception as e:
        logger.error(f"Sheets append failed: {e}")
