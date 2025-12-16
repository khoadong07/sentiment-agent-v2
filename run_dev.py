#!/usr/bin/env python3
"""
Development server script - không cần Docker
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv("app/.env")

# Add app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir.parent))

def check_environment():
    """Kiểm tra environment variables"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in .env file or environment")
        return False
    
    return True

def check_mongodb():
    """Kiểm tra MongoDB connection"""
    try:
        from app.db import mongo_conn
        # Test connection
        mongo_conn.client.admin.command('ping')
        print("✅ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {str(e)}")
        print("API will still start but may fail on requests requiring database")
        return False

def main():
    """Main function"""
    print("🚀 Starting Sentiment Analysis API (Development Mode)")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check MongoDB (non-blocking)
    check_mongodb()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start server
    try:
        import uvicorn
        uvicorn.run(
            "app.api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()