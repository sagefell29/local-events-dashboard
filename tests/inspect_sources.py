
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

SOURCES = {
    "Delft": (
        "https://www.indelft.nl/nl/uitagenda/uitagenda-delft"
    ),
    "Rijswijk": (
        "https://www.uitrijswijk.nl/categorie-evenementen.php"
    ),
    "De Broodfabriek": (
        "https://de-broodfabriek.nl/evenementen/"
    ),
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}

for name, url in SOURCES.items():
    print("\n" + "=" * 70)
    print(f"SOURCE: {name}")
    print("=" * 70)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=25,
        )

        print("HTTP status:", response.status_code)
        print("Final URL:", response.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        if soup.title:
            print("Page title:", soup.title.get_text(strip=True))

        print("HTML length:", len(response.text))

        # Remove common navigation and footer sections to reduce noise.
        for element in soup.select(
            "header, footer, nav, script, style, noscript"
        ):
            element.decompose()

        print("\nCandidate links:")

        seen = set()
        count = 0

        for link in soup.find_all("a", href=True):
            title = link.get_text(" ", strip=True)
            href = urljoin(response.url, link["href"])

            if not title or len(title) < 5:
                continue

            if href in seen:
                continue

            seen.add(href)

            # Avoid printing generic buttons and very long text.
            if len(title) > 150:
                continue

            print(f"- {title}")
            print(f"  URL: {href}")

            count += 1

            if count >= 30:
                break

        print(f"\nCandidate links printed: {count}")

        # Look for date-related text in the page.
        text = soup.get_text(" ", strip=True)

        print("\nPage text sample:")
        print(text[:1800])

    except requests.RequestException as error:
        print("Request failed:", error)