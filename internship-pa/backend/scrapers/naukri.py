"""
Naukri.com scraper — scrapes internship listings using requests.
"""
import logging
import time
import random
import requests
from bs4 import BeautifulSoup
from database.queries import upsert_job, log_action

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SEARCH_URLS = [
    "https://www.naukri.com/internship-jobs-in-india?k=web+developer+intern",
    "https://www.naukri.com/internship-jobs-in-india?k=python+intern",
    "https://www.naukri.com/internship-jobs-in-india?k=frontend+react+intern",
    "https://www.naukri.com/internship-jobs-in-india?k=iot+embedded+intern",
]


def scrape() -> list[dict]:
    all_jobs = []
    for url in SEARCH_URLS:
        try:
            time.sleep(random.uniform(3, 7))
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code != 200:
                logger.warning(f"Naukri returned {resp.status_code}")
                continue

            soup = BeautifulSoup(resp.text, "lxml")
            cards = soup.select("article.jobTuple, .list li.jobTupleHeader")

            for card in cards[:15]:
                try:
                    company = card.select_one(".companyInfo a, .subTitle")
                    role = card.select_one(".title a, .jobTuple-jobTitle")
                    location_el = card.select_one(".ellipsis.fleft.locWdth, .location span")
                    link_el = card.select_one("a[href*='naukri.com/job']")

                    if not company or not role:
                        continue

                    job = {
                        "company_name": company.text.strip(),
                        "role_title": role.text.strip(),
                        "location": location_el.text.strip() if location_el else "India",
                        "source": "naukri",
                        "job_url": link_el["href"] if link_el else url,
                        "tech_stack": [],
                        "processed": False,
                    }
                    all_jobs.append(job)
                    upsert_job(job)
                except Exception as e:
                    logger.debug(f"Naukri card error: {e}")

        except Exception as e:
            logger.error(f"Naukri scrape failed: {e}")

    log_action("scrape_done", f"Naukri scraped {len(all_jobs)} jobs", "info", {"count": len(all_jobs)})
    return all_jobs
