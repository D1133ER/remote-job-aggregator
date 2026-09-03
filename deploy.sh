#!/bin/bash

# Remote Job Aggregator Deployment Script

set -e

echo "🚀 Starting deployment of Remote Job Aggregator..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }

# Detect docker compose command (v2 plugin or standalone)
if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    echo "❌ Docker Compose is required but not installed." >&2
    echo "   Install: https://docs.docker.com/compose/install/" >&2
    exit 1
fi
echo "✅ Using: $COMPOSE"

# Environment setup
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Backend
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/remotejobs
REDIS_URL=redis://localhost:6379/0
ELASTICSEARCH_URL=http://localhost:9200
DEBUG=true
SECRET_KEY=$(openssl rand -hex 32)

# OpenAI (optional for AI enrichment)
OPENAI_API_KEY=your-openai-api-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF
    echo "✅ Created .env file. Please update with your API keys."
    exit 0
fi

# Build and deploy
echo "🔨 Building Docker images..."
$COMPOSE build

echo "📦 Starting services..."
$COMPOSE up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Database migrations
echo "🗄️ Running database migrations..."
$COMPOSE exec backend alembic upgrade head

# Initialize Elasticsearch
echo "🔍 Initializing Elasticsearch..."
$COMPOSE exec backend python -c "
from app.services.elasticsearch_service import ElasticsearchService
es = ElasticsearchService('http://elasticsearch:9200')
es.create_index()
print('✅ Elasticsearch index created')
"

echo "✅ Deployment complete!"
echo ""
echo "📊 Services running:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/api/docs"
echo "   - Flower (Celery monitoring): http://localhost:5555"
echo ""
echo "📝 Next steps:"
echo "   1. Update .env with your OpenAI API key"
echo "   2. Add more scrapers in backend/app/scrapers/"
echo "   3. Configure email alerts"