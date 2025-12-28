#!/bin/bash

# Stop script - safely stop all services

set -e

echo "🛑 Stopping Crude Oil Prediction System..."
echo "=========================================="
echo ""

# Check if Docker is being used
if docker-compose ps 2>/dev/null | grep -q "Up"; then
    echo "Stopping Docker services..."
    docker-compose down
    echo "✓ Docker services stopped"
else
    # Stop local processes
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo "Stopping backend (PID: $BACKEND_PID)..."
            kill $BACKEND_PID
            rm .backend.pid
            echo "✓ Backend stopped"
        else
            echo "Backend process not running"
            rm .backend.pid
        fi
    fi
    
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo "Stopping frontend (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID
            rm .frontend.pid
            echo "✓ Frontend stopped"
        else
            echo "Frontend process not running"
            rm .frontend.pid
        fi
    fi
    
    if [ ! -f .backend.pid ] && [ ! -f .frontend.pid ]; then
        echo "No running processes found"
        echo "Trying to kill by port..."
        
        # Try to kill processes on ports 8000 and 3000
        if lsof -ti:8000 > /dev/null 2>&1; then
            lsof -ti:8000 | xargs kill -9 2>/dev/null || true
            echo "✓ Killed process on port 8000"
        fi
        
        if lsof -ti:3000 > /dev/null 2>&1; then
            lsof -ti:3000 | xargs kill -9 2>/dev/null || true
            echo "✓ Killed process on port 3000"
        fi
    fi
fi

echo ""
echo "✅ All services stopped"
