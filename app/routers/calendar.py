from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models.calendar_event import CalendarEvent
from app.schemas.calendar import CalendarEventCreate, CalendarEventResponse
from app.services import stock_service
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.watchlist import WatchlistItem

router = APIRouter(prefix="/calendar", tags=["Calendar"])

@router.get("/this-week")
def get_this_week_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.utcnow().date()
    week_end = today + timedelta(days=7)

    manual_events = db.query(CalendarEvent).filter(
        CalendarEvent.event_date >= today,
        CalendarEvent.event_date <= week_end,
    ).all()

    events = [
        {
            "title": e.title,
            "description": e.description,
            "date": e.event_date.strftime("%d/%m"),
            "details": e.details,
            "source": "manual",
        }
        for e in manual_events
    ]

    # Земи ги watchlist тикерите на тековниот корисник
    user_tickers = {
        item.ticker for item in
        db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id).all()
    }

    try:
        earnings = stock_service.get_earnings_calendar(
            today.isoformat(), week_end.isoformat()
        )
        for e in earnings:
            if e.get("symbol") not in user_tickers:
                continue  # прескокни компании надвор од watchlist-от
            events.append({
                "title": f"{e['symbol']} EARNINGS REPORT",
                "description": "Estimated EPS",
                "date": datetime.strptime(e["date"], "%Y-%m-%d").strftime("%d/%m"),
                "details": f"Estimated EPS: ${e.get('epsEstimate', 'N/A')}. Тримесечни детали и guidance информации.",
                "source": "earnings",
            })
    except Exception as ex:
        print(f"EARNINGS CALENDAR ERROR: {ex}")

    events.sort(key=lambda x: datetime.strptime(x["date"], "%d/%m"))
    return events

@router.post("/events", response_model=CalendarEventResponse, status_code=201)
def add_manual_event(
    event: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_event = CalendarEvent(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event