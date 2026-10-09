import requests
import re

from src.models import Event
from src.sources.broodfabriek import collect_broodfabriek
from src.sources.indelft import collect_indelft
from src.sources.uitrijswijk import collect_uitrijswijk

def normalize_event_title(title: str) -> str:
    """Normalize event titles for cross-source duplicate matching."""
    title = title.lower()

    # Remove date phrases that some sources append to event titles.
    title = re.sub(
        r"\b\d{1,2}\s+t/m\s+\d{1,2}\s+"
        r"(?:januari|februari|maart|april|mei|juni|juli|"
        r"augustus|september|oktober|november|december)"
        r"(?:\s+\d{4})?\b",
        "",
        title,
    )

    # Remove punctuation and normalize whitespace.
    title = re.sub(r"[^a-z0-9]+", " ", title)
    return title.strip()



def deduplicate_events(events: list[Event]) -> list[Event]:
    """Remove obvious duplicates using title, date overlap, and venue."""
    unique_events = []

    def normalize(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

    for event in events:
        duplicate = None

        for existing in unique_events:
            # Factor 1: titles must match after basic normalization.
            same_title = (
                normalize_event_title(event.title)
                == normalize_event_title(existing.title)
            )

            # Factor 2: event date ranges must overlap.
            event_end = event.end_date or event.start_date
            existing_end = existing.end_date or existing.start_date
            dates_overlap = (
                event.start_date <= existing_end
                and existing.start_date <= event_end
            )

            # Factor 3: venues must match after basic normalization.
            same_location = (
                normalize(event.location)
                == normalize(existing.location)
            )

            if same_title and dates_overlap and same_location:
                duplicate = existing
                break

        if duplicate is None:
            unique_events.append(event)
            continue

        # Keep useful details from either version.
        if len(event.title) > len(duplicate.title):
            duplicate.title = event.title

        if not duplicate.description and event.description:
            duplicate.description = event.description

        if not duplicate.url and event.url:
            duplicate.url = event.url

    return unique_events


def collect_all_events() -> list[Event]:
    """Run all collectors, keeping failures isolated per source."""
    events = []

    collectors = [
        ("In Delft", collect_indelft),
        ("UitRijswijk", collect_uitrijswijk),
        ("De Broodfabriek", collect_broodfabriek),
    ]

    for name, collector in collectors:
        try:
            source_events = collector()
            print(f"{name}: collected {len(source_events)} events")
            events.extend(source_events)
        except requests.RequestException as error:
            print(f"{name}: source unavailable: {error}")

    unique_events = deduplicate_events(events)
    print(f"After deduplication: {len(unique_events)} events")

    return unique_events
