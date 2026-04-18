"""
main.py — Entry point for the Internship PA backend.

On Railway: runs as a long-lived worker process.
Wakes up every day at the configured send time (default 9:00 AM IST)
and executes the full daily workflow.

To run locally for testing:
    python main.py

To run a single immediate run (skip schedule):
    python main.py --now
"""
import sys
import time
import logging
import schedule
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

from database.queries import get_profile
from scheduler import run_daily

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

IST = pytz.timezone("Asia/Kolkata")


def main():
    # Run immediately if --now flag passed
    if "--now" in sys.argv:
        logger.info("--now flag detected. Running immediately.")
        run_daily()
        return

    # Get configured send time from profile
    try:
        profile = get_profile()
        hour = profile.get("send_time_hour", 9)
        minute = profile.get("send_time_minute", 0)
    except Exception:
        logger.warning("Could not load profile — defaulting to 9:00 AM IST")
        hour, minute = 9, 0

    run_time = f"{hour:02d}:{minute:02d}"
    logger.info(f"Internship PA scheduler started.")
    logger.info(f"Scheduled daily run at {run_time} IST")
    logger.info(f"Current IST time: {datetime.now(IST).strftime('%H:%M:%S')}")

    # Schedule the daily run
    schedule.every().day.at(run_time).do(run_daily)

    # Also run follow-up check at 6 PM IST
    schedule.every().day.at("18:00").do(_followup_only)

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)


def _followup_only():
    """Evening-only follow-up check."""
    logger.info("Evening follow-up check running...")
    from scheduler import step_followups
    step_followups()


if __name__ == "__main__":
    main()
