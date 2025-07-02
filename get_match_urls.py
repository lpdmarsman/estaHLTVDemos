"""
CS2 LAN Match URL Scraper (HLTV.org)

This script scrapes HLTV.org for international LAN CS2 events within a specified date range,
extracting all match result URLs for those events.

Requirements:
    - selenium
    - beautifulsoup4
    - ChromeDriver installed and in PATH

Output:
    A text file containing all unique match URLs found within the date range.
"""

import time
import re
from datetime import datetime
from typing import List, Tuple, Set, Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ─────────── Configuration ─────────── #
START_DATE: datetime = datetime(2025, 6, 1)
END_DATE: datetime = datetime(2025, 6, 30)
BASE: str = "https://www.hltv.org"
EVENTS_URL: str = f"{BASE}/events/archive?eventType=INTLLAN"
REQUEST_DELAY: float = 1.0  # seconds
OUTPUT_FILE: str = f"match_urls_{START_DATE.date()}_{END_DATE.date()}.txt"

# ─────────── Global WebDriver ─────────── #
driver: Optional[webdriver.Chrome] = None


def relaunch_driver() -> None:
    """
    Launches or restarts a Selenium Chrome WebDriver with appropriate options.
    """
    global driver
    try:
        if driver:
            driver.quit()
    except Exception:
        pass
    time.sleep(1)

    options = Options()
    # options.add_argument("--headless") # Uncomment to run without GUI
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3") # Suppress logs: INFO=0, WARNING=1, LOG_ERROR=2, LOG_FATAL=3

    driver = webdriver.Chrome(options=options)


def accept_cookies(timeout: int = 5) -> None:
    """
    Clicks the cookie consent button if present.

    Args:
        timeout (int): Maximum time to wait for cookie prompt.
    """
    cookie_button_ids = [
        "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"
    ]

    for btn_id in cookie_button_ids:
        try:
            btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.ID, btn_id))
            )
            btn.click()
            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element((By.ID, btn_id))
            )
            return
        except Exception:
            continue


def fetch_event_list(start: datetime, end: datetime) -> List[Tuple[str, str]]:
    """
    Fetches a list of HLTV event names and URLs that occurred within a given date range.

    Args:
        start (datetime): Start date.
        end (datetime): End date.

    Returns:
        List[Tuple[str, str]]: List of event name and URL tuples.
    """
    relaunch_driver()
    driver.get(EVENTS_URL)
    accept_cookies()
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    events: List[Tuple[str, str]] = []

    for ev in soup.select("a.small-event.standard-box"):
        link = BASE + ev["href"]
        name = ev.select_one(".text-ellipsis").text.strip()
        spans = ev.select("tr.eventDetails span[data-unix]")

        if len(spans) < 2:
            continue

        start_ts = datetime.fromtimestamp(int(spans[0]["data-unix"]) / 1000)
        end_ts = datetime.fromtimestamp(int(spans[1]["data-unix"]) / 1000)

        if end_ts < start or start_ts > end:
            continue

        events.append((name, link))

    return events


def extract_match_urls(event_url: str) -> List[str]:
    """
    Extracts all match result URLs from an HLTV event.

    Args:
        event_url (str): URL to the HLTV event.

    Returns:
        List[str]: Sorted list of unique match result URLs.
    """
    relaunch_driver()
    driver.get(event_url)
    accept_cookies()
    time.sleep(1)

    # Attempt to find the event results page
    try:
        result_link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.sidebar-single-line-item[href^='/results?event=']"))
        )
        href = result_link.get_attribute("href")
        results_url = href if href.startswith("http") else BASE + href
    except Exception:
        event_id_match = re.search(r"/events/(\d+)/", event_url)
        results_url = (
            f"{BASE}/results?event={event_id_match.group(1)}" if event_id_match else event_url
        )

    relaunch_driver()
    driver.get(results_url)
    accept_cookies()
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    match_urls: Set[str] = {
        BASE + a["href"]
        for a in soup.select(".results-holder a.a-reset[href^='/matches/']")
    }

    return sorted(match_urls)


def main() -> None:
    """
    Main function to fetch events and extract all associated match URLs.
    Writes all results to a text file.
    """
    print(f"Searching CS2 Intl LAN events {START_DATE.date()} → {END_DATE.date()}...")
    events = fetch_event_list(START_DATE, END_DATE)
    print(f"Found {len(events)} event(s):")
    for name, _ in events:
        print(" •", name)
    print()

    all_matches: Set[str] = set()

    for name, url in events:
        print(f"→ Scraping matches for '{name}'…", end=" ")
        try:
            matches = extract_match_urls(url)
            all_matches.update(matches)
            print(f"{len(matches)} matches found")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(REQUEST_DELAY)

    sorted_matches = sorted(all_matches)
    print(f"\nTotal unique CS2 LAN matches found: {len(sorted_matches)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for match_url in sorted_matches:
            f.write(match_url + "\n")

    if driver:
        driver.quit()


if __name__ == "__main__":
    main()
