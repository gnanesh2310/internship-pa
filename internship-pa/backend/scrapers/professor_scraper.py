"""
Professor scraper — finds professors at IITs/NITs doing relevant research.
Uses Google Scholar author search + university faculty pages.
"""
import logging
import time
import random
import re
import requests
from bs4 import BeautifulSoup
from database.queries import log_action
from database.supabase_client import get_client

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# IITs and NITs to target
TARGET_UNIVERSITIES = [
    ("IIT Bombay",   "electrical engineering", "ee.iitb.ac.in/web/people/faculty"),
    ("IIT Madras",   "electrical engineering", "ee.iitm.ac.in/faculty/"),
    ("IIT Delhi",    "electrical engineering", "ee.iitd.ac.in/faculty"),
    ("IIT Kharagpur","electrical engineering", "www.iitkgp.ac.in/department/EE"),
    ("NIT Warangal", "electrical engineering", "www.nitw.ac.in/dept/ee/"),
    ("NIT Trichy",   "electrical engineering", "www.nitt.edu/home/academics/departments/eee/faculty/"),
    ("IIT Hyderabad","electrical engineering", "iith.ac.in/ee/faculty.html"),
    ("IIT Roorkee",  "electrical engineering", "www.iitr.ac.in/departments/EE/pages/Faculty.html"),
]

# Research areas relevant to your skills
RELEVANT_KEYWORDS = [
    "iot", "internet of things", "embedded", "robotics", "computer vision",
    "power electronics", "signal processing", "control systems", "smart grid",
    "wireless sensor", "microcontroller", "fpga", "vlsi", "machine learning",
    "image processing", "drone", "autonomous", "energy harvesting",
]


def _search_scholar_author(name: str, university: str) -> dict:
    """Search Google Scholar for a professor's papers."""
    try:
        query = f"{name} {university} electrical engineering"
        url = f"https://scholar.google.com/scholar?q={query.replace(' ', '+')}&as_ylo=2022"
        time.sleep(random.uniform(3, 7))
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "lxml")

        papers = []
        for result in soup.select(".gs_ri")[:3]:
            title_el = result.select_one(".gs_rt a")
            abstract_el = result.select_one(".gs_rs")
            if title_el:
                papers.append({
                    "title": title_el.text.strip(),
                    "abstract": abstract_el.text.strip() if abstract_el else "",
                })

        return {"papers": papers}
    except Exception as e:
        logger.debug(f"Scholar search failed for {name}: {e}")
        return {"papers": []}


def _calculate_relevance(papers: list[dict]) -> int:
    """Score 0-10 how relevant this professor is."""
    if not papers:
        return 0
    score = 0
    for paper in papers:
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
        for kw in RELEVANT_KEYWORDS:
            if kw in text:
                score += 1
    return min(score, 10)


def _find_email(name: str, university: str, dept_url: str) -> str | None:
    """Try to scrape professor email from department page."""
    try:
        time.sleep(random.uniform(2, 5))
        resp = requests.get(f"https://{dept_url}", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "lxml")
        text = soup.get_text()
        # Look for email near the professor's name
        name_parts = name.lower().split()
        paragraphs = [p for p in text.split('\n') if any(part in p.lower() for part in name_parts)]
        for para in paragraphs:
            match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", para)
            if match:
                return match.group(0)
    except Exception:
        pass
    return None


def scrape_and_store(limit_per_uni: int = 5) -> int:
    """
    Scrape professors from IITs/NITs and store in professor_targets.
    Returns count of new professors added.
    """
    db = get_client()
    total_added = 0

    for university, dept, dept_url in TARGET_UNIVERSITIES:
        try:
            logger.info(f"Scraping faculty from {university}...")
            time.sleep(random.uniform(5, 10))

            url = f"https://{dept_url}"
            resp = requests.get(url, headers=HEADERS, timeout=20)
            soup = BeautifulSoup(resp.text, "lxml")

            # Generic faculty name extraction — works for most IIT pages
            faculty_names = []
            for el in soup.select("h4, h3, .faculty-name, td strong, .name"):
                name = el.text.strip()
                if len(name.split()) in (2, 3) and name[0].isupper():
                    faculty_names.append(name)

            faculty_names = list(dict.fromkeys(faculty_names))[:limit_per_uni]
            logger.info(f"  Found {len(faculty_names)} faculty at {university}")

            for name in faculty_names:
                # Check if already in DB
                existing = db.table("professor_targets").select("id").eq("professor_name", name).eq("university", university).execute()
                if existing.data:
                    continue

                # Get papers
                scholar_data = _search_scholar_author(name, university)
                papers = scholar_data.get("papers", [])
                relevance = _calculate_relevance(papers)

                if relevance == 0:
                    continue  # Skip irrelevant professors

                # Try to find email
                email = _find_email(name, university, dept_url)

                prof = {
                    "professor_name": name,
                    "university": university,
                    "department": "Electrical Engineering",
                    "email": email,
                    "paper_title_1": papers[0]["title"] if len(papers) > 0 else None,
                    "paper_abstract_1": papers[0]["abstract"][:500] if len(papers) > 0 else None,
                    "paper_title_2": papers[1]["title"] if len(papers) > 1 else None,
                    "paper_abstract_2": papers[1]["abstract"][:500] if len(papers) > 1 else None,
                    "research_areas": [kw for kw in RELEVANT_KEYWORDS if kw in str(papers).lower()],
                    "relevance_score": relevance,
                    "status": "pending",
                }

                db.table("professor_targets").insert(prof).execute()
                total_added += 1
                logger.info(f"  Added Prof. {name} ({university}) — score {relevance}")

        except Exception as e:
            logger.error(f"Failed to scrape {university}: {e}")

    log_action("scrape_done", f"Professor scraper added {total_added} professors", "info", {"count": total_added})
    return total_added
