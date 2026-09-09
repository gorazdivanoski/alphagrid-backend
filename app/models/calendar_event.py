from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)          # "FED"
    description = Column(String, nullable=False)    # "Important federal reserve feed"
    event_date = Column(DateTime, nullable=False)    # 2026-09-05
    details = Column(Text, nullable=True)             # долг текст за expanded view
    created_at = Column(DateTime, default=datetime.utcnow)