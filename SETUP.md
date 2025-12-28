# Crude Oil Prediction System - Development Setup Guide

This guide will help you set up and run the complete crude oil price prediction system on your local machine for development and testing.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Recommended)](#quick-start-recommended)
3. [Manual Setup](#manual-setup)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Development Workflow](#development-workflow)

---

## 🔧 Prerequisites

### Required Software

**Option 1: Docker (Easiest)**
- Docker Engine 24.0+
- Docker Compose 2.20+

**Option 2: Local Development**
- PostgreSQL 16+ with TimescaleDB extension
- Python 3.11+
- Node.js 18+ OR Bun 1.0+
- Git

### System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 10GB free space
- **OS**: Linux, macOS, or Windows (WSL2)

---

## 🚀 Quick Start (Recommended)

### Using the Start Script

```bash
# Navigate to project directory
cd Crude_oil_pred

# Make script executable (if not already)
chmod +x start.sh

# Run the start script
./start.sh
```

The script will automatically:
- Detect if Docker is available
- Set up the database
- Install dependencies
- Start all services

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## 🛠️ Manual Setup

Choose either Docker or Local Development setup below.

### Setup Method 1: Docker (Recommended for Development)

#### Step 1: Install Docker

**Ubuntu/Debian:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and back in, then verify
docker --version
docker-compose --version
```

**macOS:**
```bash
# Install Docker Desktop from:
# https://www.docker.com/products/docker-desktop
```

#### Step 2: Configure Environment

```bash
cd Crude_oil_pred

# Copy environment file (already exists in repo)
# Review and modify .env if needed
cat .env

# The default configuration uses mock data - perfect for testing!
```

#### Step 3: Build and Start Services

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

#### Step 4: Initialize Database (First Time Only)

The database will be automatically initialized from `backend/init.sql` when the postgres container starts.

To manually verify:
```bash
# Access postgres container
docker-compose exec postgres psql -U postgres -d crude_oil_db

# Check tables
\dt

# Exit
\q
```

#### Step 5: Access the Application

Open your browser:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)

---

### Setup Method 2: Local Development

#### Step 1: Install PostgreSQL with TimescaleDB

**Ubuntu/Debian:**
```bash
# Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Install PostgreSQL 16
sudo apt-get update
sudo apt-get install -y postgresql-16 postgresql-16-postgis-3

# Add TimescaleDB repository
sudo sh -c "echo 'deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -

# Install TimescaleDB
sudo apt-get update
sudo apt-get install -y timescaledb-2-postgresql-16

# Configure TimescaleDB
sudo timescaledb-tune --quiet --yes

# Restart PostgreSQL
sudo systemctl restart postgresql
```

**macOS:**
```bash
# Using Homebrew
brew install postgresql@16
brew install timescaledb

# Start PostgreSQL
brew services start postgresql@16
```

#### Step 2: Create Database

```bash
# Switch to postgres user and create database
sudo -u postgres psql

# In psql prompt:
CREATE DATABASE crude_oil_db;
\q

# Initialize schema
sudo -u postgres psql crude_oil_db < backend/init.sql

# Verify tables were created
sudo -u postgres psql crude_oil_db -c "\dt"
```

#### Step 3: Install Python Dependencies

```bash
# Install uv package manager (fast, modern)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.cargo/env

# Navigate to backend
cd backend

# Create virtual environment and install dependencies
uv sync

# Verify installation
uv run python -c "import fastapi; print('FastAPI installed successfully')"

cd ..
```

**Alternative with pip:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
cd ..
```

#### Step 4: Install Frontend Dependencies

**Option A: Using Bun (Recommended - Faster)**
```bash
# Install Bun
curl -fsSL https://bun.sh/install | bash
source ~/.bashrc  # or ~/.zshrc

# Install dependencies
cd frontend
bun install
cd ..
```

**Option B: Using npm**
```bash
cd frontend
npm install
cd ..
```

#### Step 5: Configure Environment Variables

```bash
# Backend configuration
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/crude_oil_db

# API Keys (optional - system uses mock data if not provided)
API_KEY_FRED=
API_KEY_NEWS=

# Application
LOG_LEVEL=INFO
MODEL_VERSION=v1.0.0
SEQUENCE_LENGTH=60
BATCH_SIZE=32
LEARNING_RATE=0.001
EPOCHS=100

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF

# Frontend configuration
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
EOF
```

---

## ⚙️ Configuration

### Environment Variables Explained

**Backend (.env):**
- `DATABASE_URL`: PostgreSQL connection string
- `API_KEY_FRED`: FRED API key (optional - mock data used if empty)
- `API_KEY_NEWS`: NewsAPI key (optional - mock data used if empty)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `MODEL_VERSION`: Current model version identifier
- `SEQUENCE_LENGTH`: Time series sequence length (default: 60)
- `BATCH_SIZE`: Training batch size (default: 32)
- `LEARNING_RATE`: Model learning rate (default: 0.001)
- `EPOCHS`: Maximum training epochs (default: 100)

**Frontend (.env.local):**
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_WS_URL`: WebSocket URL for real-time updates

### Mock Data vs Real Data

**The system works perfectly with MOCK DATA (no API keys needed)!**

- Without API keys: Generates realistic mock oil prices, indicators, and sentiment
- With API keys: Fetches real data from Yahoo Finance, FRED, and NewsAPI

**To use real data** (optional):
1. Get FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html
2. Get NewsAPI key: https://newsapi.org/register
3. Add keys to `.env` file

---

## 🏃 Running the Application

### Docker Method

```bash
# Start all services
docker-compose up -d

# View logs (all services)
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Local Development Method

**Terminal 1 - Backend:**
```bash
cd backend

# With uv
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with activated venv
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend

# With Bun
bun run dev

# Or with npm
npm run dev
```

**Terminal 3 - Database (if not running as service):**
```bash
# Start PostgreSQL (if not already running)
sudo systemctl start postgresql

# Or on macOS
brew services start postgresql@16
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_integration.py -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### API Manual Testing

**Using the interactive API docs:**
1. Open http://localhost:8000/docs
2. Try the `/api/v1/health` endpoint - should return `{"status": "ok"}`
3. Try `/api/v1/data/latest?symbol=WTI` - returns mock price data
4. Try `POST /api/v1/predict` with body `{"horizon": "1d", "symbol": "WTI"}`

**Using curl:**
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get latest price
curl http://localhost:8000/api/v1/data/latest?symbol=WTI

# Generate prediction
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"horizon": "1d", "symbol": "WTI"}'

# Get historical data
curl "http://localhost:8000/api/v1/data/historical?symbol=WTI&days=30"

# Get sentiment
curl http://localhost:8000/api/v1/sentiment?days=7
```

### Frontend Testing

Open http://localhost:3000 and verify:
- [ ] Dashboard loads without errors
- [ ] Live price displays (mock data)
- [ ] Chart renders with candlesticks
- [ ] Sentiment gauge shows percentage
- [ ] Metric cards display values
- [ ] No console errors in browser DevTools (F12)

### WebSocket Testing

**Using browser console (F12):**
```javascript
// Test price WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/prices');
ws.onmessage = (event) => console.log('Price update:', JSON.parse(event.data));

// Test prediction WebSocket
const ws2 = new WebSocket('ws://localhost:8000/ws/predictions');
ws2.onmessage = (event) => console.log('Prediction update:', JSON.parse(event.data));
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: "Port already in use"

**Solution:**
```bash
# Find process using port 8000 (backend)
sudo lsof -i :8000
kill -9 <PID>

# Find process using port 3000 (frontend)
sudo lsof -i :3000
kill -9 <PID>

# Or for Docker
docker-compose down
```

#### Issue: "Database connection failed"

**Docker:**
```bash
# Check if postgres container is running
docker-compose ps

# Restart postgres
docker-compose restart postgres

# View logs
docker-compose logs postgres
```

**Local:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start if not running
sudo systemctl start postgresql

# Test connection
psql -U postgres -d crude_oil_db -c "SELECT 1;"
```

#### Issue: "Module not found" (Python)

```bash
cd backend

# Reinstall dependencies
uv sync

# Or with pip
pip install -e .

# Verify installation
uv run python -c "import app; print('OK')"
```

#### Issue: "Module not found" (Frontend)

```bash
cd frontend

# Remove node_modules and reinstall
rm -rf node_modules .next
bun install  # or npm install

# Clear Next.js cache
rm -rf .next
```

#### Issue: "Frontend shows API errors"

**Check backend is running:**
```bash
curl http://localhost:8000/api/v1/health
```

**Check CORS configuration:**
- Verify `CORS_ORIGINS` in `.env` includes `http://localhost:3000`
- Restart backend after changing `.env`

#### Issue: "TimescaleDB extension not found"

```bash
# Connect to database
sudo -u postgres psql crude_oil_db

# Enable extension manually
CREATE EXTENSION IF NOT EXISTS timescaledb;

# Verify
\dx
```

#### Issue: "No data showing in charts"

This is expected on first run! The system uses mock data by default.

**Trigger data generation:**
```bash
# Using API
curl -X POST "http://localhost:8000/api/v1/data/fetch?symbol=WTI&days=60"

# Wait a few seconds, then check
curl "http://localhost:8000/api/v1/data/historical?symbol=WTI&days=7"
```

---

## 💻 Development Workflow

### Making Code Changes

**Backend changes:**
1. Edit files in `backend/app/`
2. FastAPI auto-reloads (if using `--reload` flag)
3. Test at http://localhost:8000/docs

**Frontend changes:**
1. Edit files in `frontend/src/`
2. Next.js auto-reloads
3. View at http://localhost:3000

**Database schema changes:**
1. Edit `backend/init.sql`
2. For Docker: `docker-compose down -v && docker-compose up -d`
3. For local: Drop and recreate database

### Adding New Features

**New API endpoint:**
1. Create endpoint in `backend/app/api/v1/endpoints/`
2. Add Pydantic schemas in `backend/app/schemas/`
3. Implement logic in `backend/app/services/`
4. Register router in `backend/app/api/v1/router.py`
5. Test at http://localhost:8000/docs

**New frontend component:**
1. Create component in `frontend/src/components/`
2. Import in page or layout
3. Style with TailwindCSS classes

### Debugging

**Backend debugging:**
```python
# Add print statements
print("Debug:", data)

# Or use logging
from app.core import get_logger
logger = get_logger(__name__)
logger.info(f"Processing: {data}")

# Check logs
docker-compose logs -f backend  # Docker
# or check terminal output for local
```

**Frontend debugging:**
- Open browser DevTools (F12)
- Check Console tab for errors
- Use Network tab to inspect API calls
- Use React DevTools extension

### Database Inspection

```bash
# Docker
docker-compose exec postgres psql -U postgres -d crude_oil_db

# Local
sudo -u postgres psql crude_oil_db

# Useful queries:
SELECT COUNT(*) FROM oil_prices;
SELECT * FROM oil_prices ORDER BY timestamp DESC LIMIT 10;
SELECT * FROM predictions ORDER BY created_at DESC LIMIT 5;
SELECT COUNT(*) FROM technical_indicators;
```

---

## 📊 Initial Data Population

To populate the database with initial data for testing:

```bash
# Method 1: Using API endpoints
curl -X POST "http://localhost:8000/api/v1/data/fetch?symbol=WTI&days=60"
curl -X POST "http://localhost:8000/api/v1/indicators/calculate?symbol=WTI&days=60"
curl -X POST "http://localhost:8000/api/v1/sentiment/fetch?days=7"

# Method 2: Let background tasks populate automatically
# Background tasks start automatically and run periodically:
# - Prices: every hour
# - Indicators: every 6 hours
# - Sentiment: every 4 hours
# - Predictions: every 12 hours

# Check if background tasks are running (look for log entries)
docker-compose logs backend | grep "Background tasks"
```

---

## 🔄 Resetting Everything

**Docker (complete reset):**
```bash
# Stop and remove everything
docker-compose down -v

# Remove images (optional)
docker-compose down --rmi all

# Rebuild from scratch
docker-compose up -d --build
```

**Local Development:**
```bash
# Drop database
sudo -u postgres psql -c "DROP DATABASE IF EXISTS crude_oil_db;"

# Recreate
sudo -u postgres psql -c "CREATE DATABASE crude_oil_db;"
sudo -u postgres psql crude_oil_db < backend/init.sql

# Clear Python cache
find backend -type d -name __pycache__ -exec rm -r {} +
find backend -type f -name "*.pyc" -delete

# Clear frontend cache
cd frontend
rm -rf .next node_modules
bun install  # or npm install
cd ..
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Backend responds: `curl http://localhost:8000/api/v1/health`
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Frontend loads: http://localhost:3000
- [ ] Database connected: Check backend logs for "Database connection successful"
- [ ] Background tasks started: Check logs for "Background tasks started"
- [ ] Mock data works: Generate prediction via API docs
- [ ] WebSocket connects: Check browser console for WebSocket messages
- [ ] Charts render: Verify candlestick chart visible on dashboard

---

## 📝 Next Steps

Once everything is running:

1. **Explore the UI**: Visit http://localhost:3000
2. **Test the API**: Use http://localhost:8000/docs
3. **Generate predictions**: Try different time horizons (1d, 7d, 30d)
4. **Monitor background tasks**: Watch logs for scheduled data fetches
5. **Experiment with real data**: Add API keys to `.env` if desired

---

## 🆘 Getting Help

If you encounter issues:

1. Check this troubleshooting guide above
2. Review logs: `docker-compose logs` or terminal output
3. Check `README.md` for additional documentation
4. Review walkthrough files in `.gemini/brain/` directory
5. Verify all prerequisites are installed
6. Try a complete reset (see "Resetting Everything" above)

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**You're all set! 🎉**

Run `./start.sh` or follow the manual steps above to get started with development!
