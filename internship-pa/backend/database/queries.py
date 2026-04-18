"""All database read/write helpers used by the PA."""
from datetime import date, datetime, timedelta
from database.supabase_client import get_client

PROFILE_ID = "00000000-0000-0000-0000-000000000001"

# ── Profile ────────────────────────────────────────────────────────────────

def get_profile() -> dict:
    db = get_client()
    res = db.table("profiles").select("*").eq("id", PROFILE_ID).single().execute()
    return res.data

# ── Job Listings ───────────────────────────────────────────────────────────

def upsert_job(job: dict) -> dict:
    db = get_client()
    res = db.table("job_listings").upsert(job, on_conflict="company_name,role_title").execute()
    return res.data[0] if res.data else {}

def get_unprocessed_jobs() -> list[dict]:
    db = get_client()
    res = db.table("job_listings").select("*").eq("processed", False).execute()
    return res.data or []

def mark_job_processed(job_id: str, classification: str):
    db = get_client()
    db.table("job_listings").update({"processed": True, "classification": classification}).eq("id", job_id).execute()

# ── Applications ───────────────────────────────────────────────────────────

def count_sent_today(app_type: str = None) -> int:
    db = get_client()
    today = date.today().isoformat()
    q = db.table("applications").select("*", count="exact").gte("date_sent", f"{today}T00:00:00")
    if app_type:
        q = q.eq("type", app_type)
    return q.execute().count or 0

def already_applied(contact_email: str) -> bool:
    db = get_client()
    res = db.table("applications").select("id").eq("contact_email", contact_email).limit(1).execute()
    return bool(res.data)

def insert_application(app: dict) -> dict:
    db = get_client()
    # Set follow_up_date to 7 days from now
    app["follow_up_date"] = (date.today() + timedelta(days=7)).isoformat()
    res = db.table("applications").insert(app).execute()
    return res.data[0] if res.data else {}

def get_pending_followups() -> list[dict]:
    db = get_client()
    today = date.today().isoformat()
    res = (db.table("applications")
             .select("*")
             .eq("follow_up_sent", False)
             .eq("reply_received", False)
             .lte("follow_up_date", today)
             .neq("status", "failed")
             .execute())
    return res.data or []

def mark_followup_sent(app_id: str):
    db = get_client()
    db.table("applications").update({
        "follow_up_sent": True,
        "follow_up_sent_at": datetime.utcnow().isoformat(),
        "status": "follow_up_sent"
    }).eq("id", app_id).execute()

# ── Professor Targets ─────────────────────────────────────────────────────

def get_pending_professors(limit: int = 10) -> list[dict]:
    db = get_client()
    res = (db.table("professor_targets")
             .select("*")
             .eq("status", "pending")
             .not_.is_("email", "null")
             .order("relevance_score", desc=True)
             .limit(limit)
             .execute())
    return res.data or []

def mark_professor_emailed(prof_id: str):
    db = get_client()
    db.table("professor_targets").update({"status": "emailed"}).eq("id", prof_id).execute()

# ── Manual Queue ──────────────────────────────────────────────────────────

def add_to_manual_queue(item: dict) -> dict:
    db = get_client()
    res = db.table("manual_queue").insert(item).execute()
    return res.data[0] if res.data else {}

# ── Activity Log ──────────────────────────────────────────────────────────

def log_action(action_type: str, description: str, level: str = "info", details: dict = None):
    db = get_client()
    db.table("activity_log").insert({
        "action_type": action_type,
        "description": description,
        "level": level,
        "details": details or {}
    }).execute()

# ── API Usage ─────────────────────────────────────────────────────────────

def track_api_usage(provider: str, tokens: int = 0, requests: int = 1, errors: int = 0):
    db = get_client()
    today = date.today().isoformat()
    # Upsert: increment counters
    existing = db.table("api_usage").select("*").eq("provider", provider).eq("date", today).execute()
    if existing.data:
        row = existing.data[0]
        db.table("api_usage").update({
            "tokens_used": row["tokens_used"] + tokens,
            "requests_made": row["requests_made"] + requests,
            "errors_count": row["errors_count"] + errors,
        }).eq("id", row["id"]).execute()
    else:
        db.table("api_usage").insert({
            "provider": provider,
            "date": today,
            "tokens_used": tokens,
            "requests_made": requests,
            "errors_count": errors,
        }).execute()
