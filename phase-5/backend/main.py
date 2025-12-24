"""
Entry point for the Todo Backend API.
Re-exports the FastAPI app from src.main for uvicorn compatibility.
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import the actual application
from src.main import app

__all__ = ["app"]