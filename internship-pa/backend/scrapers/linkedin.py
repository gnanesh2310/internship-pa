"""
LinkedIn scraper — uses Playwright for JS-rendered content.
Scrapes internship listings from LinkedIn Jobs.
Note: Run `playwright install chromium` once before using.
"""
import logging
import time
import random
from database.queries import upsert_job, log_action

logger = logging.getLogger(__name__)

SEARCH_QUERIES = [
    ("web development intern", "India"),
    ("python flask intern", "India"),
    ("frontend react intern", "India"),
    ("embedded systems intern", "India"),
    ("iot intern", "India"),
    ("research intern electrical", "India"),
]


def scrape() -> list[dict]:
    """Scrape LinkedIn internship listings using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
        return []

    all_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        for keywords, location in SEARCH_QUERIES:
            try:
                kw_encoded = keywords.replace(" ", "%20")
                loc_encoded = location.replace(" ", "%20")
                url = f"https://www.linkedin.com/jobs/search/?keywords={kw_encoded}&location={loc_encoded}&f_E=1&f_JT=I&sortBy=DD"

                page.goto(url, timeout=20000)
                time.sleep(random.uniform(2, 4))

                # Scroll to load more results
                for _ in range(3):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1)

                job_cards = page.query_selector_all(".job-search-card, .jobs-search__results-list li")
                logger.info(f"LinkedIn: found {len(job_cards)} cards for '{keywords}'")

                for card in job_cards[:15]:
                    try:
                        company_el = card.query_selector(".job-search-card__subtitle, .base-search-card__subtitle")
                        role_el = card.query_selector(".job-search-card__title, .base-search-card__title")
                        location_el = card.query_selector(".job-search-card__location, .job-search-card__location")
                        link_el = card.query_selector("a[href*='/jobs/view/']")

                        if not company_el or not role_el:
                            continue

                        job = {
                            "company_name": company_el.inner_text().strip(),
                            "role_title": role_el.inner_text().strip(),
                            "location": location_el.inner_text().strip() if location_el else "India",
                            "source": "linkedin",
                            "job_url": link_el.get_attribute("href") if link_el else "",
                            "tech_stack": [],
                            "processed": False,
                        }
                        all_jobs.append(job)
                        upsert_job(job)

                    except Exception as e:
                        logger.debug(f"LinkedIn card parse error: {e}")

                time.sleep(random.uniform(3, 6))

            except Exception as e:
                logger.error(f"LinkedIn scrape failed for '{keywords}': {e}")

        browser.close()

    log_action("scrape_done", f"LinkedIn scraped {len(all_jobs)} jobs", "info", {"count": len(all_jobs)})
    return all_jobs
