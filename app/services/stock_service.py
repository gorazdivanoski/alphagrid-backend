import time
from datetime import date, timedelta
import finnhub
import yfinance as yf
from app.core.config import settings
from app.services.cache_service import quote_cache, profile_cache

# Stock market service for retrieving real-time quotes, company profiles,
# trading volume, price history, and earnings data using Finnhub and Yahoo Finance.
# Includes caching to reduce API requests and improve performance.

client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)


def get_quote(ticker: str) -> dict:
    cached = quote_cache.get(ticker)
    if cached is not None:
        return cached

    data = client.quote(ticker)
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
        "logo": profile.get("logo"),
    }

def search_symbols(query: str) -> list[dict]:
    results = client.symbol_lookup(query)
    return results.get("result", [])[:10]


def get_earnings_calendar(from_date: str, to_date: str) -> list[dict]:
    data = client.earnings_calendar(_from=from_date, to=to_date, symbol="", international=False)
    return data.get("earningsCalendar", [])


def get_price_history(ticker: str, period: str = "1mo") -> list[dict]:
    cache_key = f"history:{ticker}:{period}"
    cached = quote_cache.get(cache_key)
    if cached is not None:
        return cached

    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    if hist.empty:
        raise ValueError(f"Нема историски податоци за '{ticker}'")

    result = [
        {
            "date": index.strftime("%Y-%m-%d"),
            "close": round(row["Close"], 2),
        }
        for index, row in hist.iterrows()
    ]

    quote_cache.set(cache_key, result)
    return result


def get_next_earnings(ticker: str) -> dict | None:
    today = date.today()
    future = today + timedelta(days=120)

    try:
        data = client.earnings_calendar(
            _from=today.isoformat(), to=future.isoformat(), symbol=ticker, international=False
        )
        events = data.get("earningsCalendar", [])
        if not events:
            return None

        next_event = sorted(events, key=lambda e: e["date"])[0]
        return {
            "date": next_event["date"],
            "eps_estimate": next_event.get("epsEstimate"),
            "revenue_estimate": next_event.get("revenueEstimate"),
        }
    except Exception:
        return None