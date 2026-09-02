from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class WatchlistItem(Base):
    __tablename__ = 'watchlist'

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    company_name = Column(String, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)
