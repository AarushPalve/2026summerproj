#!/usr/bin/env python3
"""
Matches API Endpoints

API endpoints for match-related operations.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import pandas as pd
import json
from pathlib import Path
import os

# Import core calculation functions
from core.calculations import (
    initialize_system,
    process_all_matches,
    get_current_team_metrics,
    update_with_new_match,
    infer_score_components
)

router = APIRouter()


@router.post("/upload", summary="Upload match data CSV")
async def upload_match_data(file: UploadFile = File(...)):
    """
    Upload a CSV file containing match data and process it.

    Args:
        file: CSV file containing match data

    Returns:
        JSON response with processing results
    """
    try:
        # Save the uploaded file temporarily
        temp_path = f"data/raw/{file.filename}"
        os.makedirs("data/raw", exist_ok=True)

        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        # Read the CSV file
        match_data = pd.read_csv(temp_path, low_memory=False)

        # Initialize system with the match data
        components = initialize_system(match_data)

        # Process all matches
        results = process_all_matches(match_data)

        # Get current team metrics
        current_metrics = get_current_team_metrics()

        return JSONResponse({
            "status": "success",
            "message": "Match data processed successfully",
            "teams": len(current_metrics),
            "matches_processed": len(match_data),
            "components": components,
            "sample_metrics": current_metrics.head(10).to_dict(orient="records")
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


@router.get("/teams", summary="Get current team metrics")
async def get_teams():
    """
    Get current metrics for all teams.

    Returns:
        JSON response with team metrics
    """
    try:
        metrics = get_current_team_metrics()
        return JSONResponse({
            "status": "success",
            "data": metrics.to_dict(orient="records"),
            "count": len(metrics)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving team metrics: {str(e)}")


@router.post("/update", summary="Update with new match")
async def update_match(match_data: Dict):
    """
    Update the system with a new match.

    Args:
        match_data: Dictionary containing match data

    Returns:
        JSON response with updated metrics
    """
    try:
        result = update_with_new_match(match_data)
        return JSONResponse({
            "status": "success",
            "message": "Match processed successfully",
            "data": result
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing match: {str(e)}")


@router.get("/components", summary="Get available score components")
async def get_components():
    """
    Get available score breakdown components.

    Returns:
        JSON response with component list
    """
    try:
        # Try to read from existing data
        data_files = list(Path("data/raw").glob("frc_matches_*.csv"))

        if not data_files:
            return JSONResponse({
                "status": "success",
                "components": []
            })

        # Read the most recent file
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        match_data = pd.read_csv(latest_file, low_memory=False)

        components = infer_score_components(match_data)

        return JSONResponse({
            "status": "success",
            "components": components
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving components: {str(e)}")


@router.get("/history", summary="Get match history")
async def get_match_history(limit: int = 100):
    """
    Get recent match history.

    Args:
        limit: Maximum number of matches to return

    Returns:
        JSON response with match history
    """
    try:
        # This would be implemented with actual history tracking
        # For now, return a placeholder response
        return JSONResponse({
            "status": "success",
            "data": [],
            "message": "Match history endpoint not yet implemented"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving match history: {str(e)}")
