#!/usr/bin/env python3
"""
Run the FastAPI application with environment variable loading.
"""
import uvicorn
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.resolve())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Get port from environment variable or use default 8000
    port = int(os.getenv("PORT", 8000))
    
    # Run the FastAPI application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=[str(Path(__file__).parent / "app")],
        workers=1 if os.getenv("ENV") == "development" else None
    )
