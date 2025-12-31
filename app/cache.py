import json
import hashlib
import logging
from typing import Optional, Dict, Any
import redis
from app.config import REDIS_URL, CACHE_TTL

logger = logging.getLogger(__name__)

class CacheService:
    """Production Redis cache service với fallback to memory"""
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
            self.redis_client = None
            self._memory_cache = {}
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate consistent cache key from request data"""
        # Create a consistent string representation
        cache_data = {
            "index": data.get("index", ""),
            "merged_text": data.get("merged_text", ""),
            "type": data.get("type", ""),
            "main_keywords": sorted(data.get("main_keywords", []))
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"sentiment:{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def get(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached result"""
        try:
            cache_key = self._generate_cache_key(request_data)
            
            if self.redis_client:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            else:
                # Fallback to memory cache
                return self._memory_cache.get(cache_key)
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    def set(self, request_data: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Cache result"""
        try:
            cache_key = self._generate_cache_key(request_data)
            
            if self.redis_client:
                self.redis_client.setex(
                    cache_key, 
                    CACHE_TTL, 
                    json.dumps(result)
                )
            else:
                # Fallback to memory cache with simple cleanup
                self._memory_cache[cache_key] = result
                if len(self._memory_cache) > 1000:  # Simple cleanup
                    # Remove oldest 100 items
                    keys_to_remove = list(self._memory_cache.keys())[:100]
                    for key in keys_to_remove:
                        del self._memory_cache[key]
                        
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    "type": "redis",
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory_human", "0B"),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                }
            else:
                return {
                    "type": "memory",
                    "size": len(self._memory_cache),
                    "max_size": 1000
                }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"type": "error", "message": str(e)}
    
    def clear(self) -> None:
        """Clear cache"""
        try:
            if self.redis_client:
                # Clear only sentiment analysis keys
                keys = self.redis_client.keys("sentiment:*")
                if keys:
                    self.redis_client.delete(*keys)
            else:
                self._memory_cache.clear()
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

# Global cache instance
cache = CacheService()