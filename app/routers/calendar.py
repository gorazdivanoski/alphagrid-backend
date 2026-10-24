import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.watchlist import WatchlistItem
from app.services import stock_service, macro_service
from app.routers.auth import get_current_user
from app.models.user import User

try:
    from zoneinfo import ZoneInfo
    LOCAL_TZ = ZoneInfo("Europe/Skopje")
except Exception:  # нема tzdata - користи UTC
    LOCAL_TZ = timezone.utc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calendar", tags=["Calendar"])


def _fmt_eps(value) -> str:
    if value is None:
        return "N/A"
    try:
        return f"${float(value):.2f}"
    except (TypeError, ValueError):
        return "N/A"


@router.get("/this-week")
def get_this_week_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(LOCAL_TZ).date()
    today_iso = today.isoformat()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    events = []

    # Автоматски macro настани (CPI, работни места, GDP, FOMC)
    macro_events = macro_service.get_macro_events(
        start_of_week.isoformat(), end_of_week.isoformat()
    )
    for e in macro_events:
        events.append({
            **e,
            "date": datetime.strptime(e["date_iso"], "%Y-%m-%d").strftime("%d/%m"),
            "is_past": e["date_iso"] < today_iso,
        })

    # Автоматски earnings за watchlist тикерите
    user_tickers = {
        item.ticker for item in
        db.query(WatchlistItem).filter(WatchlistItem.user_id == current_user.id).all()
    }

    try:
        earnings = stock_service.get_earnings_calendar(
            start_of_week.isoformat(), end_of_week.isoformat()
        )
        for e in earnings:
            if e.get("symbol") not in user_tickers:
                continue
            eps = _fmt_eps(e.get("epsEstimate"))
            events.append({
                "title": f"{e['symbol']} EARNINGS REPORT",
                "description": f"Estimated EPS: {eps}",
                "date": datetime.strptime(e["date"], "%Y-%m-%d").strftime("%d/%m"),
                "date_iso": e["date"],
                "details": f"Estimated EPS: {eps}. Тримесечни детали и guidance информации.",
                "source": "earnings",
                "is_past": e["date"] < today_iso,
            })
    except Exception as ex:
        logger.warning("EARNINGS CALENDAR ERROR: %s", ex)

    # Хронолошки; на ист ден macro пред earnings
    events.sort(key=lambda x: (x["date_iso"], 0 if x["source"] == "macro" else 1, x["title"]))
    return events
