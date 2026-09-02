from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, Base, engine
from app.models.watchlist import WatchlistItem
from app.schemas.watchlist import WatchlistCreate, WatchlistResponse

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

@router.get("/", response_model=List[WatchlistResponse])
def get_watchlist(db: Session = Depends(get_db)):
    return db.query(WatchlistItem).all()

@router.post("/", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(item: WatchlistItem, db: Session = Depends(get_db)):
    ticker_upper = item.ticker.upper()
    existing = db.query(WatchlistItem).filter(WatchlistItem.ticker == ticker_upper).first()
    if existing:
        raise HTTPException(status_code=400, detail="Watchlist item already exists")

    db_item = WatchlistItem(
        ticker = ticker_upper,
        company_name = item.company_name,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(ticker: str, db: Session = Depends(get_db)):
    ticker_upper = ticker.upper()
    item = db.query(WatchlistItem).filter(WatchlistItem.ticker == ticker_upper).first()
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    db.delete(item)
    db.commit()
    return None