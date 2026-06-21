#!/usr/bin/env python3
"""
FRC Strategic Dashboard - FastAPI Backend

Main application entry point for the FastAPI backend server.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from typing import Optional
import os

# Import API routes
from api import matches, teams, predictions, stats

# Create FastAPI app
app = FastAPI(
    title="FRC Strategic Dashboard API",
    description="Backend API for FRC Strategic Dashboard",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up static files serving
# We'll serve static files from a subpath to avoid conflicts with API routes
project_root = Path(__file__).parent.parent.parent
frontend_build_path = project_root / "frontend" / "build"
static_files_path = project_root / "static"

# Check if frontend build has actual content (index.html)
frontend_has_content = (
    os.path.exists(frontend_build_path) and
    any(f.name == "index.html" for f in os.scandir(frontend_build_path))
)

# Determine which static directory to use
serve_dir = None
if frontend_has_content:
    serve_dir = frontend_build_path
    print(f"Serving frontend from: {frontend_build_path}")
elif os.path.exists(static_files_path):
    serve_dir = static_files_path
    print(f"Serving static files from: {static_files_path}")

# Function to serve index.html for SPA routing
async def serve_frontend(request: Request):
    index_path = serve_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"detail": "Not Found"})

# Add catch-all route for frontend after API routes
if serve_dir:
    # Mount static files for assets (JS, CSS, etc.) if they exist
    static_assets_dir = serve_dir / "static"
    if static_assets_dir.exists():
        app.mount("/static", StaticFiles(directory=static_assets_dir), name="static-assets")

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include API routes
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Include the API router BEFORE mounting static files
# This ensures API routes take precedence
app.include_router(api_router)

# Add catch-all route for frontend SPA
if serve_dir:
    @app.get("/")
    async def read_root():
        return FileResponse(serve_dir / "index.html")

    # For SPA routing - serve index.html for all non-API, non-static routes
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        # Don't intercept API or static file routes
        if full_path.startswith("api/") or full_path.startswith("static/"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        index_path = serve_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

# Error handling
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": f"An error occurred: {str(exc)}", "error": type(exc).__name__},
    )

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server."""
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True,
    )

if __name__ == "__main__":
    # Check if running in development mode
    import argparse
    parser = argparse.ArgumentParser(description="FRC Strategic Dashboard Backend")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    args = parser.parse_args()

    # Ensure data directories exist
    os.makedirs("data/models", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)

    print(f"Starting FRC Strategic Dashboard API server...")
    print(f"Host: {args.host}, Port: {args.port}")
    print(f"API Docs: http://{args.host}:{args.port}/api/docs")

    run_server(host=args.host, port=args.port, reload=args.reload)
