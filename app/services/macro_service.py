import logging

import requests
from app.core.config import settings
from app.services.cache_service import TTLCache

logger = logging.getLogger(__name__)

macro_cache = TTLCache(ttl_seconds=3600 * 12)  # 12 часа, macro датумите не се менуваат често

# Клучни FRED release ID-иња релевантни за инвеститори.
# Забелешка: release 101 (FOMC Press Release) е намерно исклучен - со
# include_release_dates_with_no_data=true враќа placeholder датум за секој ден.
# FOMC одлуките се земаат од официјалниот календар подолу.
RELEVANT_RELEASES = {
    10: "CPI (Инфлација)",
    50: "Employment Situation (Работни места)",
    53: "GDP",
}

# Датуми на FOMC ОДЛУКА (вториот ден од состанокот), според официјалниот
# календар на Federal Reserve:
# https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
# Ажурирај еднаш годишно.
FOMC_DECISION_DATES_2026 = [
    "2026-01-28",  # состанок 27-28 јануари
    "2026-03-18",  # 17-18 март
    "2026-04-29",  # 28-29 април
    "2026-06-17",  # 16-17 јуни
    "2026-07-29",  # 28-29 јули
    "2026-09-16",  # 15-16 септември
    "2026-10-28",  # 27-28 октомври
    "2026-12-09",  # 8-9 декември
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

    # Не кеширај ако FRED падна - инаку грешката останува 12 часа
    if fred_ok:
        macro_cache.set(cache_key, events)
    return events
