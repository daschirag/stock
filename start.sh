#!/bin/bash

# Quick start script for Crude Oil Prediction System

set -e

echo "🛢️  Crude Oil Price Prediction System - Quick Start"
echo "=================================================="
echo ""

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✓ Docker found"
    USE_DOCKER=true
else
    echo "⚠ Docker not found - using local setup"
    USE_DOCKER=false
fi

if [ "$USE_DOCKER" = true ]; then
    echo ""
    echo "Starting with Docker Compose..."
    echo ""
    
    # Build and start services
    docker-compose up -d --build
    
    echo ""
    echo "✓ Services started!"
    echo ""
    echo "Access points:"
    echo "  - Frontend:  http://localhost:3000"
    echo "  - Backend:   http://localhost:8000"
    echo "  - API Docs:  http://localhost:8000/docs"
    echo "  - Database:  localhost:5432"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "To stop:"
    echo "  docker-compose down"
    
else
    echo ""
    echo "Starting with local setup..."
    echo ""
    
    # Check for PostgreSQL
    if ! command -v psql &> /dev/null; then
        echo "✗ PostgreSQL not found. Please install PostgreSQL with TimescaleDB:"
        echo "  sudo apt-get install postgresql-16 postgresql-16-timescaledb"
        exit 1
    fi
    
    # Check for Python/uv
    if ! command -v uv &> /dev/null; then
        echo "Installing uv package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source ~/.cargo/env
    fi
    
    # Check for Node.js/Bun
    if ! command -v bun &> /dev/null && ! command -v node &> /dev/null; then
        echo "✗ Neither Bun nor Node.js found. Please install one:"
        echo "  - Bun:    curl -fsSL https://bun.sh/install | bash"
        echo "  - Node:   https://nodejs.org/"
        exit 1
    fi
    
    # Setup database
    echo "Setting up database..."
    sudo -u postgres psql -c "CREATE DATABASE crude_oil_db;" 2>/dev/null || echo "Database already exists"
    sudo -u postgres psql crude_oil_db < backend/init.sql 2>/dev/null || echo "Schema already initialized"
    
    # Backend setup
    echo ""
    echo "Setting up backend..."
    cd backend
    uv sync
    
    # Start backend in background
    echo "Starting backend server..."
    uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    
    cd ..
    
    # Frontend setup
    echo ""
    echo "Setting up frontend..."
    cd frontend
    
    if command -v bun &> /dev/null; then
        bun install
        echo "Starting frontend with Bun..."
        bun run dev &
    else
        npm install
        echo "Starting frontend with npm..."
        npm run dev &
    fi
    
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    
    cd ..
    
    echo ""
    echo "✓ Services started!"
    echo ""
    echo "Access points:"
    echo "  - Frontend:  http://localhost:3000"
    echo "  - Backend:   http://localhost:8000"
    echo "  - API Docs:  http://localhost:8000/docs"
    echo ""
    echo "Process IDs:"
    echo "  - Backend:   $BACKEND_PID"
    echo "  - Frontend:  $FRONTEND_PID"
    echo ""
    echo "To stop services:"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    
    # Save PIDs to file for easy cleanup
    echo "$BACKEND_PID" > .backend.pid
    echo "$FRONTEND_PID" > .frontend.pid
fi

echo "🎉 Setup complete! Visit http://localhost:3000 to see the dashboard."
