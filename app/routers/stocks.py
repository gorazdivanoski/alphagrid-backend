# FastAPI stock routes for searching stocks, retrieving market data,
# price history, earnings reports, and AI-powered stock analysis and chat.

from fastapi import APIRouter, HTTPException, Depends, Query
from app.services import stock_service, ai_service
from app.schemas.stock import StockQuote, SymbolSearchResult
from app.routers.auth import get_current_user
from app.models.user import User
from app.schemas.ai import AIChatRequest, AIChatResponse

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("/search", response_model=list[SymbolSearchResult])
def search_stocks(q: str, current_user: User = Depends(get_current_user)):
    if len(q) < 1:
        raise HTTPException(status_code=400, detail="Пребарувањето мора да содржи барем еден карактер")
    try:
        results = stock_service.search_symbols(q)
        return [
            {"symbol": r["symbol"], "description": r["description"], "type": r["type"]}
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Finnhub грешка: {str(e)}")


@router.get("/{ticker}", response_model=StockQuote)
def get_stock(ticker: str, current_user: User = Depends(get_current_user)):
    try:
        return stock_service.get_full_stock_data(ticker)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Finnhub грешка: {str(e)}")


@router.get("/{ticker}/history")
def get_stock_history(
    ticker: str,
    period: str = Query(default="1mo", pattern="^(1d|5d|1mo|3mo|6mo|1y|5y)$"),
    current_user: User = Depends(get_current_user),
):
    try:
        return stock_service.get_price_history(ticker.upper(), period)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Грешка при вчитување историја: {str(e)}")


@router.get("/{ticker}/earnings")
def get_stock_earnings(ticker: str, current_user: User = Depends(get_current_user)):
    result = stock_service.get_next_earnings(ticker.upper())
    if result is None:
        return {"message": "Нема закажан earnings извештај во следните 4 месеци"}
    return result


@router.get("/{ticker}/ai-summary")
def get_ai_summary(ticker: str, current_user: User = Depends(get_current_user)):
    try:
        quote_data = stock_service.get_full_stock_data(ticker.upper())
        analysis = ai_service.get_stock_analysis(ticker.upper(), quote_data)
        return {"ticker": ticker.upper(), "analysis": analysis}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{ticker}/ai-chat", response_model=AIChatResponse)
def ai_chat(ticker: str, request: AIChatRequest, current_user: User = Depends(get_current_user)):
    try:
        quote_data = stock_service.get_full_stock_data(ticker.upper())
        answer = ai_service.get_followup_answer(
            ticker.upper(), quote_data, request.question, request.previous_analysis
        )
        return {"answer": answer}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))