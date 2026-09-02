from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WatchlistCreate(BaseModel):
    title: str
    company_name: Optional[str] = None

class WatchlistResponse(BaseModel):
    id: int
    ticker: str
    company_name: Optional[str] = None
    added_at: datetime

    class Config:
        from_attributes = True