# Crude Oil Price Prediction System

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **AI-powered crude oil price forecasting** — Hybrid ML models, real-time data, and a professional dashboard.

Sophisticated prediction platform combining **BiLSTM-Attention**, **CNN-LSTM**, and **XGBoost** with VMD decomposition, sentiment analysis, technical indicators, and a modern Next.js 15 UI. Works with or without PostgreSQL; uses mock data when the database is unavailable.

---

## Features

### Backend
- **Hybrid ML models**: BiLSTM-Attention + CNN-LSTM + XGBoost ensemble with Bayesian weighting
- **VMD decomposition**: Variational Mode Decomposition for frequency analysis
- **Real-time WebSocket**: Live price and prediction feeds
- **Sentiment analysis**: News-based market sentiment
- **Technical indicators**: Ichimoku Cloud, RSI, MACD, Bollinger Bands
- **95% confidence intervals** on predictions
- **Graceful fallback**: Runs without PostgreSQL; endpoints return mock/empty data when DB is unavailable
- **TimescaleDB-ready**: Optimized time-series storage when DB is configured

### Frontend
- **Live price banner**: Real-time WTI/Brent via WebSocket (fallback to REST polling)
- **Interactive charts**: Candlestick and sparklines
- **AI-style insights**: Market summary, key drivers, technical summary, price outlook
- **Key levels**: Support, resistance, pivot points
- **Economic calendar**: Upcoming events relevant to oil markets
- **News headlines**: Top headlines affecting oil
- **Watchlist**: WTI vs Brent side-by-side
- **Multi-horizon predictions**: 1-day, 7-day, 30-day with refresh
- **Sentiment gauge**, **volatility badge**, **opportunity meter**
- **Price alerts**: Set and manage alerts (stored in browser)
- **Quick stats**: 52-week high/low, session range
- **Export**: Download data as CSV
- **Theme toggle**: Dark / light mode
- **Glossary**: Expandable crude oil trading terms
- **Responsive**: Mobile-friendly layout

---

## Quick Start

### Option 1: Docker (recommended)

```bash
git clone https://github.com/AbhayZ1/Crude_oil_pred.git
cd Crude_oil_pred

./start.sh
# or: docker-compose up -d --build
```

- **Frontend**: http://localhost:3000  
- **Backend API**: http://localhost:8000  
- **API docs**: http://localhost:8000/docs  

### Option 2: Local development

**Prerequisites:** Python 3.12+, Node.js 18+ (or Bun), and optionally PostgreSQL 16+ with TimescaleDB.

```bash
git clone https://github.com/AbhayZ1/Crude_oil_pred.git
cd Crude_oil_pred
```

---

### Deployment with Vercel

The frontend and backend are treated as two separate projects when deploying.

1. **Frontend (Next.js)**
   * Import the repository into Vercel and set the root directory to `frontend/`.
   * Vercel will automatically run `npm install` and `npm run build`.
   * Configure an environment variable `NEXT_PUBLIC_API_URL` pointing to your backend URL.

   A simple `vercel.json` placed in `frontend/` helps Vercel detect the build target:

   ```json
   // frontend/vercel.json
   {
     "version": 2,
     "builds": [
       { "src": "package.json", "use": "@vercel/next" }
     ]
   }
   ```

2. **Backend (FastAPI)**
   * Deploy the backend as a Docker image using any host that supports containers (Render, Railway, etc.)
     or as a separate Vercel project with the Docker builder.
   * The existing `backend/Dockerfile` is already configured for production.
   * If you choose Vercel, add a `vercel.json` file to `backend/` like this:

   ```json
   // backend/vercel.json
   {
     "version": 2,
     "builds": [
       { "src": "Dockerfile", "use": "@vercel/docker" }
     ],
     "routes": [
       { "src": "\\/(.*)", "dest": "/app.main:app" }
     ]
   }
   ```

   * After deployment you will get a public URL such as `https://stock-backend.vercel.app`.

3. **Connect the two**
   * Set `NEXT_PUBLIC_API_URL` in the frontend project to your backend URL.
   * Frontend rewrites (see `next.config.js`) will proxy `/api/*` requests accordingly.

This separation mirrors your local development setup: two terminals, one for each service.

---

(This section may be removed or adjusted depending on where you host the backend.)

**Backend (runs without DB; uses mock data if DB is not available):**

```bash
cd backend
uv venv && uv sync
uv run uvicorn app.main:app --reload
```

**Frontend (new terminal):**

```bash
cd frontend
npm install
npm run dev
```

**Optional — database:**  
If you use PostgreSQL, create the DB and run the schema:

```bash
# Create DB and load schema (Linux/macOS example)
sudo -u postgres psql -c "CREATE DATABASE crude_oil_db;"
sudo -u postgres psql crude_oil_db < backend/init.sql
```

Set `DATABASE_URL` in `.env` (see Configuration).

