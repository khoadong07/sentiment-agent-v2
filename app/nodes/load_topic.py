from app.db import mongo_conn
import logging

logger = logging.getLogger(__name__)

# Cache topics in memory để giảm DB calls
_topic_cache = {}

def load_topic(state):
    """
    Tìm topic trong MongoDB với in-memory caching
    """
    try:
        index = state["input_data"]["index"]
        
        # Check memory cache first
        if index in _topic_cache:
            logger.debug(f"Topic cache hit for index: {index}")
            return {**state, "topic": _topic_cache[index]}
        
        logger.debug(f"Loading topic from DB: {index}")
        
        # Query với projection để chỉ lấy fields cần thiết
        topic = mongo_conn.topics_col.find_one(
            {"topic_id": index},
            {"topic_name": 1, "keywords": 1, "topic_id": 1, "_id": 0}
        )
        
        if not topic:
            logger.warning(f"Topic not found: {index}")
            raise ValueError(f"Topic not found: {index}")
        
        # Cache topic for future requests
        _topic_cache[index] = topic
        
        # Limit cache size
        if len(_topic_cache) > 1000:
            # Remove oldest 20% entries
            keys_to_remove = list(_topic_cache.keys())[:200]
            for key in keys_to_remove:
                del _topic_cache[key]
        
        logger.debug(f"Topic loaded: {topic.get('topic_name', 'Unknown')}")
        return {**state, "topic": topic}
        
    except Exception as e:
        logger.error(f"Load topic error: {str(e)}")
        raise