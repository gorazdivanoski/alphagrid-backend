# AlphaGrid Backend

REST API for **AlphaGrid**, a stock-market dashboard. It handles user accounts, personal watchlists, live quotes, price history, earnings data, a weekly calendar of market-moving events, and AI-generated stock briefings.

The web interface lives in a separate repository: **alphagrid-frontend**.

## Features

- **Authentication:** register and log in; JWT access tokens (bcrypt-hashed passwords).
- **Watchlist:** add and remove tickers per user; returns live price, daily change, volume and company logo.
- **Stocks:** symbol search, full quote, price history (1d to 5y) and the next earnings report.
- **AI analysis:** a short briefing for any ticker plus follow-up questions, powered by Google Gemini. Answers are in Macedonian and never include buy/sell/hold advice.
- **Weekly calendar:** macro releases (CPI, employment, GDP) from FRED, FOMC rate-decision dates, and earnings reports for the tickers in the user's watchlist.
- **Caching:** short in-memory caches (15 s for quotes, 12 h for macro dates) to stay within API rate limits.

## Tech stack

Python 3.12, FastAPI, SQLAlchemy with SQLite, python-jose (JWT), bcrypt, Finnhub, yfinance, Google Gen AI SDK, Uvicorn.

## Getting started

### 1. Install

```powershell
git clone <repo-url>
cd alphagrid-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate` instead.

### 2. Configure environment variables

Create a `.env` file in the project root (it is git-ignored):

```env
SECRET_KEY=<long random string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FINNHUB_API_KEY=<your Finnhub key>
FRED_API_KEY=<your FRED key>
GEMINI_API_KEY=<your Gemini key>
```

| Variable | Purpose | Where to get it |
|---|---|---|
| `SECRET_KEY` | Signs login tokens | Generate one: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM` | JWT algorithm | Use `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (default 1440 = 24 h) | - |
| `FINNHUB_API_KEY` | Quotes, search, company profiles, earnings | https://finnhub.io |
| `FRED_API_KEY` | Macro release dates | https://fred.stlouisfed.org/docs/api/api_key.html |
| `GEMINI_API_KEY` | AI analysis and chat | https://aistudio.google.com/apikey |

### 3. Run

Start the server from the project root (the SQLite file `alphagrid.db` and `.env` are resolved relative to it):

```powershell
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive docs (Swagger): http://127.0.0.1:8000/docs

Database tables are created automatically on first start.

Then start the frontend (see the **alphagrid-frontend** README). It expects this API at `http://127.0.0.1:8000`.

## API overview

All routes except `/auth/register` and `/auth/login` require an `Authorization: Bearer <token>` header.

| Method | Route | Description |
|---|---|---|
| POST | `/auth/register` | Create an account |
| POST | `/auth/login` | Log in and receive a JWT |
| GET | `/auth/me` | Current user |
| GET | `/watchlist` | Watchlist with live market data |
| POST | `/watchlist` | Add a ticker |
| DELETE | `/watchlist/{ticker}` | Remove a ticker |
| GET | `/stocks/search?q=` | Search tickers and companies |
| GET | `/stocks/{ticker}` | Quote, volume and logo |
| GET | `/stocks/{ticker}/history?period=` | Price history (`1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `5y`) |
| GET | `/stocks/{ticker}/earnings` | Next earnings report (within about 4 months) |
| GET | `/stocks/{ticker}/ai-summary` | AI briefing for the ticker |
| POST | `/stocks/{ticker}/ai-chat` | Follow-up question about the ticker |
| GET | `/calendar/this-week` | Macro and earnings events for the current week (Mon-Sun, Europe/Skopje) |

## Project structure

```
app/
  main.py        FastAPI app, CORS, router registration
  database.py    SQLAlchemy engine and session
  core/          settings (.env) and security (hashing, JWT)
  models/        database models (User, WatchlistItem)
  schemas/       Pydantic request/response models
  routers/       auth, stocks, watchlist, calendar
  services/      Finnhub/yfinance, FRED, Gemini and caching logic
```

## Maintenance notes

- **FOMC dates:** the decision dates are hardcoded in `app/services/macro_service.py` (`FOMC_DECISION_DATES_2026`). Update them each year from the [Federal Reserve calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm).
- **CORS:** the API currently allows all origins (`allow_origins=["*"]`). Restrict this to the frontend's address before deploying.

## Disclaimer

AlphaGrid is a learning project. Market data and AI-generated text are informational only and are not financial advice.
