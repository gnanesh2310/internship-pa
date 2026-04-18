"""
Scheduler — orchestrates the daily PA workflow.

Full daily flow:
1. Send morning Telegram report
2. Run all scrapers (Internshala, LinkedIn, Naukri, Wellfound)
3. Classify each unprocessed job (GREEN/YELLOW/RED)
4. Send emails for GREEN jobs (up to daily limit)
5. Add RED jobs to manual queue + Telegram alert
6. Run professor scraper
7. Email pending professors (up to limit)
8. Send follow-ups for 7-day-old unanswered emails
9. Sync Google Sheets
10. Send end-of-day Telegram summary
"""
import logging
import time
import random
import os
from datetime import datetime, date
import pytz

from database.queries import (
    get_profile, get_unprocessed_jobs, mark_job_processed,
    count_sent_today, already_applied, insert_application,
    get_pending_professors, mark_professor_emailed,
    get_pending_followups, mark_followup_sent,
    add_to_manual_queue, log_action, track_api_usage,
)
from classifier.classifier import classify, should_skip
from ai_writer.email_writer import write_company_email, write_professor_email, write_followup_email
from sender.gmail_sender import send_email, send_followup
from notifications.telegram_bot import (
    send_morning_report, send_email_success, send_manual_alert,
    send_followup_notice, send_error_alert, send_daily_summary,
)
from tracking.sheets_updater import append_new_application

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

IST = pytz.timezone("Asia/Kolkata")

# ── Step trackers ─────────────────────────────────────────────────────────
stats = {
    "emails_sent": 0,
    "emails_failed": 0,
    "manual_added": 0,
    "followups_sent": 0,
    "providers_used": [],
}


def step_scrape_jobs():
    """Run all job scrapers."""
    logger.info("=== STEP 1: Scraping jobs ===")
    try:
        from scrapers import internshala, linkedin, naukri, wellfound
        internshala.scrape()
        naukri.scrape()
        try:
            linkedin.scrape()
        except Exception as e:
            logger.warning(f"LinkedIn scraper failed (non-fatal): {e}")
        try:
            wellfound.scrape()
        except Exception as e:
            logger.warning(f"Wellfound scraper failed (non-fatal): {e}")
    except Exception as e:
        logger.error(f"Job scraping error: {e}")
        send_error_alert(str(e), "job_scraper")


def step_process_jobs():
    """Classify + email GREEN jobs."""
    logger.info("=== STEP 2: Processing job listings ===")
    profile = get_profile()

    if not profile.get("company_mode_enabled", True):
        logger.info("Company mode is OFF — skipping")
        return

    daily_limit = profile.get("company_daily_limit", 15)
    jobs = get_unprocessed_jobs()
    logger.info(f"Found {len(jobs)} unprocessed jobs")

    for job in jobs:
        # Check daily limit
        sent_today = count_sent_today("company")
        if sent_today >= daily_limit:
            logger.info(f"Daily company limit reached ({daily_limit}). Stopping.")
            break

        # Classify
        classification, reason = classify(job)
        mark_job_processed(job["id"], classification)
        logger.info(f"  {job['company_name']} — {job['role_title']}: {classification} ({reason})")

        if classification == "RED":
            # Add to manual queue if has URL
            if job.get("job_url"):
                item = {
                    "org_name": job["company_name"],
                    "role": job["role_title"],
                    "portal_url": job["job_url"],
                    "reason": reason,
                    "telegram_alerted": False,
                }
                added = add_to_manual_queue(item)
                if added:
                    send_manual_alert(
                        org=job["company_name"],
                        role=job["role_title"],
                        url=job["job_url"],
                        reason=reason,
                    )
                    added_item = {**item, "telegram_alerted": True}
                    from database.supabase_client import get_client
                    get_client().table("manual_queue").update({"telegram_alerted": True}).eq("id", added["id"]).execute()
                    stats["manual_added"] += 1
            continue

        if classification in ("GREEN", "YELLOW"):
            # Find contact email — from job data or derive from company domain
            contact_email = job.get("contact_email_hint")
            if not contact_email:
                logger.debug(f"No contact email for {job['company_name']} — skipping")
                continue

            # Check if already applied
            if already_applied(contact_email):
                logger.info(f"  Already applied to {contact_email} — skipping")
                continue

            try:
                # Generate email
                subject, body, provider = write_company_email(job)
                stats["providers_used"].append(provider)

                # Send it
                success = send_email(contact_email, subject, body, account="company")

                if success:
                    app = insert_application({
                        "company_or_prof": job["company_name"],
                        "role_or_paper": job["role_title"],
                        "contact_email": contact_email,
                        "sent_from": profile["primary_email"],
                        "type": "company",
                        "subject_line": subject,
                        "email_body": body,
                        "status": "sent",
                        "job_listing_id": job["id"],
                    })
                    append_new_application(app)
                    send_email_success(job["company_name"], job["role_title"], contact_email, provider)
                    stats["emails_sent"] += 1
                else:
                    stats["emails_failed"] += 1

            except Exception as e:
                logger.error(f"Failed to email {job['company_name']}: {e}")
                stats["emails_failed"] += 1
                send_error_alert(str(e), f"email_writer/{job['company_name']}")


