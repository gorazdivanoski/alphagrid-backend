import logging
import requests
from app.core.config import settings
from app.services.cache_service import TTLCache

# Service for retrieving and caching macroeconomic events from FRED,
# including CPI, employment, GDP releases, and scheduled FOMC decisions.

logger = logging.getLogger(__name__)

macro_cache = TTLCache(ttl_seconds=3600 * 12) # 12 hours

# Key FRED release IDs relevant to investors.
# Release 101 (FOMC Press Release) is intentionally excluded because
# include_release_dates_with_no_data=true returns placeholder dates for every day.
# FOMC decisions are retrieved from the official calendar below.
RELEVANT_RELEASES = {
    10: "CPI (Инфлација)",
    50: "Employment Situation (Работни места)",
    53: "GDP",
}

# FOMC decision dates (second day of each meeting), based on the official
# Federal Reserve calendar:
# https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
# Update annually.
FOMC_DECISION_DATES_2026 = [
    "2026-01-28",  # January 27-28 meeting
    "2026-03-18",  # March 17-18 meeting
    "2026-04-29",  # April 28-29 meeting
    "2026-06-17",  # June 16-17 meeting
    "2026-07-29",  # July 28-29 meeting
    "2026-09-16",  # September 15-16 meeting
    "2026-10-28",  # October 27-28 meeting
    "2026-12-09",  # December 8-9 meeting
]

def get_macro_events(start_date: str, end_date: str) -> list[dict]:
    cache_key = f"macro:{start_date}:{end_date}"
    cached = macro_cache.get(cache_key)
    if cached is not None:
        return cached

    events = []
    fred_ok = False

    try:
        response = requests.get(
            "https://api.stlouisfed.org/fred/releases/dates",
            params={
                "api_key": settings.FRED_API_KEY,
                "file_type": "json",
                "realtime_start": start_date,
                "realtime_end": end_date,
                "include_release_dates_with_no_data": "true",
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        fred_ok = True

        seen = set()
        for item in data.get("release_dates", []):
            release_id = item.get("release_id")
            if release_id not in RELEVANT_RELEASES:
                continue
            key = (release_id, item["date"])
            if key in seen:
                continue
            seen.add(key)
            events.append({
                "title": RELEVANT_RELEASES[release_id],
                "description": "Економски извештај",
                "date_iso": item["date"],
                "details": f"Официјален датум на објавување: {item['date']}",
                "source": "macro",
            })
    except Exception as e:
        logger.warning("FRED API грешка: %s", e)

    for decision_date in FOMC_DECISION_DATES_2026:
        if start_date <= decision_date <= end_date:
            events.append({
                "title": "FOMC решение за каматна стапка",
                "description": "Одлука на Federal Reserve",
                "date_iso": decision_date,
                "details": "Федералните резерви ја објавуваат одлуката за монетарна политика и каматните стапки.",
                "source": "macro",
            })

    # Do not cache if the FRED API fails to avoid caching incomplete data for 12 hours.
    if fred_ok:
        macro_cache.set(cache_key, events)
    return events
