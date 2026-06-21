#!/usr/bin/env python3
"""
Predictions API Endpoints

API endpoints for match prediction operations.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List
from pydantic import BaseModel

# Import ML pipeline
from core.ml_pipeline import predict_match_outcome, initialize_ml_pipeline

router = APIRouter()


class PredictionRequest(BaseModel):
    """Request model for match prediction."""
    red_mean_features: List[float]
    red_std_features: List[float]
    blue_mean_features: List[float]
    blue_std_features: List[float]
    is_qm: bool = True
    is_sf: bool = False
    is_f: bool = False


@router.post("/", summary="Predict match outcome")
async def predict_match(request: PredictionRequest):
    """
    Predict the outcome of a match using ML models.

    Args:
        request: Prediction request containing alliance features

    Returns:
        JSON response with prediction results
    """
    try:
        # Validate input sizes
        if len(request.red_mean_features) != 72:
            raise HTTPException(status_code=400, detail="red_mean_features must have 72 elements")
        if len(request.red_std_features) != 73:
            raise HTTPException(status_code=400, detail="red_std_features must have 73 elements")
        if len(request.blue_mean_features) != 72:
            raise HTTPException(status_code=400, detail="blue_mean_features must have 72 elements")
        if len(request.blue_std_features) != 73:
            raise HTTPException(status_code=400, detail="blue_std_features must have 73 elements")

        # Initialize ML pipeline if not already initialized
        initialize_ml_pipeline()

        # Make prediction
        result = predict_match_outcome(
            red_mean_features=request.red_mean_features,
            red_std_features=request.red_std_features,
            blue_mean_features=request.blue_mean_features,
            blue_std_features=request.blue_std_features,
            is_qm=request.is_qm,
            is_sf=request.is_sf,
            is_f=request.is_f
        )

        return JSONResponse({
            "status": "success",
            "prediction": result
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.post("/batch", summary="Batch predict multiple matches")
async def batch_predict(requests: List[PredictionRequest]):
    """
    Predict outcomes for multiple matches.

    Args:
        requests: List of prediction requests

    Returns:
        JSON response with batch prediction results
    """
    try:
        if len(requests) == 0:
            raise HTTPException(status_code=400, detail="No prediction requests provided")

        # Initialize ML pipeline
        initialize_ml_pipeline()

        # Process each request
        results = []
        for i, req in enumerate(requests):
            try:
                result = predict_match_outcome(
                    red_mean_features=req.red_mean_features,
                    red_std_features=req.red_std_features,
                    blue_mean_features=req.blue_mean_features,
                    blue_std_features=req.blue_std_features,
                    is_qm=req.is_qm,
                    is_sf=req.is_sf,
                    is_f=req.is_f
                )
                results.append({
                    "request_id": i,
                    "prediction": result
                })
            except Exception as e:
                results.append({
                    "request_id": i,
                    "error": str(e)
                })

        return JSONResponse({
            "status": "success",
            "results": results,
            "processed": len(results)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")


@router.get("/health", summary="Check ML pipeline health")
async def check_health():
    """
    Check if the ML pipeline is initialized and ready.

    Returns:
        JSON response with health status
    """
    try:
        # Try to initialize the pipeline
        pipeline = initialize_ml_pipeline()
        return JSONResponse({
            "status": "healthy",
            "message": "ML pipeline is ready",
            "has_rf_model": pipeline.rf_model is not None
        })
    except Exception as e:
        return JSONResponse({
            "status": "degraded",
            "message": str(e),
            "error": type(e).__name__
        })
