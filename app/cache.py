import json
import hashlib
import logging
from typing import Optional, Dict, Any
from app.config import CACHE_TTL

logger = logging.getLogger(__name__)

class MemoryCache:
    """
    In-memory cache đơn giản cho production nhỏ
    Có thể thay thế bằng Redis cho scale lớn hơn
    """
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._max_size = 1000  # Giới hạn số lượng items
    
    def _generate_key(self, data: Dict[str, Any]) -> str:
        """Tạo cache key từ input data"""
        # Cache dựa trên index, merged text và type
        cache_data = {
            "index": data.get("index", ""),
            "text": data.get("merged_text", ""),
            "type": data.get("type", "")
        }
        content = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, data: Dict[str, Any]) -> Optional[Dict]:
        """Lấy kết quả từ cache"""
        try:
            key = self._generate_key(data)
            cached_item = self._cache.get(key)
            
            if cached_item:
                import time
                if time.time() - cached_item["timestamp"] < CACHE_TTL:
                    logger.info(f"Cache hit for key: {key[:8]}...")
                    return cached_item["data"]
                else:
                    # Expired, remove from cache
                    del self._cache[key]
                    logger.info(f"Cache expired for key: {key[:8]}...")
            
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    def set(self, data: Dict[str, Any], result: Dict) -> None:
        """Lưu kết quả vào cache"""
        try:
            key = self._generate_key(data)
            
            # Cleanup old entries if cache is full
            if len(self._cache) >= self._max_size:
                self._cleanup_old_entries()
            
            import time
            self._cache[key] = {
                "data": result,
                "timestamp": time.time()
            }
            
            logger.info(f"Cache set for key: {key[:8]}...")
            
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
    
    def _cleanup_old_entries(self):
        """Xóa 20% entries cũ nhất"""
        import time
        current_time = time.time()
        
        # Sort by timestamp and remove oldest 20%
        sorted_items = sorted(
            self._cache.items(), 
            key=lambda x: x[1]["timestamp"]
        )
        
        remove_count = len(sorted_items) // 5  # 20%
        for i in range(remove_count):
            key = sorted_items[i][0]
            del self._cache[key]
        
        logger.info(f"Cleaned up {remove_count} old cache entries")
    
    def clear(self):
        """Xóa toàn bộ cache"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def stats(self) -> Dict:
        """Thống kê cache"""
        return {
            "size": len(self._cache),
            "max_size": self._max_size
        }

# Global cache instance
cache = MemoryCache()