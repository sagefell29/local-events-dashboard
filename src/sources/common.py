import re
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}

MONTHS = {
    "januari": 1,
    "februari": 2,
    "maart": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "augustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}

DELFT_LISTING = (
    "https://www.indelft.nl/nl/uitagenda/uitagenda-delft"
)
RIJSWIJK_LISTING = (
    "https://www.uitrijswijk.nl/categorie-evenementen.php"
)
BROODFABRIEK_LISTING = (
    "https://de-broodfabriek.nl/evenementen/"
)


def fetch_soup(url: str) -> BeautifulSoup:
    """Download a page and return its parsed HTML."""
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=25,
    )
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def page_text(soup: BeautifulSoup) -> str:
    """Return readable text without scripts or navigation."""
    for element in soup.select(
        "script, style, nav, footer, noscript"
    ):
        element.decompose()

    return soup.get_text(" ", strip=True)


def parse_date(value: str):
    """Parse a Dutch date such as '15 november 2026'."""
    match = re.search(
        r"(\d{1,2})\s+"
        r"(januari|februari|maart|april|mei|juni|juli|"
        r"augustus|september|oktober|november|december)"
        r"\s+(\d{4})",
        value.lower(),
    )

    if not match:
        return None

    day, month, year = match.groups()

    try:
        return date(
            int(year),
            MONTHS[month],
            int(day),
        )
    except ValueError:
        return None




def extract_date_range(text: str):
    """Extract Dutch dates, including abbreviated and cross-month ranges."""
    text = text.lower()

    months_pattern = (
        r"januari|februari|maart|april|mei|juni|juli|"
        r"augustus|september|oktober|november|december"
    )

    # Format: 31 oktober t/m 1 november 2026
    cross_month_match = re.search(
        rf"(\d{{1,2}})\s+({months_pattern})\s+"
        rf"(?:t/m|tot en met|-|–)\s*"
        rf"(\d{{1,2}})\s+({months_pattern})\s+(\d{{4}})",
        text,
    )

    if cross_month_match:
        start_day, start_month, end_day, end_month, year = (
            cross_month_match.groups()
        )

        try:
            start = date(int(year), MONTHS[start_month], int(start_day))
            end = date(int(year), MONTHS[end_month], int(end_day))

            # Handle ranges crossing into the next calendar year.
            if end < start:
                end = date(int(year) + 1, MONTHS[end_month], int(end_day))

            return start, end
        except ValueError:
            return None, None

    # Format: 10 t/m 11 oktober 2026
    same_month_match = re.search(
        rf"(\d{{1,2}})\s+t/m\s+(\d{{1,2}})\s+"
        rf"({months_pattern})\s+(\d{{4}})",
        text,
    )

    if same_month_match:
        start_day, end_day, month_name, year = same_month_match.groups()

        try:
            month = MONTHS[month_name]
            return (
                date(int(year), month, int(start_day)),
                date(int(year), month, int(end_day)),
            )
        except ValueError:
            return None, None

    # Format: 20 september 2026 or
    # 20 september 2026 - 8 februari 2027
    full_date_pattern = rf"\d{{1,2}}\s+(?:{months_pattern})\s+\d{{4}}"
    matches = re.findall(full_date_pattern, text)

    if not matches:
        return None, None

    start = parse_date(matches[0])
    end = parse_date(matches[1]) if len(matches) >= 2 else None

    return start, end

def extract_price(text: str):
    """Extract a euro price, if one is clearly stated."""
    match = re.search(
        r"€\s*([\d.]+(?:,\d{2})?)",
        text,
    )

    if not match:
        return None, None

    value = float(
        match.group(1).replace(".", "").replace(",", ".")
    )
    return value, value


def extract_links(soup: BeautifulSoup, base_url: str):
    """Return unique event-like links from a listing."""
    links = []

    for anchor in soup.find_all("a", href=True):
        title = anchor.get_text(" ", strip=True)
        url = urljoin(base_url, anchor["href"])

        if not title or not url.startswith("http"):
            continue

        links.append((title, url))

    return list(dict.fromkeys(links))