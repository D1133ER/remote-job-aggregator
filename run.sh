#!/bin/bash
# Run frontend and backend together
# Usage: ./run.sh [--with-infra]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    if [ "$WITH_INFRA" = true ]; then
        echo "Stopping infrastructure..."
        cd "$SCRIPT_DIR" && $COMPOSE down 2>/dev/null
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM

# Detect docker compose command (prefer standalone docker-compose)
if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
else
    COMPOSE=""
fi

# Start infrastructure if not already running
WITH_INFRA=false
if ! ss -tln 2>/dev/null | grep -q ':5432'; then
    WITH_INFRA=true
    if [ -z "$COMPOSE" ]; then
        echo "❌ Docker Compose not found, and PostgreSQL is not running on :5432."
        echo "   Install Docker Compose or start PostgreSQL/Redis/Elasticsearch manually:"
        echo "   postgresql://user:password@localhost:5432/remotejobs"
        exit 1
    fi
    echo "🐳 Starting infrastructure (PostgreSQL, Redis, Elasticsearch)..."
    cd "$SCRIPT_DIR" && $COMPOSE up -d postgres redis elasticsearch
    echo "⏳ Waiting for services to be ready..."
    sleep 10
fi

# Activate backend venv
source "$SCRIPT_DIR/backend/.venv/bin/activate"

echo "🚀 Starting backend..."
cd "$SCRIPT_DIR/backend"
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

echo "🚀 Starting frontend..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

echo ""
echo "✅ Services running:"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Frontend:     http://localhost:3000"
if [ "$WITH_INFRA" = true ]; then
    echo ""
    echo "📦 Infrastructure:"
    echo "   PostgreSQL:   localhost:5432"
    echo "   Redis:        localhost:6379"
    echo "   Elasticsearch: localhost:9200"
fi
echo ""
echo "Press Ctrl+C to stop"

wait
