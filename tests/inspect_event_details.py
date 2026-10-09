
import requests
from bs4 import BeautifulSoup

EVENTS = {
    "Delft": (
        "https://www.indelft.nl/nl/uitagenda/"
        "uitagenda-delft/1662788622/"
        "concert-accordeonensemble-opus-2"
    ),
    "Rijswijk": (
        "https://www.uitrijswijk.nl/"
        "evenement-Papier-Biennale-2026--Familielijnen-591"
    ),
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}

for name, url in EVENTS.items():
    print("\n" + "=" * 70)
    print(f"EVENT DETAILS: {name}")
    print("=" * 70)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=25,
        )

        print("HTTP status:", response.status_code)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        if soup.title:
            print("Page title:", soup.title.get_text(strip=True))

        # Print structured metadata where available.
        for tag in soup.find_all("meta"):
            prop = tag.get("property", "")
            name_attr = tag.get("name", "")
            content = tag.get("content", "")

            if content and (
                prop.startswith("og:")
                or name_attr in (
                    "description",
                    "date",
                    "startDate",
                )
            ):
                print(f"META {prop or name_attr}: {content}")

        # Print readable page text for date and price inspection.
        for element in soup.select(
            "script, style, nav, footer, noscript"
        ):
            element.decompose()

        text = soup.get_text(" ", strip=True)

        print("\nPAGE TEXT:")
        print(text[:4500])

    except requests.RequestException as error:
        print("Request failed:", error)