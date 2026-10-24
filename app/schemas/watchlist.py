from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Pydantic schemas for creating and retrieving watchlist items,
# including stock details, date added, and ORM compatibility.

class WatchlistCreate(BaseModel):
    ticker: str
    company_name: Optional[str] = None

class WatchlistResponse(BaseModel):
    id: int
    ticker: str
    company_name: Optional[str] = None
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)