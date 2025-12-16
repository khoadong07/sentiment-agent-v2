import asyncio
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.main import agent
from app.schemas import PostInput, AnalysisResult
from app.cache import cache
from app.db import mongo_conn
from app.config import MAX_CONCURRENT_REQUESTS, REQUEST_TIMEOUT

# Cấu hình logging
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Semaphore để giới hạn concurrent requests
request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management cho FastAPI"""
    # Startup
    logger.info("Starting Sentiment Analysis API...")
    logger.info(f"Max concurrent requests: {MAX_CONCURRENT_REQUESTS}")
    logger.info(f"Request timeout: {REQUEST_TIMEOUT}s")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sentiment Analysis API...")
    cache.clear()

# Tạo FastAPI app với lifecycle
app = FastAPI(
    title="Sentiment Analysis API",
    description="High-performance API phân tích sentiment và keyword matching",
    version="2.0.0",
    lifespan=lifespan
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
        "cache_stats": cache.stats()
    }

@app.post("/analyze")
@limiter.limit("100/minute")  # Rate limiting
async def analyze_sentiment(request: Request, post: PostInput, background_tasks: BackgroundTasks):
    """
    High-performance sentiment analysis với caching và concurrency control
    """
    async with request_semaphore:  # Limit concurrent requests
        start_time = time.time()
        
        try:
            logger.info(f"Processing request for post ID: {post.id}")
            
            # Prepare data for caching - tạo merged_text để cache
            input_data = post.model_dump()  # Use model_dump instead of dict()
            title = (input_data.get("title") or "").strip()
            content = (input_data.get("content") or "").strip()
            description = (input_data.get("description") or "").strip()
            text_parts = [part for part in [title, content, description] if part]
            merged_text = " ".join(text_parts)
            
            # Check cache first
            cache_data = {"index": input_data["index"], "merged_text": merged_text}
            cached_result = cache.get(cache_data)
            if cached_result:
                logger.info(f"Cache hit - Response time: {time.time() - start_time:.3f}s")
                return cached_result
            
            # Process with timeout
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(process_analysis, input_data),
                    timeout=REQUEST_TIMEOUT
                )
                
                # Cache the result in background
                background_tasks.add_task(cache_result, cache_data, result)
                
                processing_time = time.time() - start_time
                logger.info(f"Analysis completed - Response time: {processing_time:.3f}s")
                
                return result
                
            except asyncio.TimeoutError:
                logger.error(f"Request timeout after {REQUEST_TIMEOUT}s")
                return {
                    "index": input_data.get("index", ""),
                    "targeted": False,
                    "topic": "Timeout",
                    "sentiment": "neutral",
                    "confidence": 0.0,
                    "keywords": {"positive": [], "negative": [], "neutral": []},
                    "explanation": "Request timeout"
                }
                
        except Exception as e:
            logger.error(f"Internal error: {str(e)}")
            return {
                "index": input_data.get("index", "") if 'input_data' in locals() else "",
                "targeted": False,
                "topic": "Error",
                "sentiment": "neutral",
                "confidence": 0.0,
                "keywords": {"positive": [], "negative": [], "neutral": []},
                "explanation": f"Internal error: {str(e)}"
            }

def process_analysis(input_data: dict) -> dict:
    """Synchronous processing function"""
    try:
        state = agent.invoke({"input_data": input_data})
        result = state.get("final_result", {})
        
        # Ensure result is completely serializable
        clean_result = {
            "index": str(result.get("index", "")),
            "targeted": bool(result.get("targeted", False)),
            "topic": str(result.get("topic", "")),
            "sentiment": str(result.get("sentiment", "neutral")),
            "confidence": float(result.get("confidence", 0.0)),
            "keywords": {
                "positive": list(result.get("keywords", {}).get("positive", [])),
                "negative": list(result.get("keywords", {}).get("negative", [])),
                "neutral": list(result.get("keywords", {}).get("neutral", []))
            },
            "explanation": str(result.get("explanation", ""))
        }
        
        return clean_result
            
    except Exception as e:
        logger.error(f"Process analysis error: {str(e)}")
        # Return a clean error response instead of raising
        return {
            "index": input_data.get("index", ""),
            "targeted": False,
            "topic": "Error",
            "sentiment": "neutral",
            "confidence": 0.0,
            "keywords": {"positive": [], "negative": [], "neutral": []},
            "explanation": f"Lỗi xử lý: {str(e)}"
        }

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
        # Test MongoDB connection
        db_status = "healthy"
        try:
            mongo_conn.client.admin.command('ping')
        except Exception as e:
            db_status = "error"
        
        # Get cache stats safely
        cache_size = 0
        try:
            cache_info = cache.stats()
            cache_size = int(cache_info.get("size", 0))
        except Exception:
            pass
        
        return {
            "status": "healthy",
            "service": "sentiment-analysis", 
            "version": "2.0.0",
            "database": db_status,
            "cache": {
                "size": cache_size,
                "max_size": 1000
            },
            "concurrent_limit": int(MAX_CONCURRENT_REQUESTS)
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "service": "sentiment-analysis",
            "version": "2.0.0",
            "error": "Health check failed"
        }



@app.post("/test-validation")
def test_validation(data: dict):
    """Debug endpoint để test validation"""
    try:
        post = PostInput(**data)
        return {
            "status": "valid",
            "parsed_data": post.dict()
        }
    except Exception as e:
        return {
            "status": "invalid", 
            "error": str(e),
            "received_data": data
        }

@app.post("/debug-llm")
def debug_llm_response(data: dict):
    """Debug endpoint để test LLM response trực tiếp"""
    try:
        from app.llm import llm
        from app.prompts import SENTIMENT_ANALYSIS_PROMPT
        
        # Simple test prompt
        test_prompt = SENTIMENT_ANALYSIS_PROMPT.format(
            topic_name="Dyson",
            keywords=["dyson", "máy lọc không khí"],
            text=data.get("text", "Test text")
        )
        
        response = llm.invoke(test_prompt)
        raw_content = response.content
        
        # Try to parse
        from app.nodes.analyze_with_llm import parse_llm_response
        parsed_result = parse_llm_response(raw_content)
        
        return {
            "raw_response": raw_content,
            "parsed_result": parsed_result,
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }