from pydantic import BaseModel
from typing import Optional

# Pydantic schemas for stock quotes and symbol search results,
# including pricing, trading volume, company details, and logo.

class SymbolSearchResult(BaseModel):
    symbol: str
    description: str
    type: str

class StockQuote(BaseModel):
    ticker: str
    name: str
    price: float
    change: float
    percent_change: float
    volume: Optional[int] = None
    logo: Optional[str] = None