import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from app.services.sentiment_service import sentiment_service
from app.schemas import SentimentRequest, SentimentResponse, PostInput, AnalysisResult
from app.cache import cache
from app.config import MAX_CONCURRENT_REQUESTS, REQUEST_TIMEOUT, RATE_LIMIT, ENVIRONMENT

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('sentiment_requests_total', 'Total sentiment analysis requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('sentiment_request_duration_seconds', 'Request duration in seconds')
CACHE_HITS = Counter('sentiment_cache_hits_total', 'Total cache hits')
CACHE_MISSES = Counter('sentiment_cache_misses_total', 'Total cache misses')

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Semaphore để giới hạn concurrent requests
request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management cho FastAPI"""
    # Startup
    logger.info("Starting Sentiment Analysis API v2.0...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Max concurrent requests: {MAX_CONCURRENT_REQUESTS}")
    logger.info(f"Request timeout: {REQUEST_TIMEOUT}s")
    logger.info(f"Rate limit: {RATE_LIMIT}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sentiment Analysis API...")
    cache.clear()

# Tạo FastAPI app với lifecycle
app = FastAPI(
    title="Sentiment Analysis API",
    description="High-performance API phân tích sentiment và keyword matching với Langfuse tracing",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if ENVIRONMENT != "production" else None
)

# Middleware stack (thứ tự quan trọng)
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compression
app.add_middleware(SlowAPIMiddleware)  # Rate limiting

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "Sentiment Analysis API v2.0",
        "status": "running",
        "environment": ENVIRONMENT,
        "cache_stats": cache.stats()
    }

@app.post("/analyze", response_model=SentimentResponse)
@limiter.limit(RATE_LIMIT)
async def analyze_sentiment(request: Request, sentiment_request: SentimentRequest, background_tasks: BackgroundTasks):
    """
    High-performance sentiment analysis với caching, concurrency control và Langfuse tracing
    """
    start_time = time.time()
    
    async with request_semaphore:  # Limit concurrent requests
        try:
            with REQUEST_DURATION.time():
                logger.info(f"Processing request for ID: {sentiment_request.id}")
                
                # Prepare cache data
                if sentiment_request.type in {"fbPageComment", "fbGroupComment", "fbUserComment", "forumComment",
                                            "newsComment", "youtubeComment", "tiktokComment", "snsComment",
                                            "linkedinComment", "ecommerceComment", "threadsComment"}:
                    merged_text = sentiment_request.content or ""
                else:
                    text_parts = [
                        part for part in [
                            sentiment_request.title or "",
                            sentiment_request.content or "",
                            sentiment_request.description or ""
                        ] if part.strip()
                    ]
                    merged_text = " ".join(text_parts)
                
                cache_data = {
                    "index": sentiment_request.index or "",
                    "merged_text": merged_text,
                    "type": sentiment_request.type,
                    "main_keywords": sentiment_request.main_keywords
                }
                
                # Check cache first
                cached_result = cache.get(cache_data)
                if cached_result:
                    CACHE_HITS.inc()
                    REQUEST_COUNT.labels(method="POST", endpoint="/analyze", status="200").inc()
                    logger.info(f"Cache hit - Response time: {time.time() - start_time:.3f}s")
                    return SentimentResponse(**cached_result)
                
                CACHE_MISSES.inc()
                
                # Process with timeout
                try:
                    result = await asyncio.wait_for(
                        asyncio.to_thread(sentiment_service.analyze, sentiment_request),
                        timeout=REQUEST_TIMEOUT
                    )
                    
                    # Cache the result in background
                    background_tasks.add_task(cache_result, cache_data, result.dict())
                    
                    processing_time = time.time() - start_time
                    REQUEST_COUNT.labels(method="POST", endpoint="/analyze", status="200").inc()
                    logger.info(f"Analysis completed - Response time: {processing_time:.3f}s")
                    
                    return result
                    
                except asyncio.TimeoutError:
                    REQUEST_COUNT.labels(method="POST", endpoint="/analyze", status="408").inc()
                    logger.error(f"Request timeout after {REQUEST_TIMEOUT}s")
                    return SentimentResponse(
                        targeted=False,
                        sentiment="neutral",
                        confidence=0.0,
                        keywords={"positive": [], "negative": []},
                        explanation="Request timeout"
                    )
                    
        except Exception as e:
            REQUEST_COUNT.labels(method="POST", endpoint="/analyze", status="500").inc()
            logger.error(f"Internal error: {str(e)}")
            return SentimentResponse(
                targeted=False,
                sentiment="neutral",
                confidence=0.0,
                keywords={"positive": [], "negative": []},
                explanation=f"Internal error: {str(e)}"
            )

@app.post("/analyze/legacy", response_model=AnalysisResult)
@limiter.limit(RATE_LIMIT)
async def analyze_sentiment_legacy(request: Request, post: PostInput, background_tasks: BackgroundTasks):
    """
    Legacy endpoint để backward compatibility với format cũ
    """
    # Convert PostInput to SentimentRequest
    sentiment_request = SentimentRequest(
        id=post.id,
        index=post.index,
        title=post.title,
        content=post.content,
        description=post.description,
        type=post.type or "",
        main_keywords=post.main_keywords
    )
    
    # Call main analyze function
    result = await analyze_sentiment(request, sentiment_request, background_tasks)
    
    # Convert to legacy format
    return AnalysisResult(
        id=sentiment_request.id,
        index=sentiment_request.index or "",
        type=sentiment_request.type,
        targeted=result.targeted,
        sentiment=result.sentiment,
        confidence=result.confidence,
        keywords={
            "positive": result.keywords.get("positive", []),
            "negative": result.keywords.get("negative", [])
        },
        explanation=result.explanation,
        log_level=1 if result.targeted else 0
    )

def cache_result(cache_data: dict, result: dict):
    """Background task để cache kết quả"""
    try:
        cache.set(cache_data, result)
    except Exception as e:
        logger.error(f"Cache error: {str(e)}")

@app.get("/health")
def health_check():
    """Comprehensive health check"""
    try:
        cache_stats = cache.stats()
        
        return {
            "status": "healthy",
            "service": "sentiment-analysis", 
            "version": "2.0.0",
            "environment": ENVIRONMENT,
            "cache": cache_stats,
            "concurrent_limit": MAX_CONCURRENT_REQUESTS,
            "features": {
                "langfuse_tracing": True,
                "redis_cache": cache_stats.get("type") == "redis",
                "rate_limiting": True,
                "prometheus_metrics": True
            }
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "service": "sentiment-analysis",
            "version": "2.0.0",
            "error": "Health check failed"
        }

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/cache/stats")
def cache_stats():
    """Cache statistics endpoint"""
    return cache.stats()

@app.post("/cache/clear")
def clear_cache():
    """Clear cache endpoint (admin only)"""
    cache.clear()
    return {"message": "Cache cleared successfully"}

# Debug endpoints (chỉ trong development)
if ENVIRONMENT != "production":
    @app.post("/debug/validate")
    def debug_validate(data: dict):
        """Debug endpoint để test validation"""
        try:
            request = SentimentRequest(**data)
            return {
                "status": "valid",
                "parsed_data": request.dict()
            }
        except Exception as e:
            return {
                "status": "invalid", 
                "error": str(e),
                "received_data": data
            }