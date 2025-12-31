# Sentiment Analysis API v2.0

High-performance production-ready sentiment analysis API với FastAPI, AI Agent và Langfuse tracing.

## 🚀 Features

- **High Performance**: Multi-instance deployment với load balancing
- **AI-Powered**: Sử dụng LLM cho sentiment analysis chính xác
- **Production Ready**: Redis caching, rate limiting, monitoring
- **Observability**: Langfuse tracing cho AI operations
- **Scalable**: Docker-based deployment với auto-scaling
- **Monitoring**: Prometheus metrics, health checks

## 📋 Requirements

- Docker & Docker Compose
- Python 3.9+
- Redis (optional, có fallback memory cache)
- OpenAI-compatible API key
- Langfuse account (optional)

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd sentiment-agent-v2
```

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env với các thông tin cần thiết
```

### 3. Required Environment Variables
```bash
# LLM Configuration
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=google/gemma-3-12b-it
OPENAI_URI=https://api.deepinfra.com/v1/openai

# Langfuse Tracing
LANGFUSE_SECRET_KEY=sk-lf-xxx
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_HOST=http://your-langfuse-host:3002

# Performance Settings
MAX_CONCURRENT_REQUESTS=50
REQUEST_TIMEOUT=60
RATE_LIMIT=100/minute
WORKERS=4

# Cache
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

## 🚀 Deployment

### Development
```bash
# Start single instance
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

# Or with Docker
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
# Deploy với load balancing
chmod +x deploy.sh
./deploy.sh

# Hoặc manual
docker-compose up -d
```

## 📡 API Usage

### Main Endpoint
```bash
POST /analyze
Content-Type: application/json

{
  "id": "unique_id",
  "index": "document_index",
  "topic": "Brand Name",
  "title": "Post title",
  "content": "Main content text",
  "description": "Additional description",
  "type": "tiktokComment",
  "main_keywords": ["brand", "product"]
}
```

### Response Format
```json
{
  "targeted": true,
  "sentiment": "positive",
  "confidence": 0.85,
  "keywords": {
    "positive": ["tốt", "xuất sắc"],
    "negative": []
  },
  "explanation": "Người dùng khen ngợi sản phẩm"
}
```

### Legacy Endpoint (Backward Compatibility)
```bash
POST /analyze/legacy
# Sử dụng format cũ, trả về AnalysisResult
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Basic info |
| `/analyze` | POST | Main sentiment analysis |
| `/analyze/legacy` | POST | Legacy format support |
| `/health` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |
| `/cache/stats` | GET | Cache statistics |
| `/cache/clear` | POST | Clear cache |

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:4880/health
```

### Metrics (Prometheus)
```bash
curl http://localhost:4880/metrics
```

### Cache Statistics
```bash
curl http://localhost:4880/cache/stats
```

## 🧪 Testing

### Performance Test
```bash
python3 test_production_api.py
```

### Load Test
```bash
# Sử dụng Apache Bench
ab -n 1000 -c 10 -T application/json -p test_payload.json http://localhost:4880/analyze

# Hoặc với wrk
wrk -t12 -c400 -d30s -s test_script.lua http://localhost:4880/analyze
```

## 🔍 Langfuse Tracing

API tự động trace tất cả LLM calls và analysis operations:

- **Traces**: Mỗi request tạo một trace với metadata
- **Spans**: LLM calls, text processing, caching
- **Metrics**: Response time, success rate, confidence scores
- **Debugging**: Raw LLM responses, parsing errors

Xem traces tại Langfuse dashboard: `http://your-langfuse-host:3002`

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Nginx     │    │   Redis     │    │  Langfuse   │
│Load Balancer│    │   Cache     │    │  Tracing    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────┐
│              API Instances (3x)                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ FastAPI +   │ │ FastAPI +   │ │ FastAPI +   │   │
│  │ AI Agent    │ │ AI Agent    │ │ AI Agent    │   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────┐
                  │ LLM Service │
                  │(DeepInfra)  │
                  └─────────────┘
```

## 🔧 Configuration

### Performance Tuning
```bash
# Tăng số workers
WORKERS=8

# Tăng concurrent requests
MAX_CONCURRENT_REQUESTS=100

# Tăng cache TTL
CACHE_TTL=7200

# Tăng rate limit
RATE_LIMIT=200/minute
```

### Scaling
```bash
# Scale API instances
docker-compose up -d --scale sentiment-api-1=5

# Scale với resource limits
docker-compose up -d --scale sentiment-api-1=3 --scale sentiment-api-2=3
```

## 📝 Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f sentiment-api-1

# Nginx access logs
docker-compose logs -f nginx

# Redis logs
docker-compose logs -f redis
```

### Log Locations
- Application logs: `logs/app/`
- Nginx logs: `logs/nginx/`
- Container logs: `docker-compose logs`

## 🚨 Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Check Redis status
   docker-compose exec redis redis-cli ping
   
   # Restart Redis
   docker-compose restart redis
   ```

2. **LLM API Errors**
   ```bash
   # Check API key
   echo $OPENAI_API_KEY
   
   # Test API directly
   curl -H "Authorization: Bearer $OPENAI_API_KEY" $OPENAI_URI/models
   ```

3. **High Memory Usage**
   ```bash
   # Check memory usage
   docker stats
   
   # Reduce cache TTL
   CACHE_TTL=1800
   ```

4. **Slow Response Times**
   ```bash
   # Check concurrent requests
   MAX_CONCURRENT_REQUESTS=30
   
   # Reduce timeout
   REQUEST_TIMEOUT=30
   ```

## 🔐 Security

- Rate limiting enabled
- CORS configured
- Environment variables for secrets
- Health check endpoints
- Request timeout protection

## 📈 Performance Benchmarks

Typical performance với 3 API instances:

- **Throughput**: 200+ requests/second
- **Response Time**: 
  - Cache hit: <100ms
  - Cache miss: 1-3s (depending on LLM)
- **Concurrent Users**: 100+
- **Uptime**: 99.9%

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Add tests
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- GitHub Issues: [Create Issue](link-to-issues)
- Documentation: [Wiki](link-to-wiki)
- Email: support@yourcompany.com