import finnhub
import yfinance as yf
from app.core.config import settings
from app.services.cache_service import quote_cache, profile_cache

client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)


def get_quote(ticker: str) -> dict:
    cached = quote_cache.get(ticker)
    if cached is not None:
        return cached

    data = client.quote(ticker)
    # data: {c: current, d: change, dp: percent, h: high, l: low, o: open, pc: prev_close, t: timestamp}
    if data.get("c") is None or data.get("c") == 0:
        raise ValueError(f"Нема податоци за ticker '{ticker}'")

    result = {
        "price": data["c"],
        "change": data["d"],
        "percent_change": data["dp"],
        "high": data["h"],
        "low": data["l"],
        "open": data["o"],
        "previous_close": data["pc"],
    }
    quote_cache.set(ticker, result)
    return result


def get_volume(ticker: str) -> int | None:
    cache_key = f"volume:{ticker}"
    cached = quote_cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        stock = yf.Ticker(ticker)
        info = stock.fast_info
        volume = info.get("last_volume") or info.get("lastVolume")
        if volume:
            quote_cache.set(cache_key, int(volume))
            return int(volume)
    except Exception:
        pass

    return None

def get_company_profile(ticker: str) -> dict:
    cached = profile_cache.get(ticker)
    if cached is not None:
        return cached

    profile = client.company_profile2(symbol=ticker)
    result = {
        "name": profile.get("name", ticker),
        "logo": profile.get("logo"),
        "industry": profile.get("finnhubIndustry"),
    }
    profile_cache.set(ticker, result)
    return result


def get_full_stock_data(ticker: str) -> dict:
    """Комбинира quote + profile + volume во еден response - за watchlist и stock detail."""
    ticker = ticker.upper()
    quote = get_quote(ticker)
    profile = get_company_profile(ticker)
    volume = get_volume(ticker)

    return {
        "ticker": ticker,
        "name": profile["name"],
        "price": quote["price"],
        "change": quote["change"],
        "percent_change": quote["percent_change"],
        "volume": volume,
    }


def search_symbols(query: str) -> list[dict]:
    results = client.symbol_lookup(query)
    return results.get("result", [])[:10]


def get_earnings_calendar(from_date: str, to_date: str) -> list[dict]:
    data = client.earnings_calendar(_from=from_date, to=to_date, symbol="", international=False)
    return data.get("earningsCalendar", [])