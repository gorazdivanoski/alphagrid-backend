from fastapi import APIRouter, HTTPException, Query
from app.services.stock_service import analyze_stock, stock_history, generate_ai_summary

router = APIRouter(prefix="/stocks", tags=["Stocks & Analysis"])

@router.get("/{ticker}")
def get_stock_analysis(ticker: str):

    data = analyze_stock(ticker)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
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
    data = generate_ai_summary(ticker)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data