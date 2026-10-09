import requests
import re
from src.models import Event
from src.sources.common import (
    fetch_soup,
    page_text,
    extract_date_range,
    extract_links,
    extract_price,
)

DELFT_LISTING = (
    "https://www.indelft.nl/nl/uitagenda/uitagenda-delft"
)

def collect_indelft() -> list[Event]:
    """Collect events from In Delft detail pages."""
    events = []
    soup = fetch_soup(DELFT_LISTING)

    links = [
        (title, url)
        for title, url in extract_links(soup, DELFT_LISTING)
        if "/nl/uitagenda/uitagenda-delft/" in url
        and url.rstrip("/") != DELFT_LISTING.rstrip("/")
    ]

    # Only follow unique event pages, not category or navigation links.
    seen = set()

    for _, url in links:
        if url in seen:
            continue
        seen.add(url)

        try:
            detail = fetch_soup(url)
            text = page_text(detail)

            title = (
                detail.select_one("h1")
                or detail.select_one("meta[property='og:title']")
            )

            if title and title.name == "meta":
                title_text = title.get("content", "").strip()
            elif title:
                title_text = title.get_text(" ", strip=True)
            else:
                title_text = ""

            if not title_text:
                continue

            start, end = extract_date_range(text)
            if start is None:
                continue

            price_min, price_max = extract_price(text)

            description = ""
            description_match = re.search(
                r"Meer informatie\s+(.*?)\s+Wanneer\b",
                text,
                re.IGNORECASE,
            )
            if description_match:
                description = description_match.group(1).strip()

            location = "Delft"
            venue_match = re.search(
                r"Contact\s+(.+?)\s+Plan je route",
                text,
                re.IGNORECASE,
            )
            if venue_match:
                location = venue_match.group(1).strip()

            events.append(
                Event(
                    title=title_text,
                    location=location,
                    start_date=start,
                    end_date=end,
                    description=description,
                    price_min=price_min,
                    price_max=price_max,
                    source="In Delft",
                    url=url,
                )
            )

        except requests.RequestException as error:
            print(f"Skipping Delft page {url}: {error}")

    return events