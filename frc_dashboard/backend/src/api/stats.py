#!/usr/bin/env python3
"""
Stats API Endpoints

API endpoints for statistical analysis and system information.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
import pandas as pd
import os

# Import core calculation functions
from core.calculations import get_current_team_metrics

router = APIRouter()


@router.get("/system", summary="Get system information")
async def get_system_info():
    """
    Get information about the system status.

    Returns:
        JSON response with system information
    """
    try:
        # Get team count
        metrics = get_current_team_metrics()
        team_count = len(metrics)

        # Count data files
        data_files = []
        if os.path.exists("data/raw"):
            data_files = [f for f in os.listdir("data/raw") if f.endswith('.csv')]

        # Count models
        model_files = []
        if os.path.exists("data/models"):
            model_files = [f for f in os.listdir("data/models") if f.endswith(('.onnx', '.joblib', '.json'))]

        return JSONResponse({
            "status": "success",
            "system": {
                "teams_loaded": team_count,
                "data_files": len(data_files),
                "model_files": len(model_files),
                "data_directory": "data/raw",
                "models_directory": "data/models"
            }
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system info: {str(e)}")


@router.get("/calculations", summary="Get calculation statistics")
async def get_calculation_stats():
    """
    Get statistics about the current calculations.

    Returns:
        JSON response with calculation statistics
    """
    try:
        metrics = get_current_team_metrics()

        if len(metrics) == 0:
            return JSONResponse({
                "status": "success",
                "message": "No calculation data available"
            })

        # Calculate statistics
        stats = {
            "teams": len(metrics),
            "total_matches_played": int(metrics['matches_played'].sum()),
            "avg_matches_per_team": float(metrics['matches_played'].mean()),
            "epa_range": {
                "min": float(metrics['epa'].min()),
                "max": float(metrics['epa'].max()),
                "mean": float(metrics['epa'].mean()),
                "std": float(metrics['epa'].std())
            },
            "opr_range": {
                "min": float(metrics['opr'].min()),
                "max": float(metrics['opr'].max()),
                "mean": float(metrics['opr'].mean()),
                "std": float(metrics['opr'].std())
            }
        }

        return JSONResponse({
            "status": "success",
            "stats": stats
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving calculation stats: {str(e)}")


@router.get("/distribution", summary="Get metric distributions")
async def get_distributions():
    """
    Get distribution statistics for all metrics.

    Returns:
        JSON response with distribution data
    """
    try:
        metrics = get_current_team_metrics()

        if len(metrics) == 0:
            return JSONResponse({
                "status": "success",
                "message": "No distribution data available"
            })

        # Calculate distributions for each metric
        distributions = {}
        numeric_cols = ['epa', 'opr', 'copr_totalPoints', 'copr_autoPoints',
                       'copr_teleopPoints', 'copr_foulPoints']

        for col in numeric_cols:
            if col in metrics.columns:
                distributions[col] = {
                    "mean": float(metrics[col].mean()),
                    "median": float(metrics[col].median()),
                    "std": float(metrics[col].std()),
                    "min": float(metrics[col].min()),
                    "max": float(metrics[col].max()),
                    "q25": float(metrics[col].quantile(0.25)),
                    "q75": float(metrics[col].quantile(0.75))
                }

        return JSONResponse({
            "status": "success",
            "distributions": distributions
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving distributions: {str(e)}")
