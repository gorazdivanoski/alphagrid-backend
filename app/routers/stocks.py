from fastapi import APIRouter, HTTPException, Depends
from app.services import stock_service
from app.schemas.stock import StockQuote, SymbolSearchResult
from app.routers.auth import get_current_user
from app.models.user import User

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