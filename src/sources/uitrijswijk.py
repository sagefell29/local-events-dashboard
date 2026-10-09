import requests
import re
from src.models import Event
from src.sources.common import (
    fetch_soup,
    page_text,
    extract_date_range,
    extract_links
)

RIJSWIJK_LISTING = (
    "https://www.uitrijswijk.nl/categorie-evenementen.php"
)

def extract_uitrijswijk_venue(soup, text: str) -> str:
    """Extract a venue from an UitRijswijk event page."""
    # Look for the element containing the event date range.
    for element in soup.find_all(["span", "p", "div"]):
        value = element.get_text(" ", strip=True)

        if (
            re.search(r"\d{1,2}\s+\w+\s+\d{4}", value, re.IGNORECASE)
            and len(value) < 250
        ):
            # Remove the date portion and keep the remaining text.
            cleaned = re.sub(
                r".*?\d{1,2}\s+\w+\s+\d{4}\s*-\s*"
                r"(?:\w+\s+)?\d{1,2}\s+\w+\s+\d{4}\s*",
                "",
                value,
                count=1,
                flags=re.IGNORECASE,
            ).strip(" -–|")

            # Remove leading opening hours, e.g. "12.00 - 20.30 uur".
            cleaned = re.sub(
                r"^\d{1,2}[.:]\d{2}\s*-\s*"
                r"\d{1,2}[.:]\d{2}\s*(?:uur)?\s*",
                "",
                cleaned,
                count=1,
                flags=re.IGNORECASE,
            ).strip()

            if cleaned and len(cleaned) < 100:
                return cleaned

    return "Rijswijk"

def collect_uitrijswijk() -> list[Event]:
    events = []
    soup = fetch_soup(RIJSWIJK_LISTING)

    # Keep one link per event URL. The listing repeats links as
    # both the event title and "Meer informatie".
    links = []
    seen_urls = set()

    for title, url in extract_links(soup, RIJSWIJK_LISTING):
        if "/evenement-" in url and url not in seen_urls:
            links.append((title, url))
            seen_urls.add(url)

    for _, url in links:
        try:
            detail = fetch_soup(url)
            text = page_text(detail)

            # UitRijswijk uses h2 rather than h1 for event titles.
            heading = detail.find(["h1", "h2"])
            title = (
                heading.get_text(" ", strip=True)
                if heading
                else ""
            )

            # Fallback to the Open Graph title if no heading is found.
            if not title:
                meta_title = detail.find(
                    "meta", property="og:title"
                )
                if meta_title:
                    title = meta_title.get("content", "").strip()

            if not title:
                print(f"Skipping page with no title: {url}")
                continue

            start, end = extract_date_range(text)

            if start is None:
                print(f"Skipping page with no recognised date: {url}")
                continue

            events.append(
                Event(
                    title=title,
                    location=extract_uitrijswijk_venue(detail, text),
                    start_date=start,
                    end_date=end,
                    description=text,
                    source="UitRijswijk",
                    url=url,
                )
            )

        except requests.RequestException as error:
            print(f"Skipping UitRijswijk page {url}: {error}")

    return events