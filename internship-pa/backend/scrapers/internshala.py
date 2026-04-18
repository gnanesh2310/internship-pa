"""
Internshala scraper — scrapes internship listings.
Uses requests + BeautifulSoup (no JS needed for listing pages).
"""
import logging
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from database.queries import upsert_job, log_action

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

SEARCH_URLS = [
    "https://internshala.com/internships/web-development-internship/",
    "https://internshala.com/internships/python-internship/",
    "https://internshala.com/internships/reactjs-internship/",
    "https://internshala.com/internships/embedded-systems-internship/",
    "https://internshala.com/internships/iot-internship/",
    "https://internshala.com/internships/research-internship/",
]


def _extract_email_from_text(text: str) -> str | None:
    """Try to find an email in the description."""
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def scrape() -> list[dict]:
    """Scrape all configured Internshala URLs and return list of jobs."""
    all_jobs = []
    for url in SEARCH_URLS:
        try:
            time.sleep(random.uniform(2, 5))
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"Internshala returned {resp.status_code} for {url}")
                continue

            soup = BeautifulSoup(resp.text, "lxml")
            internship_cards = soup.select(".internship_meta") or soup.select(".individual_internship")

            for card in internship_cards[:20]:
                try:
                    company = card.select_one(".company_name a, .link_display_like_text")
                    role = card.select_one(".profile a, h3.heading_4_5")
                    location_el = card.select_one(".location_link, .location span")
                    url_el = card.select_one("a[href*='/internship/detail']")

                    if not company or not role:
                        continue

                    job = {
                        "company_name": company.text.strip(),
                        "role_title": role.text.strip(),
                        "location": location_el.text.strip() if location_el else "Remote",
                        "source": "internshala",
                        "job_url": f"https://internshala.com{url_el['href']}" if url_el else url,
                        "tech_stack": [],
                        "processed": False,
                    }
                    all_jobs.append(job)
                    upsert_job(job)

                except Exception as e:
                    logger.debug(f"Card parse error: {e}")
                    continue

            logger.info(f"Internshala: scraped {len(internship_cards)} from {url}")

        except Exception as e:
            logger.error(f"Internshala scrape failed for {url}: {e}")

    log_action("scrape_done", f"Internshala scraped {len(all_jobs)} jobs", "info", {"count": len(all_jobs)})
    return all_jobs
