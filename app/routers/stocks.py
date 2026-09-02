from fastapi import APIRouter, HTTPException, Query
from app.services.stock_service import analyze_stock, stock_history, search_stocks
from app.services.ai_service import generate_real_ai_analysis
from app.services.cache_service import stock_cache, ai_cache

router = APIRouter(prefix="/stocks", tags=["Stocks & Analysis"])

@router.get("/search")
def search_ticker(q: str):
    return search_stocks(q)

@router.get("/{ticker}")
def get_stock_analysis(ticker: str):
    ticker_upper = ticker.upper()

    if ticker_upper in stock_cache:
        return stock_cache[ticker_upper]

    data = analyze_stock(ticker_upper)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])

    stock_cache[ticker_upper] = data
    return data

@router.get("/{ticker}/history")
def get_stock_history(
        ticker: str,
        period: str = Query("1y", description="The period of the historical data"),
):
    data = stock_history(ticker, period)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

@router.get("/{ticker}/ai-summary")
def get_ai_summary(ticker: str):
    ticker_upper = ticker.upper()

    if ticker_upper in ai_cache:
        return ai_cache[ticker_upper]

    if ticker_upper in stock_cache:
        stock_data = stock_cache[ticker_upper]
    else:
        stock_data = analyze_stock(ticker_upper)
        if "error" in stock_data:
            raise HTTPException(status_code=404, detail=stock_data["error"])
        stock_cache[ticker_upper] = stock_data

    ai_response = generate_real_ai_analysis(stock_data)
    if "error" in ai_response:
        raise HTTPException(status_code=500, detail=ai_response["error"])

    ai_cache[ticker_upper] = ai_response
    return ai_response
