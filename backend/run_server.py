#!/usr/bin/env python3
"""
FastAPI server startup script
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"🚀 Starting FastAPI server on {host}:{port}")
    print(f"📚 API docs available at: http://{host}:{port}/docs")
    print(f"🔗 API root: http://{host}:{port}/")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    ) 