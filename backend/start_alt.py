#!/usr/bin/env python3
"""
Alternative start script for Render deployment
"""

import os
import sys
import uvicorn

def main():
    try:
        # Import the app
        from main import app
        
        # Get port from environment or default
        port = int(os.environ.get("PORT", 8000))
        
        print(f"Starting server on port {port}")
        
        # Start uvicorn server
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            workers=1,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
