
import streamlit as st
import pandas as pd
from datetime import date, timedelta

from src.translation import translate_text
from src.sources.collector import collect_all_events


# Cache collected events separately from translations.
@st.cache_data(show_spinner="Loading local events...")
def load_events():
    return collect_all_events()


# Cache each translation by its original text.
# Cached results are reused across Streamlit reruns.
@st.cache_data(show_spinner=False)
def translate_cached(text: str) -> str:
    return translate_text(text, "nl", "en")


# Return translated or original text according to the selected language.
def display_text(text: str, language: str) -> str:
    if not text:
        return ""

    if language == "English":
        return translate_cached(text)

    return text


# Streamlit app layout
st.set_page_config(
    page_title="Local Events",
    page_icon="📅",
    layout="wide",
)

st.title("📅 Local Events")
st.caption("Discover what's happening in Delft and Rijswijk.")


# Refresh collected events without clearing reusable translations.
if st.button(
    "🔄 Refresh events",
    help="Fetch the latest events from all sources",
):
    load_events.clear()
    st.rerun()


today = date.today()

# Collect events from all configured sources.
events = load_events()


# Convert Event objects into rows for filtering and display.
# Keep original Dutch text in the data; translate only when displaying it.
df = pd.DataFrame([
    {
        "title": event.title,
        "location": event.location,
        "date": event.start_date,
        "end_date": event.end_date or event.start_date,
        "price_min": event.price_min,
        "price_max": event.price_max,
        "category": event.category,
        "description": event.description,
        "url": event.url,
        "source": event.source,
    }
    for event in events
])

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df["end_date"] = pd.to_datetime(df["end_date"])


# Sidebar filters
with st.sidebar:
    st.header("Filters")

    locations = st.multiselect(
        "Location",
        ["Delft", "Rijswijk"],
        default=["Delft", "Rijswijk"],
    )

    time_period = st.selectbox(
        "Time period",
        ["7 days", "14 days", "30 days", "90 days", "All upcoming"],
        index=2,
    )

    free_only = st.checkbox("Free events only")

    max_price = st.number_input(
        "Maximum price (€)",
        min_value=0.0,
        value=50.0,
        step=5.0,
    )

    language = st.radio(
        "Language",
        ["English", "Nederlands"],
        horizontal=True,
    )


# Apply location filters.
location_mask = pd.Series(False, index=df.index)

if "Delft" in locations:
    location_mask |= df["location"].str.contains(
        "Delft", case=False, na=False
    )

if "Rijswijk" in locations:
    location_mask |= df["location"].str.contains(
        "Rijswijk", case=False, na=False
    )


# Include ongoing events and events that have not yet started.
today_ts = pd.Timestamp(today)
date_mask = df["end_date"] >= today_ts

if time_period != "All upcoming":
    days = int(time_period.split()[0])
    period_end = pd.Timestamp(today + timedelta(days=days))
    date_mask &= df["date"] <= period_end

filtered = df[location_mask & date_mask].copy()


# Apply price filters.
if free_only:
    # Unknown prices are not assumed to be free.
    filtered = filtered[
        (filtered["price_min"] == 0)
        & (filtered["price_max"] == 0)
    ]
else:
    # Keep events with unknown prices; filter known prices by minimum price.
    filtered = filtered[
        filtered["price_min"].isna()
        | (filtered["price_min"] <= max_price)
    ]

filtered = filtered.sort_values("date")


# Summary metrics
col1, col2 = st.columns(2)

col1.metric("Upcoming events", len(filtered))

known_free = (
    (filtered["price_min"] == 0)
    & (filtered["price_max"] == 0)
)
col2.metric("Free events", int(known_free.sum()))

st.divider()


# Display event cards.
if filtered.empty:
    st.info("No events match your filters.")
else:
    for _, event in filtered.iterrows():
        with st.container(border=True):
            # Translate titles and descriptions only in English mode.
            title = display_text(event["title"], language)
            description = display_text(event["description"], language)

            st.subheader(title)

            # Format the event date or date range.
            start = event["date"].strftime("%a, %d %b %Y")
            end = event["end_date"].strftime("%d %b %Y")

            date_label = start
            if event["end_date"].date() != event["date"].date():
                date_label += f" – {end}"

            # Keep venue, category, and source names as collected.
            st.caption(
                f'{date_label} · {event["location"]} · '
                f'{event["category"]} · {event["source"]}'
            )

            # Display price information.
            if pd.isna(event["price_min"]):
                st.write("**Price:** Not listed")
            elif (
                event["price_min"] == 0
                and event["price_max"] == 0
            ):
                st.write("**Price:** Free")
            elif (
                pd.notna(event["price_max"])
                and event["price_max"] != event["price_min"]
            ):
                st.write(
                    f'**Price:** €{event["price_min"]:.2f} – '
                    f'€{event["price_max"]:.2f}'
                )
            else:
                st.write(f'**Price:** From €{event["price_min"]:.2f}')

            if description:
                st.write(description)

            if event["url"]:
                st.link_button("View event", event["url"])


st.caption(
    "Events collected from In Delft, UitRijswijk, and De Broodfabriek."
)