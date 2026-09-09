from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CalendarEventCreate(BaseModel):
    title: str
    description: str
    event_date: datetime
    details: Optional[str] = None

class CalendarEventResponse(BaseModel):
    id: int
    title: str
    description: str
    event_date: datetime
    details: Optional[str] = None
    source: str = "manual"   # "manual" или "earnings" - да разликуваме на фронт

    model_config = ConfigDict(from_attributes=True)