---

## Architecture

```
┌─────────────────┐
│   Next.js 15    │  React 19, TailwindCSS, Framer Motion
│   Dashboard     │  useLivePrice → WebSocket / REST fallback
└────────┬────────┘
         │ HTTP / WebSocket
         ▼
┌────────────────────────────────────────┐
│         FastAPI Backend                │
│  Data: Yahoo Finance, FRED, NewsAPI    │
│  ML: BiLSTM-Attention, CNN-LSTM,       │
│      XGBoost, VMD, Ensemble            │
│  Insights, key levels, calendar       │
└────────┬───────────────────────────────┘
         │ (optional)
         ▼
┌─────────────────┐
│ PostgreSQL 16   │  TimescaleDB for time-series
└─────────────────┘
```

---

## API Reference

Base URL: `http://localhost:8000`  
Interactive docs: http://localhost:8000/docs  

### Data
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/data/latest` | Current price (mock if no DB) |
| GET | `/api/v1/data/historical` | Historical prices |
| POST | `/api/v1/data/fetch` | Trigger background fetch |

### Predictions
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/predict` | Generate prediction |
| GET | `/api/v1/predict/history` | Past predictions |

### Insights & calendar
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/insights` | AI-style summary, drivers, outlook |
| GET | `/api/v1/insights/key-levels` | Support, resistance, pivots |
| GET | `/api/v1/calendar` | Economic calendar events |

### Technical & sentiment
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/indicators` | Technical indicators |
| POST | `/api/v1/indicators/calculate` | Calculate indicators |
| GET | `/api/v1/sentiment` | Aggregated sentiment |
| POST | `/api/v1/sentiment/fetch` | Fetch news sentiment |

### WebSockets
| Path | Description |
|------|-------------|
| `WS /api/v1/ws/prices` | Real-time prices (e.g. every 5s) |
| `WS /api/v1/ws/predictions` | Real-time predictions |

### System
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check (DB-independent) |

---

## Project structure

```
Crude_oil_pred/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # health, historical, predict, sentiment, websocket, insights
│   │   ├── core/               # config, logging, database (graceful no-DB)
│   │   ├── models/db/          # SQLAlchemy models
│   │   ├── models/ml/          # BiLSTM-Attention, CNN-LSTM, XGBoost, ensemble
│   │   ├── schemas/            # Pydantic request/response
│   │   └── services/           # data, prediction, sentiment, technical_indicators, etc.
│   ├── tests/
│   ├── init.sql
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/                # layout, page, globals.css
│   │   ├── components/
│   │   │   ├── charts/         # PriceChart, Sparkline
│   │   │   └── dashboard/      # AIInsights, KeyLevels, Watchlist, SentimentGauge, etc.
│   │   └── hooks/              # useLivePrice (WebSocket + REST fallback)
│   ├── package.json
│   └── tailwind.config.ts
├── docker-compose.yml
├── start.sh / stop.sh
├── .env.example
└── README.md
```

---

## Configuration

Copy `.env.example` to `.env` and adjust as needed.

**Backend (`.env`):**

```env
DATABASE_URL=postgresql://user:password@localhost:5432/crude_oil_db
API_KEY_FRED=your_fred_api_key
API_KEY_NEWS=your_news_api_key
LOG_LEVEL=INFO
MODEL_VERSION=v1.0.0
```

**Frontend (`.env.local`):**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

If `DATABASE_URL` is missing or PostgreSQL is down, the backend still starts and serves mock/empty data where applicable.

---

## ML model summary

- **BiLSTM-Attention**: High-frequency IMFs; 256 bidirectional LSTM units, 8-head attention.  
- **CNN-LSTM**: Mid-frequency IMFs; Conv1D 64 filters, LSTM 128 units.  
- **XGBoost**: Low-frequency IMFs and trend; 500 trees, early stopping.  
- **Ensemble**: Bayesian weight optimization (Optuna), 95% confidence intervals, optional sentiment adjustment (±2%).

---

## Testing

```bash
# Backend
cd backend
uv run pytest tests/ -v

# Integration
uv run pytest tests/test_integration.py -v
```

---

## Docker

**Services:** `postgres` (PostgreSQL + TimescaleDB), `backend` (port 8000), `frontend` (port 3000).

```bash
docker-compose up -d --build
docker-compose logs -f backend
docker-compose down
```

---

## Contributing

1. Fork the repo  
2. Create a branch (`git checkout -b feature/your-feature`)  
3. Commit changes (`git commit -m 'Add your feature'`)  
4. Push and open a Pull Request  

---

## License

MIT — see [LICENSE](LICENSE).

---

## Acknowledgments

FastAPI, Next.js, Lightweight Charts, TimescaleDB, Optuna, yfinance, and the open-source ML/data community.

---

**Built for crude oil price forecasting and market insight.**
