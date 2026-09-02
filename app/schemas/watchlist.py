from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class WatchlistCreate(BaseModel):
    ticker: str
    company_name: Optional[str] = None

class WatchlistResponse(BaseModel):
    id: int
    ticker: str
    company_name: Optional[str] = None
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)