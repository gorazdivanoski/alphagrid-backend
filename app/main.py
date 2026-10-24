from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import user, watchlist  # важно - експлицитен import пред create_all
from app.routers import stocks, watchlist as watchlist_router, auth, calendar

# Main FastAPI application setup for AlphaGrid,
# including database initialization, CORS configuration,
# API router registration, and a root status endpoint.

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AlphaGrid API",
    description="Интелигентен систем за финансиска анализа, технички индикатори и макро сообраќај.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(watchlist_router.router)
app.include_router(calendar.router)

@app.get("/")
def read_root():
    return {
        "project": "AlphaGrid API",
        "status": "Online",
        "message": "This is the backend of the AlphaGrid API.",
    }