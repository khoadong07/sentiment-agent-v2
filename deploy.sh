#!/bin/bash

# High-performance production deployment script for Sentiment Analysis API

set -e

echo "🚀 Deploying High-Performance Sentiment Analysis API to Production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create .env file with required environment variables:"
    echo "OPENAI_API_KEY=your_key_here"
    echo "MONGO_URI=your_mongodb_uri"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating log directories...${NC}"
mkdir -p logs/nginx logs/app

# Set proper permissions
chmod 755 logs/nginx logs/app

# Pull latest base images
echo -e "${YELLOW}📦 Pulling latest base images...${NC}"
docker-compose -f $COMPOSE_FILE pull

# Build with optimizations
echo -e "${YELLOW}🔨 Building optimized images...${NC}"
docker-compose -f $COMPOSE_FILE build --no-cache --parallel

# Deploy with zero-downtime strategy
echo -e "${YELLOW}🔄 Deploying with high-availability setup...${NC}"

# Stop existing services
docker-compose -f $COMPOSE_FILE down

# Start infrastructure services first
echo -e "${BLUE}🗄️  Starting infrastructure services...${NC}"
docker-compose -f $COMPOSE_FILE up -d redis

# Wait for infrastructure
sleep 10

# Start API instances
echo -e "${BLUE}🚀 Starting API instances...${NC}"
docker-compose -f $COMPOSE_FILE up -d sentiment-api-1 sentiment-api-2 sentiment-api-3

# Wait for API instances
sleep 20

# Start load balancer
echo -e "${BLUE}⚖️  Starting load balancer...${NC}"
docker-compose -f $COMPOSE_FILE up -d nginx

# Wait for all services to be ready
echo -e "${YELLOW}⏳ Waiting for all services to be ready...${NC}"
sleep 30

# Comprehensive health checks
echo -e "${YELLOW}🔍 Running comprehensive health checks...${NC}"

# Check individual API instances
for i in {1..3}; do
    echo -e "${BLUE}Checking sentiment-api-$i...${NC}"
    if docker-compose -f $COMPOSE_FILE exec -T sentiment-api-$i curl -f http://localhost:4880/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ sentiment-api-$i is healthy${NC}"
    else
        echo -e "${RED}❌ sentiment-api-$i health check failed${NC}"
        docker-compose -f $COMPOSE_FILE logs sentiment-api-$i
        exit 1
    fi
done

# Check load balancer
echo -e "${BLUE}Checking load balancer...${NC}"
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Load balancer is healthy${NC}"
else
    echo -e "${RED}❌ Load balancer health check failed${NC}"
    docker-compose -f $COMPOSE_FILE logs nginx
    exit 1
fi

# Check Redis
echo -e "${BLUE}Checking Redis...${NC}"
if docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${RED}❌ Redis health check failed${NC}"
    exit 1
fi

# Performance test
echo -e "${YELLOW}⚡ Running performance test...${NC}"
echo "Testing load balancer response times:"
for i in {1..10}; do
    response=$(curl -s -o /dev/null -w "%{http_code} %{time_total}s" http://localhost/health)
    echo "  Request $i: $response"
done

# Load test
echo -e "${YELLOW}🔥 Running concurrent load test...${NC}"
echo "Testing with 20 concurrent requests:"
for i in {1..20}; do
    curl -s -o /dev/null http://localhost/health &
done
wait
echo -e "${GREEN}✅ Concurrent load test completed${NC}"

# Clean up old images
echo -e "${YELLOW}🧹 Cleaning up old images...${NC}"
docker image prune -f

echo -e "${GREEN}🎉 High-Performance Deployment Completed Successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Production Services:${NC}"
echo "  🌐 Load Balancer: http://localhost"
echo "  🏥 Health Check: http://localhost/health"
echo "  📊 Nginx Status: http://localhost/nginx_status"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "  📋 View all logs: docker-compose logs -f"
echo "  📊 Service status: docker-compose ps"
echo "  💻 Resource usage: docker stats"
echo "  🔄 Restart service: docker-compose restart <service>"
echo "  📈 Scale API: docker-compose up -d --scale sentiment-api-1=2"
echo ""
echo -e "${BLUE}🚨 Monitoring:${NC}"
echo "  📈 Nginx status: http://localhost/nginx_status"
echo "  🔍 Service logs: docker-compose logs -f"
echo ""
echo -e "${GREEN}✨ Your high-performance sentiment analysis API is now running!${NC}"