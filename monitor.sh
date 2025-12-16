#!/bin/bash

# Production monitoring script for Sentiment Analysis API

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
API_URL="http://localhost"
REFRESH_INTERVAL=5

show_header() {
    clear
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           Sentiment Analysis API - Production Monitor        ║${NC}"
    echo -e "${BLUE}║                    $(date '+%Y-%m-%d %H:%M:%S')                     ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_services() {
    echo -e "${YELLOW}🔍 Service Status:${NC}"
    
    # Check Docker services
    services=("sentiment-api-1" "sentiment-api-2" "sentiment-api-3" "nginx" "redis" "prometheus")
    
    for service in "${services[@]}"; do
        if docker-compose ps -q $service > /dev/null 2>&1; then
            status=$(docker-compose ps $service | tail -n +3 | awk '{print $4}')
            if [[ $status == *"Up"* ]]; then
                echo -e "  ✅ $service: ${GREEN}Running${NC}"
            else
                echo -e "  ❌ $service: ${RED}$status${NC}"
            fi
        else
            echo -e "  ❌ $service: ${RED}Not found${NC}"
        fi
    done
    echo ""
}

check_health() {
    echo -e "${YELLOW}🏥 Health Checks:${NC}"
    
    # API Health
    if curl -s -f $API_URL/health > /dev/null 2>&1; then
        response=$(curl -s $API_URL/health | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")
        echo -e "  ✅ API Health: ${GREEN}$response${NC}"
    else
        echo -e "  ❌ API Health: ${RED}Failed${NC}"
    fi
    
    # Load Balancer
    if curl -s -f $API_URL > /dev/null 2>&1; then
        echo -e "  ✅ Load Balancer: ${GREEN}Active${NC}"
    else
        echo -e "  ❌ Load Balancer: ${RED}Failed${NC}"
    fi
    
    # Redis
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo -e "  ✅ Redis: ${GREEN}Connected${NC}"
    else
        echo -e "  ❌ Redis: ${RED}Failed${NC}"
    fi
    
    echo ""
}

show_metrics() {
    echo -e "${YELLOW}📊 Performance Metrics:${NC}"
    
    # Get API metrics if available
    if curl -s -f $API_URL/metrics > /dev/null 2>&1; then
        metrics=$(curl -s $API_URL/metrics 2>/dev/null)
        
        # Parse cache stats if available
        cache_hits=$(echo "$metrics" | jq -r '.cache_stats.hits // "N/A"' 2>/dev/null || echo "N/A")
        cache_misses=$(echo "$metrics" | jq -r '.cache_stats.misses // "N/A"' 2>/dev/null || echo "N/A")
        
        echo -e "  📈 Cache Hits: $cache_hits"
        echo -e "  📉 Cache Misses: $cache_misses"
        
        if [[ "$cache_hits" != "N/A" && "$cache_misses" != "N/A" ]]; then
            total=$((cache_hits + cache_misses))
            if [ $total -gt 0 ]; then
                hit_rate=$(echo "scale=1; $cache_hits * 100 / $total" | bc -l 2>/dev/null || echo "N/A")
                echo -e "  🎯 Cache Hit Rate: ${hit_rate}%"
            fi
        fi
    fi
    
    echo ""
}

show_resource_usage() {
    echo -e "${YELLOW}💻 Resource Usage:${NC}"
    
    # Docker stats
    docker stats --no-stream --format "  {{.Name}}: CPU {{.CPUPerc}} | Memory {{.MemUsage}}" | grep -E "(sentiment|nginx|redis)" | head -6
    
    echo ""
}

show_recent_logs() {
    echo -e "${YELLOW}📋 Recent Activity (Last 10 lines):${NC}"
    
    # Show recent API logs
    docker-compose logs --tail=5 sentiment-api-1 2>/dev/null | tail -5 | while read line; do
        echo -e "  ${BLUE}API1:${NC} $line"
    done
    
    # Show recent Nginx logs
    docker-compose logs --tail=3 nginx 2>/dev/null | tail -3 | while read line; do
        echo -e "  ${GREEN}NGINX:${NC} $line"
    done
    
    echo ""
}

show_quick_stats() {
    echo -e "${YELLOW}⚡ Quick Performance Test:${NC}"
    
    # Test response time
    response_time=$(curl -s -o /dev/null -w "%{time_total}" $API_URL/health 2>/dev/null || echo "error")
    
    if [ "$response_time" != "error" ]; then
        echo -e "  ⏱️  Response Time: ${response_time}s"
        
        if [ $(echo "$response_time < 0.5" | bc -l 2>/dev/null || echo 0) -eq 1 ]; then
            echo -e "  🚀 Performance: ${GREEN}Excellent${NC}"
        elif [ $(echo "$response_time < 1.0" | bc -l 2>/dev/null || echo 0) -eq 1 ]; then
            echo -e "  ✅ Performance: ${YELLOW}Good${NC}"
        else
            echo -e "  ⚠️  Performance: ${RED}Needs attention${NC}"
        fi
    else
        echo -e "  ❌ Response: ${RED}Failed${NC}"
    fi
    
    echo ""
}

show_commands() {
    echo -e "${BLUE}🔧 Available Commands:${NC}"
    echo -e "  ${GREEN}r${NC} - Refresh now"
    echo -e "  ${GREEN}l${NC} - Show full logs"
    echo -e "  ${GREEN}s${NC} - Show service status"
    echo -e "  ${GREEN}t${NC} - Run performance test"
    echo -e "  ${GREEN}q${NC} - Quit"
    echo ""
}

# Main monitoring loop
main() {
    echo -e "${GREEN}Starting Production Monitor...${NC}"
    echo -e "${YELLOW}Press 'q' to quit, 'r' to refresh, 'h' for help${NC}"
    echo ""
    
    while true; do
        show_header
        check_services
        check_health
        show_metrics
        show_resource_usage
        show_recent_logs
        show_quick_stats
        
        echo -e "${BLUE}Next refresh in ${REFRESH_INTERVAL}s... (Press any key for commands)${NC}"
        
        # Wait for input or timeout
        if read -t $REFRESH_INTERVAL -n 1 key; then
            case $key in
                'q'|'Q')
                    echo -e "\n${GREEN}Monitoring stopped.${NC}"
                    exit 0
                    ;;
                'r'|'R')
                    continue
                    ;;
                'l'|'L')
                    echo -e "\n${YELLOW}Full logs (Press Ctrl+C to return):${NC}"
                    docker-compose logs -f
                    ;;
                's'|'S')
                    echo -e "\n${YELLOW}Service details:${NC}"
                    docker-compose ps
                    read -p "Press Enter to continue..."
                    ;;
                't'|'T')
                    echo -e "\n${YELLOW}Running performance test...${NC}"
                    ./performance_test.sh
                    read -p "Press Enter to continue..."
                    ;;
                'h'|'H')
                    show_commands
                    read -p "Press Enter to continue..."
                    ;;
            esac
        fi
    done
}

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose not found${NC}"
    exit 1
fi

# Check if bc is available for calculations
if ! command -v bc &> /dev/null; then
    echo -e "${YELLOW}⚠️  'bc' not found, some calculations may not work${NC}"
fi

# Start monitoring
main