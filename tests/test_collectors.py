
from datetime import date

from src.sources1 import collect_all_events


if __name__ == "__main__":
    events = collect_all_events()

    print(f"\nTotal collected: {len(events)}")

    today = date.today()

    upcoming = sorted(
        (
            event
            for event in events
            if (
                event.end_date or event.start_date
            ) >= today
        ),
        key=lambda event: event.start_date,
    )

    for event in upcoming[:25]:
        date_label = event.start_date.strftime("%d %b %Y")

        if event.end_date:
            date_label += (
                " - " + event.end_date.strftime("%d %b %Y")
            )

        price_label = (
            f"€{event.price_min:.2f}"
            if event.price_min is not None
            else "Price unknown"
        )

        print(f"\n{event.title}")
        print(f"  Date: {date_label}")
        print(f"  Location: {event.location}")
        print(f"  Price: {price_label}")
        print(f"  Source: {event.source}")
        print(f"  URL: {event.url}")