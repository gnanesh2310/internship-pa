"""
Classifier — scores each job listing as GREEN, YELLOW, or RED.

GREEN  → Auto-email immediately (good match, automatable portal)
YELLOW → Email with caveat (partial match or needs review)
RED    → Add to manual queue (govt portal, CAPTCHA, no email)
"""
import re
from database.queries import get_profile

# Sites/orgs that ALWAYS require manual application
MANUAL_ORG_PATTERNS = [
    r"isro", r"drdo", r"barc", r"npcil", r"hal\b", r"nal\b",
    r"bsnl", r"bhel", r"ongc", r"coal india", r"ntpc",
    r"government", r"govt", r"ministry", r"icar", r"csir",
    r"sarkari", r"naukri\.gov", r"employment exchange",
]

# Roles we target
TARGET_ROLE_KEYWORDS = [
    "web", "frontend", "react", "javascript", "fullstack", "full stack",
    "flask", "python", "backend", "iot", "embedded", "esp32", "firmware",
    "research intern", "research assistant", "ml", "computer vision",
    "software intern", "software engineer intern", "developer intern",
]

# Strong skill matches
STRONG_SKILL_MATCH = [
    "react", "javascript", "html", "css", "python", "flask",
    "esp32", "raspberry pi", "iot", "opencv", "git",
]

# Immediate disqualifiers for automation
AUTO_RED_SIGNALS = [
    "aadhaar", "otp login", "sso", "government portal", "apply via portal only",
    "no email applications", "walk-in", "walk in", "offline only",
]


def classify(job: dict) -> tuple[str, str]:
    """
    Returns (classification, reason):
      classification: 'GREEN' | 'YELLOW' | 'RED'
      reason: human-readable explanation
    """
    profile = get_profile()
    company_lower = job.get("company_name", "").lower()
    role_lower = job.get("role_title", "").lower()
    desc_lower = (job.get("description") or "").lower()
    location = (job.get("location") or "").lower()
    combined = f"{company_lower} {role_lower} {desc_lower}"

    # ── RED: Manual-only orgs ─────────────────────────────────────────────
    for pattern in MANUAL_ORG_PATTERNS:
        if re.search(pattern, combined):
            return "RED", f"Government/PSU org detected: '{pattern}' — must apply via official portal"

    # ── RED: Portal signals ───────────────────────────────────────────────
    for signal in AUTO_RED_SIGNALS:
        if signal in combined:
            return "RED", f"Portal-only application detected: '{signal}'"

    # ── RED: No contact email possible ───────────────────────────────────
    if not job.get("job_url") and not job.get("contact_email_hint"):
        return "RED", "No job URL or contact found — cannot automate"

    # ── Check role match ──────────────────────────────────────────────────
    role_matched = any(kw in role_lower or kw in desc_lower for kw in TARGET_ROLE_KEYWORDS)
    skill_matches = [s for s in STRONG_SKILL_MATCH if s in combined]

    # ── Check location match ──────────────────────────────────────────────
    target_locs = [l.lower() for l in profile.get("target_locations", [])]
    location_ok = (
        "remote" in location
        or any(loc in location for loc in target_locs)
        or location == ""  # unknown location = give benefit of doubt
    )

    # ── GREEN: Strong match ───────────────────────────────────────────────
    if role_matched and len(skill_matches) >= 2 and location_ok:
        return "GREEN", f"Strong match: role={role_lower[:40]}, skills={skill_matches[:3]}"

    # ── GREEN: Good enough match ──────────────────────────────────────────
    if role_matched and location_ok:
        return "GREEN", f"Role match: {role_lower[:40]}"

    # ── YELLOW: Partial match ─────────────────────────────────────────────
    if role_matched or len(skill_matches) >= 1:
        return "YELLOW", f"Partial match: skills={skill_matches}, location={'✓' if location_ok else '?'}"

    # ── RED: No match ─────────────────────────────────────────────────────
    return "RED", f"No role/skill match for: {role_lower[:40]}"


def should_skip(job: dict) -> tuple[bool, str]:
    """Check if we already applied to this company recently."""
    from database.queries import already_applied
    email_hint = job.get("contact_email_hint")
    if email_hint and already_applied(email_hint):
        return True, f"Already applied to {email_hint}"
    return False, ""