def step_professor_emails():
    """Email pending professors."""
    logger.info("=== STEP 3: Professor emails ===")
    profile = get_profile()

    if not profile.get("professor_mode_enabled", True):
        logger.info("Professor mode is OFF — skipping")
        return

    daily_limit = profile.get("professor_daily_limit", 5)
    professors = get_pending_professors(limit=daily_limit * 2)

    for prof in professors:
        sent_today = count_sent_today("professor")
        if sent_today >= daily_limit:
            logger.info(f"Daily professor limit reached ({daily_limit}). Stopping.")
            break

        if not prof.get("email"):
            logger.debug(f"No email for Prof. {prof['professor_name']} — skipping")
            continue

        if already_applied(prof["email"]):
            mark_professor_emailed(prof["id"])
            continue

        try:
            subject, body, provider = write_professor_email(prof)
            stats["providers_used"].append(provider)

            success = send_email(prof["email"], subject, body, account="professor")

            if success:
                app = insert_application({
                    "company_or_prof": prof["professor_name"],
                    "role_or_paper": f"{prof['university']} — {prof.get('department', 'EEE')}",
                    "contact_email": prof["email"],
                    "sent_from": profile["research_email"],
                    "type": "professor",
                    "subject_line": subject,
                    "email_body": body,
                    "status": "sent",
                })
                append_new_application(app)
                mark_professor_emailed(prof["id"])
                send_email_success(prof["professor_name"], prof["university"], prof["email"], provider)
                stats["emails_sent"] += 1
            else:
                stats["emails_failed"] += 1

        except Exception as e:
            logger.error(f"Failed to email Prof. {prof['professor_name']}: {e}")
            stats["emails_failed"] += 1


def step_followups():
    """Send follow-up emails for 7-day-old unanswered applications."""
    logger.info("=== STEP 4: Follow-ups ===")
    pending = get_pending_followups()
    logger.info(f"Found {len(pending)} follow-ups due")

    for app in pending:
        try:
            subject, body, provider = write_followup_email(app)
            account = "professor" if app["type"] == "professor" else "company"
            success = send_email(app["contact_email"], subject, body, account=account)

            if success:
                mark_followup_sent(app["id"])
                from datetime import datetime
                days = (datetime.utcnow() - datetime.fromisoformat(app["date_sent"].replace("Z", ""))).days
                send_followup_notice(app["company_or_prof"], app["role_or_paper"], days)
                stats["followups_sent"] += 1

        except Exception as e:
            logger.error(f"Follow-up failed for {app['company_or_prof']}: {e}")


def step_scrape_professors():
    """Run professor scraper to find new research targets."""
    logger.info("=== STEP 5: Professor scraper ===")
    profile = get_profile()
    if not profile.get("professor_mode_enabled", True):
        return
    try:
        from scrapers.professor_scraper import scrape_and_store
        count = scrape_and_store(limit_per_uni=3)
        logger.info(f"Professor scraper added {count} new professors")
    except Exception as e:
        logger.error(f"Professor scraper failed: {e}")


def run_daily():
    """Full daily run — called once per day."""
    logger.info("=" * 60)
    logger.info("INTERNSHIP PA — DAILY RUN STARTING")
    logger.info(f"Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
    logger.info("=" * 60)

    # Reset stats
    for k in stats:
        if isinstance(stats[k], list):
            stats[k].clear()
        else:
            stats[k] = 0

    # Morning report
    from database.queries import count_sent_today
    from database.supabase_client import get_client
    db = get_client()
    total = db.table("applications").select("*", count="exact").execute().count or 0
    manual_pending = db.table("manual_queue").select("*", count="exact").eq("status", "pending").execute().count or 0
    prof_sent = db.table("applications").select("*", count="exact").eq("type", "professor").execute().count or 0
    send_morning_report(count_sent_today(), total, manual_pending, prof_sent)

    # Run all steps
    step_scrape_jobs()
    step_process_jobs()
    step_professor_emails()
    step_followups()
    step_scrape_professors()

    # Sync Sheets
    try:
        from tracking.sheets_updater import sync_all_applications
        sync_all_applications()
    except Exception as e:
        logger.error(f"Sheets sync failed: {e}")

    # End-of-day summary
    send_daily_summary(
        sent=stats["emails_sent"],
        failed=stats["emails_failed"],
        manual=stats["manual_added"],
        followups=stats["followups_sent"],
        providers_used=stats["providers_used"],
    )

    log_action("daily_run_complete", f"Daily run complete. Sent: {stats['emails_sent']}, Failed: {stats['emails_failed']}", "success")
    logger.info(f"\n✓ Done. Sent: {stats['emails_sent']}, Failed: {stats['emails_failed']}, Manual: {stats['manual_added']}")
