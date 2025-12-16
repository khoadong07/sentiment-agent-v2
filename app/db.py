import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import (
    MONGO_URI, 
    DB_NAME, 
    MONGO_MAX_POOL_SIZE,
    MONGO_MIN_POOL_SIZE, 
    MONGO_MAX_IDLE_TIME_MS
)

logger = logging.getLogger(__name__)

def create_mongo_connection():
    """
    Tạo kết nối MongoDB với connection pooling tối ưu cho production
    """
    try:
        # Optimized settings for MongoDB Atlas
        client = MongoClient(
            MONGO_URI,
            # Connection pool settings
            maxPoolSize=MONGO_MAX_POOL_SIZE,
            minPoolSize=MONGO_MIN_POOL_SIZE,
            maxIdleTimeMS=MONGO_MAX_IDLE_TIME_MS,
            
            # Timeout settings (longer for Atlas)
            serverSelectionTimeoutMS=10000,  # 10s for Atlas
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            
            # Performance settings for Atlas
            retryWrites=True,
            retryReads=True,
            readPreference='primary',  # Primary for Atlas
            
            # Connection management
            maxConnecting=10,
            waitQueueTimeoutMS=10000,
            
            # Atlas specific settings
            ssl=True,
            tlsAllowInvalidCertificates=False
        )
        
        # Test connection
        client.admin.command('ping')
        logger.info(f"MongoDB connection pool initialized: max={MONGO_MAX_POOL_SIZE}, min={MONGO_MIN_POOL_SIZE}")
        
        return client
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Lỗi kết nối MongoDB: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Lỗi không xác định khi kết nối MongoDB: {str(e)}")
        raise

# Lazy connection pattern cho production
class MongoConnection:
    _instance = None
    _client = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _ensure_connection(self):
        """Lazy initialization - chỉ kết nối khi cần thiết"""
        if not self._initialized:
            try:
                logger.info(f"Initializing MongoDB connection to: {MONGO_URI}")
                self._client = create_mongo_connection()
                self._initialized = True
                logger.info(f"Database connection established: {DB_NAME}")
                
                # Test the topics collection
                test_count = self._client[DB_NAME]["qc_sentiment"].count_documents({}, limit=1)
                logger.info(f"Topics collection accessible, sample count: {test_count}")
                
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                self._initialized = False
                self._client = None
                raise
    
    @property
    def client(self):
        self._ensure_connection()
        return self._client
    
    @property
    def db(self):
        self._ensure_connection()
        return self._client[DB_NAME]
    
    @property
    def topics_col(self):
        self._ensure_connection()
        return self.db["qc_sentiment"]

# Global instances - lazy initialization
mongo_conn = MongoConnection()

# Backward compatibility
def get_client():
    return mongo_conn.client

def get_db():
    return mongo_conn.db

def get_topics_col():
    return mongo_conn.topics_col

# For backward compatibility
client = None  # Will be initialized on first access
db = None      # Will be initialized on first access
topics_col = None  # Will be initialized on first access

logger.info("MongoDB connection configured (lazy initialization)")