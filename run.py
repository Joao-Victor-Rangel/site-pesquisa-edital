#!/usr/bin/env python3
"""
FundingAI Backend Server
Run with: python run.py
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print("🚀 Starting FundingAI Backend Server...")
    print(f"📡 Server will run on: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📊 API docs available at: http://{host}:{port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )