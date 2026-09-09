from pydantic import BaseModel
from typing import Optional

class StockQuote(BaseModel):
    ticker: str
    name: str
    price: float
    change: float
    percent_change: float
    volume: Optional[int] = None

class SymbolSearchResult(BaseModel):
    symbol: str
    description: str
    type: str