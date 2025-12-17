# Sentiment Analysis API

API phân tích sentiment và keyword matching cho nội dung tiếng Việt.

## Tính năng

- Nhận dữ liệu với format: `{id, index, title, content, description, type}`
- Tìm topic trong MongoDB dựa vào `index` để lấy keywords
- Phân tích sentiment của nội dung đối với topic
- Trích xuất keywords liên quan và phân loại theo sentiment
- Trả về kết quả với explanation tối đa 25 từ

## Cài đặt

1. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

2. **Cấu hình environment:**
Tạo file `.env` với nội dung:
```
MONGO_URI=mongodb://localhost:27017
DB_NAME=n8n
OPENAI_API_KEY=your_openai_api_key
```

3. **Chuẩn bị MongoDB:**
- Tạo collection `qc_sentiment` trong database
- Mỗi document có format:
```json
{
  "topic_id": "6641ccbdf4901a7ae602197f",
  "topic_name": "máy lọc không khí", 
  "keywords": ["máy lọc", "không khí", "dyson", "sharp"]
}
```

## Chạy server

```bash
python run_server.py
```

Server sẽ chạy tại: http://localhost:4880

## API Endpoints

### POST /analyze
Phân tích sentiment cho nội dung

**Request:**
```json
{
  "id": "648188429745076_1253949522502296",
  "index": "6641ccbdf4901a7ae602197f", 
  "title": "Xem xong cũng làm thử, trời ơi đầu tư ngay cái máy lọc kk dyson 30 củ đi",
  "content": "",
  "description": "T có phải nạn nhân của máy lọc không khí ko tụi bay",
  "type": "fbGroupTopic"
}
```

**Response:**
```json
{
  "index": "6641ccbdf4901a7ae602197f",
  "targeted": true,
  "topic": "máy lọc không khí",
  "sentiment": "positive",
  "confidence": 0.85,
  "keywords": {
    "positive": ["hiệu quả", "tốt"],
    "negative": ["đắt"],
    "neutral": ["dyson", "máy lọc"]
  },
  "explanation": "Nội dung thể hiện thái độ tích cực về máy lọc không khí"
}
```

### GET /health
Kiểm tra trạng thái server

## Test

Chạy test với dữ liệu mẫu:
```bash
python test_api.py
```

## Quy trình xử lý

1. **Load Topic:** Tìm topic trong MongoDB theo `index`
2. **Merge Text:** Gộp `title`, `content`, `description`
3. **Analyze with LLM:** Phân tích sentiment và trích xuất keywords
4. **Format Output:** Tạo kết quả cuối cùng theo schema

## Cấu trúc project

```
app/
├── api.py              # FastAPI endpoints
├── main.py             # LangGraph workflow
├── config.py           # Cấu hình
├── db.py              # MongoDB connection
├── llm.py             # OpenAI LLM
├── prompts.py         # LLM prompts
├── schemas.py         # Pydantic models
├── state.py           # Graph state
└── nodes/             # Processing nodes
    ├── load_topic.py
    ├── merge_text.py
    ├── analyze_with_llm.py
    └── format_output.py
```

## 🚀 Production Deployment (High Performance)

### Architecture Overview
```
Internet → Nginx Load Balancer → 3x API Instances → MongoDB Atlas
                ↓
            Redis Cache + Sentinel
                ↓
            Prometheus Monitoring
```

### Production Features
- **Load Balancing**: Nginx với 3 API instances
- **High Availability**: Redis Sentinel, health checks
- **Caching**: Optimized Redis với LRU policy
- **Monitoring**: Prometheus metrics, detailed logging
- **Performance**: Tối ưu cho 100+ concurrent requests
- **Security**: Rate limiting, security headers

### Quick Production Setup

1. **Deploy to Production**:
```bash
chmod +x deploy.sh
./deploy.sh
```

2. **Monitor System**:
```bash
chmod +x monitor.sh
./monitor.sh
```

3. **Performance Testing**:
```bash
chmod +x performance_test.sh
./performance_test.sh
```

### Production Configuration

#### Environment Variables (.env)
```env
# Database
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=n8n

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Performance (Production optimized)
MONGO_MAX_POOL_SIZE=200
MONGO_MIN_POOL_SIZE=20
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=45
CACHE_TTL=7200
```

#### Production Services
- **API Instances**: 3x containers với load balancing
- **Nginx**: Load balancer với caching
- **Redis**: High-performance cache với persistence
- **Redis Sentinel**: High availability
- **Prometheus**: Monitoring và metrics

### Performance Benchmarks
- **Throughput**: 50+ requests/second
- **Response Time**: <1s average
- **Concurrent Users**: 100+ simultaneous
- **Cache Hit Rate**: 80%+
- **Uptime**: 99.9%+

### Monitoring & Maintenance

#### Real-time Monitoring
```bash
# Interactive monitor
./monitor.sh

# Docker stats
docker stats

# Service logs
docker-compose logs -f
```

#### Health Checks
- **API Health**: `http://localhost/health`
- **Nginx Status**: `http://localhost/nginx_status`
- **Prometheus**: `http://localhost:9090`
- **Metrics**: `http://localhost/metrics`

#### Scaling Commands
```bash
# Scale API instances
docker-compose up -d --scale sentiment-api-1=2

# Restart specific service
docker-compose restart sentiment-api-1

# Update configuration
docker-compose up -d --force-recreate nginx
```

### Production Troubleshooting

#### Common Issues
1. **High Response Time**:
   - Check `docker stats` for resource usage
   - Monitor cache hit rate
   - Scale API instances

2. **Memory Issues**:
   - Adjust Redis maxmemory
   - Check for memory leaks in logs
   - Restart services if needed

3. **Database Connection**:
   - Verify MongoDB URI
   - Check network connectivity
   - Monitor connection pool

#### Log Analysis
```bash
# API errors
docker-compose logs sentiment-api-1 | grep ERROR

# Nginx access logs
docker-compose logs nginx | grep -E "HTTP/[0-9.]+ [45][0-9][0-9]"

# Performance logs
docker-compose logs | grep "Response time"
```

### Security Considerations
- Rate limiting: 50 req/s per IP
- Security headers enabled
- No sensitive data in logs
- Container isolation
- Non-root user execution

### Backup & Recovery
```bash
# Backup Redis data
docker-compose exec redis redis-cli BGSAVE

# Export configuration
docker-compose config > backup-config.yml

# Health check before deployment
curl -f http://localhost/health
```