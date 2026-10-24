# FastAPI watchlist routes for retrieving stocks with live market data,
# adding new stocks, and removing stocks from the authenticated user's watchlist.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, Base, engine
from app.models.watchlist import WatchlistItem
from app.schemas.watchlist import WatchlistCreate, WatchlistResponse
from app.routers.auth import get_current_user
from app.models.user import User
from app.services import stock_service

# Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

@router.get("", response_model=List[dict])
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id).all()

    enriched = []
    for item in items:
        try:
            live_data = stock_service.get_full_stock_data(item.ticker)
        except Exception:
            # If Finnhub fails (e.g., invalid ticker or rate limit), return basic data.
            live_data = {
                "ticker": item.ticker,
                "name": item.company_name or item.ticker,
                "price": None,
                "change": None,
                "percent_change": None,
                "volume": None,
            }
        enriched.append({
            "id": item.id,
            "added_at": item.added_at,
            **live_data,
        })

    return enriched


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
        item: WatchlistCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    ticker_upper = item.ticker.upper()
    existing = db.query(WatchlistItem).filter(WatchlistItem.ticker == ticker_upper, WatchlistItem.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Watchlist item already exists")

    db_item = WatchlistItem(
        ticker = ticker_upper,
        company_name = item.company_name,
        user_id = current_user.id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(ticker: str, db: Session = Depends(get_db),
                          current_user: User = Depends(get_current_user),
):
    ticker_upper = ticker.upper()
    item = db.query(WatchlistItem).filter(
        WatchlistItem.ticker == ticker_upper,
        WatchlistItem.user_id == current_user.id,
).first()
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    db.delete(item)
    db.commit()
    return None