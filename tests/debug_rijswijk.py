
from ..src.sources1 import (
    RIJSWIJK_LISTING,
    fetch_soup,
    extract_links,
    extract_date_range,
    page_text,
    extract_rijswijk_venue
)

print("1. Fetching the listing...")
listing = fetch_soup(RIJSWIJK_LISTING)

links = extract_links(listing, RIJSWIJK_LISTING)

print("Total links extracted:", len(links))

event_links = [
    (title, url)
    for title, url in links
    if "/evenement-" in url
]

print("Event links matching the collector filter:", len(event_links))

for title, url in event_links:
    print(f"  {title}: {url}")

if not event_links:
    print("\nNo event links passed the filter.")
    print("Raw hrefs containing 'evenement':")

    for anchor in listing.find_all("a", href=True):
        if "evenement" in anchor["href"].lower():
            print(anchor.get_text(" ", strip=True), anchor["href"])

else:
    title, url = event_links[0]

    print("\n2. Inspecting the first event detail page...")
    print("URL:", url)

    detail = fetch_soup(url)

    print("\nPage title:", detail.title.get_text(strip=True)
          if detail.title else "No title")

    print("\nHeadings found:")
    for heading in detail.find_all(["h1", "h2", "h3"]):
        print(f"  <{heading.name}> {heading.get_text(' ', strip=True)}")

    text = page_text(detail)

    print("\n3. Date extraction test:")
    print("Extracted dates:", extract_date_range(text))

    print("\n4. Relevant page text:")
    print(text[:1800])
    
    print("\n5. Inspecting venue-related HTML:")
    for element in detail.find_all(["h2", "h3", "p", "div", "span"]):
        value = element.get_text(" ", strip=True)

        if any(
            keyword in value.lower()
            for keyword in [
                "museum rijswijk",
                "de broodfabriek",
                "locatie",
                "adres",
            ]
        ):
            if value:
                print(element.name, repr(value[:300]))