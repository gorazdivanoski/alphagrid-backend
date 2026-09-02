import requests
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from app.services.ai_service import generate_real_ai_analysis

def analyze_stock(ticker: str):
    try:
        stock = yf.Ticker(ticker.upper())

        df = stock.history(period='1y')

        if df.empty:
            return {"error": f"No data found for {ticker.upper()}"}


        df.ta.rsi(length=14, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.sma(length=200, append=True)

        latest = df.iloc[-1]
        current_price = latest['Close']

        rsi = latest.get('RSI_14', None)
        sma_50 = latest.get('SMA_50', None)
        sma_200 = latest.get('SMA_200', None)

        verdict = "Neutral"
        if rsi and rsi < 30:
            verdict = "Oversold (Потенцијална можност за купување)"
        elif rsi and rsi > 70:
            verdict = "Overbought (Внимавај, можност за корекција)"


        next_earnings_date = "N/A"
        try:
            calendar = stock.calendar
            if isinstance(calendar, dict):
                if "Earnings Date" in calendar and calendar["Earnings Date"]:
                    next_earnings_date = str(calendar["Earnings Date"][0])
                elif 0 in calendar:
                    next_earnings_date = str(calendar[0])
            elif hasattr(calendar, "empty") and not calendar.empty:
                if "Earnings Date" in calendar:
                    next_earnings_date = str(calendar["Earnings Date"].iloc[0])
        except Exception:
            next_earnings_date = "N/A"

        return {
            "ticker": ticker.upper(),
            "currency": stock.info.get("currency", "USD"),
            "sector": stock.info.get("sector", "N/A"),
            "current_price": round(current_price, 2),
            "indicators": {
                "rsi_14": round(rsi, 2) if pd.notna(rsi) else None,
                "sma_50": round(sma_50, 2) if pd.notna(sma_50) else None,
                "sma_200": round(sma_200, 2) if pd.notna(sma_200) else None,
            },
            "technical_verdict": verdict,
            "next_earnings_date": next_earnings_date,
            "business_summary": stock.info.get("longBusinessSummary", "Описот не е достапен.")[:400] + "..."
        }
    except Exception as e:
        return {"error": str(e)}

def stock_history(ticker: str, period: str = "1y"):
    try:
        stock = yf.Ticker(ticker.upper())
        df = stock.history(period=period)

        if df.empty:
            return {"error": f"No data found for {ticker.upper()}"}

        df.reset_index(inplace=True)
        chart_data = []

        for _, row in df.iterrows():
            chart_data.append({
                "date": row["Date"].strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"]),
            })

        return {
            "ticker": ticker.upper(),
            "period": period,
            "data_points": len(chart_data),
            "history": chart_data
        }
    except Exception as e:
        return {"error": str(e)}


def generate_ai_summary(ticker: str):
    data = analyze_stock(ticker)

    if "error" in data:
        return data

    return generate_real_ai_analysis(data)

def search_stocks(query: str) -> list:
    if not query or len(query.strip()) < 1:
        return []

    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=8&newsCount=0"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        results = []
        for quote in data.get("quotes", []):
            if quote.get("quoteType") in ["EQUITY", "ETF"]:
                results.append({
                    "symbol": quote.get("symbol"),
                    "name": quote.get("shortname") or quote.get("longname"),
                    "exchange": quote.get("exchange"),
                    "type": quote.get("quoteType"),
                })
        return results
    except Exception:
        return []
