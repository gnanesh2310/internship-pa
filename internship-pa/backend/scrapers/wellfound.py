"""
Wellfound (AngelList) scraper — startup internships.
Uses Playwright since Wellfound is heavily JS-rendered.
"""
import logging
import time
import random
from database.queries import upsert_job, log_action

logger = logging.getLogger(__name__)

SEARCH_URLS = [
    "https://wellfound.com/jobs?role=software-engineer&jobType=internship&remote=true",
    "https://wellfound.com/jobs?role=frontend-engineer&jobType=internship",
    "https://wellfound.com/jobs?role=full-stack-engineer&jobType=internship&remote=true",
]


def scrape() -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright not installed.")
        return []

    all_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")

        for url in SEARCH_URLS:
            try:
                page.goto(url, timeout=25000, wait_until="networkidle")
                time.sleep(random.uniform(2, 4))

                cards = page.query_selector_all("[data-test='StartupResult'], .styles_component__2_DGB")

                for card in cards[:15]:
                    try:
                        company_el = card.query_selector("h2, .styles_name__2cvFb")
                        role_el = card.query_selector("a[href*='/jobs/'], .styles_jobTitle__2pGkU")
                        location_el = card.query_selector(".styles_locationTagStyle__a3s1n")
                        link_el = card.query_selector("a[href*='/jobs/']")
                        stack_els = card.query_selector_all(".styles_tagStyle__1N4JL, [data-test='SkillTag']")

                        if not company_el or not role_el:
                            continue

                        job = {
                            "company_name": company_el.inner_text().strip(),
                            "role_title": role_el.inner_text().strip(),
                            "location": location_el.inner_text().strip() if location_el else "Remote",
                            "source": "wellfound",
                            "job_url": f"https://wellfound.com{link_el.get_attribute('href')}" if link_el else url,
                            "tech_stack": [el.inner_text().strip() for el in stack_els[:8]],
                            "processed": False,
                        }
                        all_jobs.append(job)
                        upsert_job(job)

                    except Exception as e:
                        logger.debug(f"Wellfound card error: {e}")

                time.sleep(random.uniform(4, 8))

            except Exception as e:
                logger.error(f"Wellfound scrape failed for {url}: {e}")

        browser.close()

    log_action("scrape_done", f"Wellfound scraped {len(all_jobs)} jobs", "info", {"count": len(all_jobs)})
    return all_jobs
