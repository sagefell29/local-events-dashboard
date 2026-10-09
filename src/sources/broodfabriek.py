from urllib.parse import urljoin
from src.models import Event
from src.sources.common import (
    fetch_soup,
    extract_date_range,
)

BROODFABRIEK_LISTING = (
    "https://de-broodfabriek.nl/evenementen/"
)

def collect_broodfabriek() -> list[Event]:
    """Collect dated events from De Broodfabriek's agenda."""
    events = []
    soup = fetch_soup(BROODFABRIEK_LISTING)

    # The agenda lists titles and dates in its visible link text.
    for anchor in soup.find_all("a", href=True):
        title_text = anchor.get_text(" ", strip=True)

        if not title_text:
            continue

        start, end = extract_date_range(title_text)

        if start is None:
            continue

        url = urljoin(BROODFABRIEK_LISTING, anchor["href"])

        # These links often lead directly to the event organiser.
        events.append(
            Event(
                title=title_text,
                location="De Broodfabriek, Rijswijk",
                start_date=start,
                end_date=end,
                source="De Broodfabriek",
                url=url,
            )
        )

    return events