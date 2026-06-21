#!/usr/bin/env python3
"""
Teams API Endpoints

API endpoints for team-related operations.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import pandas as pd

# Import core calculation functions
from core.calculations import get_current_team_metrics

router = APIRouter()


@router.get("/", summary="Get all teams")
async def get_all_teams():
    """
    Get metrics for all teams.

    Returns:
        JSON response with all team metrics
    """
    try:
        metrics = get_current_team_metrics()
        return JSONResponse({
            "status": "success",
            "data": metrics.to_dict(orient="records"),
            "count": len(metrics)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving teams: {str(e)}")


@router.get("/{team_number}", summary="Get specific team")
async def get_team(team_number: int):
    """
    Get metrics for a specific team.

    Args:
        team_number: Team number to retrieve

    Returns:
        JSON response with team metrics
    """
    try:
        metrics = get_current_team_metrics()
        team_metrics = metrics[metrics['team'] == team_number]

        if len(team_metrics) == 0:
            raise HTTPException(status_code=404, detail=f"Team {team_number} not found")

        return JSONResponse({
            "status": "success",
            "data": team_metrics.iloc[0].to_dict()
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving team: {str(e)}")


@router.get("/rankings", summary="Get team rankings")
async def get_rankings(
    sort_by: str = "epa",
    order: str = "desc",
    limit: Optional[int] = None
):
    """
    Get team rankings sorted by a specific metric.

    Args:
        sort_by: Metric to sort by (epa, opr, etc.)
        order: Sort order (asc or desc)
        limit: Maximum number of teams to return

    Returns:
        JSON response with ranked teams
    """
    try:
        metrics = get_current_team_metrics()

        # Validate sort_by parameter
        valid_metrics = ['team', 'matches_played', 'epa', 'opr', 'copr_totalPoints',
                        'copr_autoPoints', 'copr_teleopPoints', 'copr_foulPoints']
        if sort_by not in valid_metrics:
            raise HTTPException(status_code=400, detail=f"Invalid sort metric: {sort_by}")

        # Sort teams
        ascending = order.lower() == "asc"
        ranked = metrics.sort_values(by=sort_by, ascending=ascending)

        # Apply limit
        if limit is not None and limit > 0:
            ranked = ranked.head(limit)

        return JSONResponse({
            "status": "success",
            "data": ranked.to_dict(orient="records"),
            "count": len(ranked),
            "sorted_by": sort_by,
            "order": order
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving rankings: {str(e)}")


@router.get("/compare", summary="Compare multiple teams")
async def compare_teams(teams: List[int] = Query(...)):
    """
    Compare metrics for multiple teams.

    Args:
        teams: List of team numbers to compare

    Returns:
        JSON response with comparison data
    """
    try:
        if len(teams) == 0:
            raise HTTPException(status_code=400, detail="No teams specified for comparison")

        metrics = get_current_team_metrics()
        comparison = metrics[metrics['team'].isin(teams)]

        if len(comparison) == 0:
            raise HTTPException(status_code=404, detail="None of the specified teams were found")

        return JSONResponse({
            "status": "success",
            "data": comparison.to_dict(orient="records"),
            "count": len(comparison)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing teams: {str(e)}")


@router.get("/stats", summary="Get team statistics summary")
async def get_team_stats():
    """
    Get summary statistics for all teams.

    Returns:
        JSON response with statistics summary
    """
    try:
        metrics = get_current_team_metrics()

        if len(metrics) == 0:
            return JSONResponse({
                "status": "success",
                "message": "No team data available"
            })

        # Calculate statistics
        stats = {
            "total_teams": len(metrics),
            "avg_matches_played": float(metrics['matches_played'].mean()),
            "avg_epa": float(metrics['epa'].mean()),
            "avg_opr": float(metrics['opr'].mean()),
            "max_epa": float(metrics['epa'].max()),
            "min_epa": float(metrics['epa'].min()),
            "top_team": int(metrics.loc[metrics['epa'].idxmax(), 'team']),
            "bottom_team": int(metrics.loc[metrics['epa'].idxmin(), 'team'])
        }

        return JSONResponse({
            "status": "success",
            "stats": stats
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving team stats: {str(e)}")
