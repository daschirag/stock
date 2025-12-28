# Crude Oil Price Prediction System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.108+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **AI-powered crude oil price forecasting with hybrid ML models**

Sophisticated prediction platform combining BiLSTM-Attention, CNN-LSTM, and XGBoost models with real-time data pipelines and professional web interface.

---

## 🎯 Features

- **Hybrid ML Models**: BiLSTM-Attention + CNN-LSTM + XGBoost ensemble
- **VMD Decomposition**: Variational Mode Decomposition for frequency analysis
- **Real-time Updates**: WebSocket integration for live price feeds
- **Sentiment Analysis**: News-based market sentiment tracking
- **Technical Indicators**: Ichimoku Cloud, RSI, MACD, Bollinger Bands
- **Confidence Intervals**: 95% prediction confidence bounds
- **Modern UI**: Next.js 15 dashboard with interactive charts
- **TimescaleDB**: Optimized time-series data storage

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd Crude_oil_pred

# Start all services
./start.sh

# Or manually with Docker Compose
docker-compose up -d --build
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

**Prerequisites:**
- PostgreSQL 16+ with TimescaleDB
- Python 3.11+
- Node.js 18+ or Bun 1.0+

```bash
# 1. Setup database
sudo -u postgres psql -c "CREATE DATABASE crude_oil_db;"
sudo -u postgres psql crude_oil_db < backend/init.sql

# 2. Backend setup
cd backend
uv sync  # or: pip install -r requirements.txt
uv run uvicorn app.main:app --reload

# 3. Frontend setup (new terminal)
cd frontend
bun install  # or: npm install
bun run dev  # or: npm run dev
```

---

## 📊 Architecture

```
┌─────────────────┐
│   Next.js 15    │  Frontend (React 19 + TailwindCSS)
│   Dashboard     │  
└────────┬────────┘
         │ HTTP/WebSocket
         ↓
┌────────────────────────────────────────┐
│         FastAPI Backend                │
│  ┌──────────────────────────────────┐  │
│  │  Data Pipeline                   │  │
│  │  - Yahoo Finance (Oil Prices)    │  │
│  │  - FRED API (Macro Indicators)   │  │
│  │  - NewsAPI (Sentiment)           │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  ML Models                       │  │
│  │  - BiLSTM-Attention (High-freq)  │  │
│  │  - CNN-LSTM (Mid-freq)           │  │
│  │  - XGBoost (Low-freq)            │  │
│  │  - Ensemble (Bayesian weights)   │  │
│  └──────────────────────────────────┘  │
└────────┬───────────────────────────────┘
         │
         ↓
┌─────────────────┐
│ PostgreSQL 16   │
│ + TimescaleDB   │  Time-series database
└─────────────────┘
```

---

## 🧠 ML Model Details

### Hybrid Ensemble Architecture

**1. BiLSTM-Attention** (High-frequency IMFs)
- 256 LSTM units, bidirectional
- 8-head multi-head attention
- Dropout: 0.2
- Optimizer: Adam (lr=0.001)

**2. CNN-LSTM** (Mid-frequency IMFs)
- Conv1D: 64 filters, kernel=3
- LSTM: 128 units
- MaxPooling1D: pool_size=2

**3. XGBoost** (Low-frequency IMFs & Trend)
- 500 trees,  learning_rate=0.01
- max_depth=5
- Early stopping: 50 rounds

**4. Ensemble Framework**
- Bayesian weight optimization (Optuna)
- 95% confidence intervals
- Sentiment-adjusted predictions (±2%)

---

## 📡 API Endpoints

### Data
- `GET /api/v1/data/latest` - Current price
- `GET /api/v1/data/historical` - Historical prices
- `POST /api/v1/data/fetch` - Trigger background fetch

### Predictions
- `POST /api/v1/predict` - Generate prediction
- `GET /api/v1/predict/history` - Past predictions

### Technical Indicators
- `GET /api/v1/indicators` - Get indicators
- `POST /api/v1/indicators/calculate` - Calculate indicators

### Sentiment
- `GET /api/v1/sentiment` - Aggregated sentiment
- `POST /api/v1/sentiment/fetch` - Fetch news

### WebSockets
- `WS /ws/prices` - Real-time price updates (every 5s)
- `WS /ws/predictions` - Real-time predictions (every 30s)

### System
- `GET /api/v1/health` - Health check

Full API documentation: http://localhost:8000/docs

---

## 🗂️ Project Structure

```
Crude_oil_pred/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API routes
│   │   ├── core/                # Config, logging, database
│   │   ├── models/
│   │   │   ├── db/              # SQLAlchemy models
│   │   │   └── ml/              # ML models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── services/            # Business logic
│   ├── tests/                   # Integration tests
│   ├── init.sql                 # Database schema
│   └── pyproject.toml           # Dependencies
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js app router
│   │   └── components/          # React components
│   ├── package.json
│   └── tailwind.config.ts
├── docker-compose.yml
├── start.sh                     # Quick start script
└── README.md
```

---

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`):
```env
DATABASE_URL=postgresql://user:password@localhost:5432/crude_oil_db
API_KEY_FRED=your_fred_api_key
API_KEY_NEWS=your_news_api_key
LOG_LEVEL=INFO
MODEL_VERSION=v1.0.0
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
uv run pytest tests/ -v

# Integration tests
uv run pytest tests/test_integration.py -v

# Frontend tests (when implemented)
cd frontend
bun test
```

---

## 📈 Background Tasks

Automatic scheduled tasks:
- **Price Fetch**: Every hour (WTI + Brent)
- **Technical Indicators**: Every 6 hours
- **Sentiment Analysis**: Every 4 hours
- **Predictions**: Every 12 hours

---

## 🎨 Frontend Features

- **Live Price Banner**: Real-time price with trend
- **Interactive Charts**: Candlestick visualization
- **Sentiment Gauge**: Circular progress indicator
- **Metric Cards**: Key statistics display
- **Dark Theme**: Professional slate + amber gold
- **Responsive**: Mobile-friendly design

---

## 🐳 Docker Deployment

### Services

- **postgres**: PostgreSQL 16 + TimescaleDB 2.13
- **backend**: FastAPI application (port 8000)
- **frontend**: Next.js application (port 3000)

### Commands

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Clean volumes
docker-compose down -v
```

---

## 📝 Development

### Add New Endpoint

1. Create endpoint in `backend/app/api/v1/endpoints/`
2. Add schemas in `backend/app/schemas/`
3. Create service logic in `backend/app/services/`
4. Register router in `backend/app/api/v1/router.py`

### Add New Component

1. Create component in `frontend/src/components/`
2. Import in page or layout
3. Style with TailwindCSS classes

---

## 🔒 Security

- CORS configuration
- API key protection
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)
- Rate limiting (production recommended)

---

## 📊 Performance

### Optimization Features

- Async I/O throughout
- Connection pooling (SQLAlchemy)
- Background task scheduling
- Database indexing (TimescaleDB)
- Efficient queries (time-series partitioning)

### Benchmarks

- API response: <100ms (cached)
- Prediction generation: ~2s
- WebSocket latency: <50ms

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **FastAPI**: Modern Python web framework
- **Next.js**: React meta-framework
- **Lightweight Charts**: TradingView charting library
- **TimescaleDB**: Time-series database
- **Optuna**: Hyperparameter optimization

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check API documentation at `/docs`
- Review walkthrough documents in `/.gemini/brain/`

---

**Built with ❤️ for financial forecasting**
