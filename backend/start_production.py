#!/usr/bin/env python3
"""
Production startup script for Visual Product Matcher API
Handles environment-specific configurations and graceful startup
"""

import os
import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables and files are present"""
    logger.info("Checking production environment...")
    
    # Check for required files
    required_files = [
        "main.py",
        "models.py", 
        "similarity.py",
        "pinecone_service.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing required files: {missing_files}")
        return False
    
    # Check for database
    db_files = ["product_database_deploy.json", "product_database.json"]
    db_found = False
    for db_file in db_files:
        if Path(db_file).exists():
            logger.info(f"Found database file: {db_file}")
            db_found = True
            break
    
    if not db_found:
        logger.error("No product database found!")
        return False
    
    # Check environment variables
    env_vars = {
        "PORT": os.getenv("PORT", "8000"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY")
    }
    
    logger.info(f"Environment configuration:")
    for key, value in env_vars.items():
        if key.endswith("_KEY"):
            logger.info(f"  {key}: {'✓ Set' if value else '✗ Missing'}")
        else:
            logger.info(f"  {key}: {value}")
    
    return True

def main():
    """Main startup function"""
    logger.info("🚀 Starting Visual Product Matcher API (Production)")
    
    if not check_environment():
        logger.error("Environment check failed. Exiting.")
        sys.exit(1)
    
    # Import and run the FastAPI app
    try:
        import uvicorn
        from main import app
        
        port = int(os.getenv("PORT", 8000))
        host = os.getenv("HOST", "0.0.0.0")
        
        logger.info(f"Starting server on {host}:{port}")
        
        uvicorn.run(
            app, 
            host=host, 
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
