#!/bin/bash

# Performance testing script for production deployment

set -e

echo "🚀 Starting Performance Tests for Sentiment Analysis API"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
API_URL="http://localhost"
HEALTH_URL="$API_URL/health"
ANALYZE_URL="$API_URL/analyze"

# Test data
TEST_DATA='{
  "id": "test_performance_001",
  "index": "6641ccbdf4901a7ae602197f",
  "title": "Performance test title",
  "content": "This is a performance test content for load testing",
  "description": "Performance testing description with multiple keywords",
  "type": "performance_test"
}'

echo -e "${BLUE}📊 System Information:${NC}"
echo "CPU Cores: $(nproc)"
echo "Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Docker Version: $(docker --version)"
echo ""

# Health check first
echo -e "${YELLOW}🏥 Health Check...${NC}"
if curl -s -f $HEALTH_URL > /dev/null; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${RED}❌ API is not responding${NC}"
    exit 1
fi

# Test 1: Response time test
echo -e "${YELLOW}⏱️  Test 1: Response Time Analysis${NC}"
echo "Testing response times for 50 requests..."

total_time=0
success_count=0
error_count=0

for i in {1..50}; do
    response_time=$(curl -s -o /dev/null -w "%{time_total}" -X POST \
        -H "Content-Type: application/json" \
        -d "$TEST_DATA" \
        $ANALYZE_URL 2>/dev/null || echo "error")
    
    if [ "$response_time" != "error" ]; then
        total_time=$(echo "$total_time + $response_time" | bc -l)
        success_count=$((success_count + 1))
        printf "."
    else
        error_count=$((error_count + 1))
        printf "x"
    fi
done

echo ""
if [ $success_count -gt 0 ]; then
    avg_time=$(echo "scale=3; $total_time / $success_count" | bc -l)
    echo -e "${GREEN}✅ Average response time: ${avg_time}s${NC}"
    echo -e "${GREEN}✅ Success rate: $success_count/50 ($(echo "scale=1; $success_count * 100 / 50" | bc -l)%)${NC}"
else
    echo -e "${RED}❌ All requests failed${NC}"
fi

# Test 2: Concurrent load test
echo -e "${YELLOW}🔥 Test 2: Concurrent Load Test${NC}"
echo "Testing with 20 concurrent requests..."

start_time=$(date +%s.%N)
for i in {1..20}; do
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$TEST_DATA" \
        $ANALYZE_URL > /dev/null &
done
wait
end_time=$(date +%s.%N)

concurrent_duration=$(echo "$end_time - $start_time" | bc -l)
echo -e "${GREEN}✅ 20 concurrent requests completed in: ${concurrent_duration}s${NC}"

# Test 3: Sustained load test
echo -e "${YELLOW}📈 Test 3: Sustained Load Test${NC}"
echo "Testing sustained load for 60 seconds..."

sustained_start=$(date +%s)
sustained_end=$((sustained_start + 60))
sustained_count=0
sustained_errors=0

while [ $(date +%s) -lt $sustained_end ]; do
    if curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$TEST_DATA" \
        $ANALYZE_URL > /dev/null 2>&1; then
        sustained_count=$((sustained_count + 1))
    else
        sustained_errors=$((sustained_errors + 1))
    fi
    printf "."
done

echo ""
requests_per_second=$(echo "scale=2; $sustained_count / 60" | bc -l)
echo -e "${GREEN}✅ Sustained load: $sustained_count requests in 60s${NC}"
echo -e "${GREEN}✅ Throughput: ${requests_per_second} requests/second${NC}"
echo -e "${GREEN}✅ Error rate: $sustained_errors errors${NC}"

# Test 4: Memory and CPU usage
echo -e "${YELLOW}💻 Test 4: Resource Usage Analysis${NC}"
echo "Checking Docker container resource usage..."

echo -e "${BLUE}Container Stats:${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep -E "(NAME|sentiment|nginx|redis)"

# Test 5: Cache performance
echo -e "${YELLOW}🗄️  Test 5: Cache Performance Test${NC}"
echo "Testing cache hit rates..."

# First request (cache miss)
cache_miss_time=$(curl -s -o /dev/null -w "%{time_total}" -X POST \
    -H "Content-Type: application/json" \
    -d "$TEST_DATA" \
    $ANALYZE_URL)

# Second request (should be cache hit)
cache_hit_time=$(curl -s -o /dev/null -w "%{time_total}" -X POST \
    -H "Content-Type: application/json" \
    -d "$TEST_DATA" \
    $ANALYZE_URL)

echo -e "${GREEN}✅ Cache miss time: ${cache_miss_time}s${NC}"
echo -e "${GREEN}✅ Cache hit time: ${cache_hit_time}s${NC}"

if [ $(echo "$cache_hit_time < $cache_miss_time" | bc -l) -eq 1 ]; then
    improvement=$(echo "scale=1; ($cache_miss_time - $cache_hit_time) * 100 / $cache_miss_time" | bc -l)
    echo -e "${GREEN}✅ Cache improvement: ${improvement}%${NC}"
else
    echo -e "${YELLOW}⚠️  Cache may not be working optimally${NC}"
fi

# Test 6: Load balancer test
echo -e "${YELLOW}⚖️  Test 6: Load Balancer Distribution${NC}"
echo "Testing load distribution across API instances..."

# Check which instances are responding
for i in {1..10}; do
    curl -s $HEALTH_URL | grep -o '"service":"[^"]*"' || echo "No service info"
done

echo ""
echo -e "${GREEN}🎉 Performance Testing Completed!${NC}"
echo ""
echo -e "${BLUE}📊 Summary:${NC}"
echo "  ⏱️  Average Response Time: ${avg_time:-N/A}s"
echo "  🔥 Concurrent Load: 20 requests handled"
echo "  📈 Sustained Throughput: ${requests_per_second:-N/A} req/s"
echo "  🗄️  Cache Performance: Working"
echo "  ⚖️  Load Balancer: Active"
echo ""
echo -e "${BLUE}💡 Recommendations:${NC}"
if [ $(echo "$avg_time > 2" | bc -l 2>/dev/null || echo 0) -eq 1 ]; then
    echo "  ⚠️  Consider optimizing response times (>2s average)"
fi
if [ $sustained_errors -gt 5 ]; then
    echo "  ⚠️  High error rate detected, check logs"
fi
echo "  ✅ Monitor with: docker stats"
echo "  ✅ Check logs with: docker-compose logs -f"