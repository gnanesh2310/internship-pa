"""
AI Email Writer — generates personalised cold emails using a 4-provider fallback chain.

Chain: Gemini 1.5 Flash → Groq Llama3 → OpenRouter → Together AI
"""
import logging
from database.queries import get_profile, log_action
from ai_writer import gemini_client, groq_client, openrouter_client, together_client

logger = logging.getLogger(__name__)

# ── Company email prompt ──────────────────────────────────────────────────

COMPANY_PROMPT = """
You are writing a cold internship application email on behalf of {full_name}.

APPLICANT PROFILE:
- Name: {full_name}
- Degree: {degree}
- CGPA: {cgpa}
- Location: {location}
- Skills: {skills}
- Portfolio: {portfolio_url}
- GitHub: {github_url}

TARGET COMPANY:
- Company: {company_name}
- Role: {role_title}
- Job Description snippet: {description_snippet}
- Tech Stack: {tech_stack}

RESUME HIGHLIGHTS:
{resume_snippet}

RULES:
1. Write ONLY the email body — no subject line, no "Subject:", no preamble
2. Keep it under 180 words
3. Start with a genuine compliment about their product/tech stack — not generic
4. Mention 1-2 specific skills that match their stack
5. One sentence about a specific project from the resume
6. Clear CTA: ask for a 15-minute call or to review your work
7. Professional but conversational — NOT formal corporate language
8. Do NOT use: "I am writing to", "Please find attached", "I believe I am a great fit"
9. Sign off as: {full_name}

Write the email body now:
"""

PROFESSOR_PROMPT = """
You are writing a cold research internship request email on behalf of {full_name}.

APPLICANT:
- Name: {full_name}
- Degree: {degree}, CGPA: {cgpa}
- Location: {location}
- Skills: {skills}
- Portfolio: {portfolio_url}

TARGET PROFESSOR:
- Name: Prof. {professor_name}
- University: {university}
- Research Paper 1: "{paper_title_1}"
  Abstract snippet: {paper_abstract_1}
- Research Paper 2: "{paper_title_2}"
  Abstract snippet: {paper_abstract_2}

RULES:
1. Write ONLY the email body — no subject line
2. Keep it under 200 words
3. Start with ONE specific sentence referencing a finding from their actual paper
4. Explain how your skills (embedded systems, IoT, Python) relate to their research
5. Mention that you've read their specific paper (use the actual title)
6. Ask if they have a research internship opening for Summer 2025
7. Mention you can start immediately / flexible timeline
8. Professional academic tone
9. Sign off as: {full_name}, {degree}

Write the email body now:
"""

FOLLOWUP_PROMPT = """
Write a short, polite follow-up email for an internship application.

Original email was sent to: {company_or_prof}
Role/Research area: {role_or_paper}
Days since sent: {days_since}
Applicant: {full_name}

RULES:
1. Keep it under 80 words
2. Reference the original email briefly
3. Restate interest without being desperate
4. Politely ask if they had a chance to review
5. Professional tone

Write ONLY the follow-up body:
"""

# ── Fallback chain ────────────────────────────────────────────────────────

def _call_with_fallback(prompt: str) -> tuple[str, str]:
    """Try each AI provider in order. Returns (text, provider_name)."""
    providers = [
        ("gemini",      gemini_client.generate),
        ("groq",        groq_client.generate),
        ("openrouter",  openrouter_client.generate),
        ("together",    together_client.generate),
    ]
    last_error = None
    for name, fn in providers:
        try:
            text = fn(prompt)
            if text and len(text) > 50:
                return text, name
        except Exception as e:
            last_error = e
            logger.warning(f"AI provider {name} failed: {e}")
    raise RuntimeError(f"All AI providers failed. Last error: {last_error}")


# ── Public API ────────────────────────────────────────────────────────────

def write_company_email(job: dict) -> tuple[str, str, str]:
    """Returns (subject_line, email_body, provider_used)."""
    profile = get_profile()
    skills_str = ", ".join(
        profile.get("skills_frontend", []) +
        profile.get("skills_backend", []) +
        profile.get("skills_embedded", [])
    )
    prompt = COMPANY_PROMPT.format(
        full_name=profile["full_name"],
        degree=profile["degree"],
        cgpa=profile["cgpa"],
        location=profile["location"],
        skills=skills_str,
        portfolio_url=profile["portfolio_url"],
        github_url=profile["github_url"],
        company_name=job["company_name"],
        role_title=job["role_title"],
        description_snippet=(job.get("description") or "")[:400],
        tech_stack=", ".join(job.get("tech_stack") or []),
        resume_snippet=(profile.get("resume_text") or "")[:600],
    )
    body, provider = _call_with_fallback(prompt)
    subject = f"Internship Application — {job['role_title']} | {profile['full_name']}"
    log_action("email_written", f"AI email written for {job['company_name']}", "info", {"provider": provider})
    return subject, body, provider


def write_professor_email(prof: dict) -> tuple[str, str, str]:
    """Returns (subject_line, email_body, provider_used)."""
    profile = get_profile()
    skills_str = ", ".join(
        profile.get("skills_embedded", []) +
        profile.get("skills_backend", []) +
        profile.get("skills_tools", [])
    )
    prompt = PROFESSOR_PROMPT.format(
        full_name=profile["full_name"],
        degree=profile["degree"],
        cgpa=profile["cgpa"],
        location=profile["location"],
        skills=skills_str,
        portfolio_url=profile["portfolio_url"],
        professor_name=prof["professor_name"],
        university=prof["university"],
        paper_title_1=prof.get("paper_title_1") or "Recent research",
        paper_abstract_1=(prof.get("paper_abstract_1") or "")[:300],
        paper_title_2=prof.get("paper_title_2") or "Related work",
        paper_abstract_2=(prof.get("paper_abstract_2") or "")[:300],
    )
    body, provider = _call_with_fallback(prompt)
    subject = f"Research Internship Inquiry — {prof['department'] or 'EEE/ECE'} | {profile['full_name']}, VNIT Nagpur"
    log_action("email_written", f"Professor email written for {prof['professor_name']}", "info", {"provider": provider})
    return subject, body, provider


def write_followup_email(app: dict) -> tuple[str, str, str]:
    """Returns (subject_line, follow_up_body, provider_used)."""
    profile = get_profile()
    from datetime import datetime
    days = (datetime.utcnow() - datetime.fromisoformat(app["date_sent"].replace("Z", ""))).days
    prompt = FOLLOWUP_PROMPT.format(
        company_or_prof=app["company_or_prof"],
        role_or_paper=app["role_or_paper"],
        days_since=days,
        full_name=profile["full_name"],
    )
    body, provider = _call_with_fallback(prompt)
    subject = f"Re: Internship Application — {app['role_or_paper']}"
    return subject, body, provider
