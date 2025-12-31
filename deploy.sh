#!/bin/bash

# Production deployment script for Sentiment Analysis API v2.0
set -e

echo "🚀 Deploying Sentiment Analysis API v2.0 to Production..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-production}
WORKERS=${WORKERS:-4}
PORT=${PORT:-4880}

echo -e "${YELLOW}Environment: $ENVIRONMENT${NC}"
echo -e "${YELLOW}Workers: $WORKERS${NC}"
echo -e "${YELLOW}Port: $PORT${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found! Please create it first.${NC}"
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=("OPENAI_API_KEY" "LLM_MODEL" "OPENAI_URI" "LANGFUSE_SECRET_KEY" "LANGFUSE_PUBLIC_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Required environment variable $var is not set${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Environment variables validated${NC}"

# Create logs directory
mkdir -p logs/nginx

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Build new images
echo "🔨 Building Docker images..."
docker-compose build --no-cache

# Start Redis first
echo "🗄️ Starting Redis..."
docker-compose up -d redis

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
timeout=30
while ! docker-compose exec redis redis-cli ping > /dev/null 2>&1; do
    sleep 1
    timeout=$((timeout - 1))
    if [ $timeout -eq 0 ]; then
        echo -e "${RED}❌ Redis failed to start within 30 seconds${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ Redis is ready${NC}"

# Start API services
echo "🚀 Starting API services..."
docker-compose up -d sentiment-api-1 sentiment-api-2 sentiment-api-3

# Wait for API services to be healthy
echo "⏳ Waiting for API services to be healthy..."
for service in sentiment-api-1 sentiment-api-2 sentiment-api-3; do
    timeout=60
    while ! docker-compose exec $service curl -f http://localhost:8000/health > /dev/null 2>&1; do
        sleep 2
        timeout=$((timeout - 2))
        if [ $timeout -le 0 ]; then
            echo -e "${RED}❌ $service failed to become healthy${NC}"
            docker-compose logs $service
            exit 1
        fi
    done
    echo -e "${GREEN}✅ $service is healthy${NC}"
done

# Start Nginx
echo "🌐 Starting Nginx load balancer..."
docker-compose up -d nginx

# Final health check
echo "🏥 Performing final health check..."
sleep 5

# Check if the load balancer is working
if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Load balancer is working${NC}"
else
    echo -e "${RED}❌ Load balancer health check failed${NC}"
    docker-compose logs nginx
    exit 1
fi

# Show service status
echo ""
echo "📊 Service Status:"
docker-compose ps

# Show resource usage
echo ""
echo "💻 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Test API endpoints
echo ""
echo "🧪 Testing API endpoints..."

# Test main endpoint
if curl -s -X POST http://localhost:$PORT/analyze \
   -H "Content-Type: application/json" \
   -d '{
     "id": "deploy_test",
     "index": "test_index", 
     "topic": "Test",
     "title": "Test deployment",
     "content": "This is a test message for deployment",
     "type": "newsComment",
     "main_keywords": ["test"]
   }' > /dev/null; then
    echo -e "${GREEN}✅ /analyze endpoint working${NC}"
else
    echo -e "${RED}❌ /analyze endpoint failed${NC}"
fi

# Test metrics endpoint
if curl -s http://localhost:$PORT/metrics > /dev/null; then
    echo -e "${GREEN}✅ /metrics endpoint working${NC}"
else
    echo -e "${RED}❌ /metrics endpoint failed${NC}"
fi

# Show deployment info
echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Service Information:"
echo "  API URL: http://localhost:$PORT"
echo "  Health Check: http://localhost:$PORT/health"
echo "  Metrics: http://localhost:$PORT/metrics"
echo "  Cache Stats: http://localhost:$PORT/cache/stats"
echo "  API Docs: http://localhost:$PORT/docs (if not production)"
echo ""
echo "🔧 Management Commands:"
echo "  View logs: docker-compose logs -f [service_name]"
echo "  Scale API: docker-compose up -d --scale sentiment-api-1=2"
echo "  Stop all: docker-compose down"
echo "  Restart: docker-compose restart [service_name]"
echo ""
echo "📊 Monitoring:"
echo "  Redis: docker-compose exec redis redis-cli monitor"
echo "  Stats: docker stats"
echo ""

# Optional: Run performance test
read -p "🧪 Run performance test? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Running performance test..."
    if [ -f "test_production_api.py" ]; then
        python3 test_production_api.py
    else
        echo -e "${YELLOW}⚠️ test_production_api.py not found, skipping performance test${NC}"
    fi
fi

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"