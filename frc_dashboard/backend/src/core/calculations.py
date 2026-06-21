#!/usr/bin/env python3
"""
Core Calculation Engine

This module contains the core logic for EPA, OPR, cOPR calculations
and integrates the delta updater functionality.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import math
import re
import ast
from pathlib import Path
import json
import os


class RecursiveLeastSquaresFilter:
    """
    Recursive Least Squares (RLS) Filter for updating team performance metrics.

    This class implements the RLS algorithm to efficiently update EPA, OPR, and cOPR
    metrics as new match data becomes available, without needing to re-invert
    large matrices for each update.
    """

    def __init__(self, num_teams: int, regularization: float = 1.0):
        """
        Initialize the RLS filter.

        Args:
            num_teams: Number of teams in the system
            regularization: Regularization parameter lambda (default: 1.0)
        """
        self.num_teams = num_teams
        self.regularization = regularization

        # Initialize parameter vector (theta) - contains EPA, OPR, and cOPR values
        # Structure: theta[team_idx, metric_idx]
        # 0: EPA (Expected Points Added)
        # 1: OPR (Offensive Power Rating)
        # 2: cOPR_totalPoints
        # 3: cOPR_autoPoints
        # 4: cOPR_teleopPoints
        # 5: cOPR_foulPoints
        self.theta = np.zeros((num_teams, 6))

        # Initialize error covariance matrix P
        self.P = np.eye(num_teams) / regularization

        # Track residual variances for adaptive learning
        self.score_resid_var = 400.0
        self.component_resid_vars = {
            'totalPoints': 1.0,
            'autoPoints': 1.0,
            'teleopPoints': 1.0,
            'foulPoints': 1.0
        }

        # Learning rate for EPA updates
        self.alpha = 0.10

    def calculate_gain_vector(self, x: np.ndarray) -> np.ndarray:
        """
        Calculate the Kalman gain vector K_k for the RLS update.

        Args:
            x: Alliance assignment vector (1 x num_teams)

        Returns:
            K: Gain vector for this update
        """
        denominator = 1.0 + np.dot(x.T, np.dot(self.P, x))
        if denominator <= 0:
            raise RuntimeError("Non-positive update denominator in RLS filter")

        K = np.dot(self.P, x) / denominator
        return K

    def update_parameters(self, x: np.ndarray, y: np.ndarray, K: np.ndarray):
        """
        Update the parameter vector theta using the RLS update rule.

        Args:
            x: Alliance assignment vector
            y: Observed score vector
            K: Gain vector
        """
        prediction = np.dot(x.T, self.theta)
        residual = y - prediction

        # Update theta for all metrics
        self.theta += np.outer(K, residual)

        # Update error covariance matrix P
        self.P = self.P - np.outer(K, np.dot(x.T, self.P))

        return residual

    def update_epa_simple(self, alliance_teams: List[int], actual_score: float, predicted_score: float):
        """
        Update EPA using simple exponential smoothing.

        Args:
            alliance_teams: List of team indices in the alliance
            actual_score: Actual score achieved by the alliance
            predicted_score: Predicted score based on current EPA values
        """
        delta_alliance = actual_score - predicted_score
        delta_per_team = delta_alliance / len(alliance_teams)

        for team_idx in alliance_teams:
            self.theta[team_idx, 0] += self.alpha * delta_per_team

    def get_team_metrics(self, team_idx: int) -> Dict[str, float]:
        """
        Get all metrics for a specific team.

        Args:
            team_idx: Team index

        Returns:
            Dictionary containing all metrics for the team
        """
        return {
            'epa': float(self.theta[team_idx, 0]),
            'opr': float(self.theta[team_idx, 1]),
            'copr_totalPoints': float(self.theta[team_idx, 2]),
            'copr_autoPoints': float(self.theta[team_idx, 3]),
            'copr_teleopPoints': float(self.theta[team_idx, 4]),
            'copr_foulPoints': float(self.theta[team_idx, 5])
        }

    def predict_alliance_score(self, alliance_teams: List[int]) -> Tuple[float, float]:
        """
        Predict alliance score and variance based on current team metrics.

        Args:
            alliance_teams: List of team indices in the alliance

        Returns:
            Tuple of (predicted_score, variance)
        """
        # Create alliance assignment vector
        x = np.zeros(self.num_teams)
        x[alliance_teams] = 1.0

        # Predict score (using OPR as the primary predictor)
        predicted_score = float(np.dot(x, self.theta[:, 1]))  # Use OPR column

        # Calculate variance
        variance = float(np.dot(x.T, np.dot(self.P, x)))

        return predicted_score, variance


class DeltaUpdaterAgent:
    """
    Main Delta Updater Agent that processes match data and updates team metrics.

    This agent handles the complete workflow of:
    1. Loading match data
    2. Processing matches in chronological order
    3. Applying RLS updates to team metrics
    4. Recording before/after states for each match
    """

    def __init__(self):
        """Initialize the Delta Updater Agent."""
        self.team_index = {}  # Mapping from team numbers to indices
        self.teams = []       # List of team numbers in order
        self.rls_filter = None
        self.matches_played = {}  # Track matches played per team
        self.match_history = []   # Store processed match data

    def initialize_from_match_data(self, match_data: pd.DataFrame) -> None:
        """
        Initialize the agent by extracting all unique teams from match data.

        Args:
            match_data: DataFrame containing match data
        """
        # Extract all unique team numbers from the data
        all_teams = set()

        for _, row in match_data.iterrows():
            red_teams = self._parse_team_keys(row.get('alliances.red.team_keys', []))
            blue_teams = self._parse_team_keys(row.get('alliances.blue.team_keys', []))

            all_teams.update(red_teams)
            all_teams.update(blue_teams)

        # Create sorted list and index mapping
        self.teams = sorted(all_teams)
        self.team_index = {team: idx for idx, team in enumerate(self.teams)}

        # Initialize RLS filter
        self.rls_filter = RecursiveLeastSquaresFilter(len(self.teams))

        # Initialize matches played counter
        self.matches_played = {team: 0 for team in self.teams}

        print(f"Initialized Delta Updater with {len(self.teams)} teams")

    def _parse_team_keys(self, team_keys) -> List[int]:
        """
        Parse team keys and extract team numbers.

        Args:
            team_keys: Raw team keys (could be list, string, or None)

        Returns:
            List of team numbers as integers
        """
        if isinstance(team_keys, list):
            return [self._extract_team_number(key) for key in team_keys]
        elif isinstance(team_keys, str):
            return [self._extract_team_number(team_keys)]
        elif team_keys is None or pd.isna(team_keys):
            return []
        else:
            return [self._extract_team_number(team_keys)]

    def _extract_team_number(self, team_key) -> int:
        """
        Extract team number from team key string.

        Args:
            team_key: Team key string (e.g., 'frc254')

        Returns:
            Team number as integer
        """
        if isinstance(team_key, str):
            match = re.search(r'\d+', team_key)
            if match:
                return int(match.group())
        return int(team_key)

    def _build_alliance_vector(self, team_numbers: List[int]) -> np.ndarray:
        """
        Build alliance assignment vector for RLS filter.

        Args:
            team_numbers: List of team numbers

        Returns:
            Alliance assignment vector (1 x num_teams)
        """
        x = np.zeros(len(self.teams))
        team_indices = [self.team_index[team] for team in team_numbers]
        x[team_indices] = 1.0
        return x

    def _build_target_vector(self, match_row: pd.Series, color: str, components: List[str]) -> np.ndarray:
        """
        Build target vector y for RLS update.

        Args:
            match_row: Row containing match data
            color: Alliance color ('red' or 'blue')
            components: List of score breakdown components

        Returns:
            Target vector y
        """
        # Get scores - order matters: [EPA, OPR, totalPoints, autoPoints, teleopPoints, foulPoints]
        y_values = [
            self._get_numeric_value(match_row.get(f'alliances.{color}.score')),  # EPA/OPR target
            self._get_numeric_value(match_row.get(f'alliances.{color}.score')),  # OPR target
        ]

        # Add component targets
        for component in components:
            if component == 'totalPoints':
                y_values.append(self._get_numeric_value(match_row.get(f'alliances.{color}.score')))
            else:
                breakdown_value = self._get_numeric_value(
                    match_row.get(f'score_breakdown.{color}.{component}')
                )
                y_values.append(breakdown_value)

        # Ensure we have exactly 6 values
        while len(y_values) < 6:
            y_values.append(0.0)

        return np.array(y_values[:6])  # Take first 6 to be safe

    def _get_numeric_value(self, value) -> float:
        """
        Convert value to numeric, handling None/NaN cases.

        Args:
            value: Input value

        Returns:
            Numeric value or 0.0 if conversion fails
        """
        if value is None or pd.isna(value):
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def process_match(self, match_row: pd.Series, components: List[str]) -> Dict:
        """
        Process a single match and update team metrics.

        Args:
            match_row: Row containing match data for one match
            components: List of score breakdown components to track

        Returns:
            Dictionary containing before/after metrics for all teams in the match
        """
        result = {
            'match_key': match_row.get('key'),
            'event_key': match_row.get('event_key'),
            'match_number': match_row.get('match_number'),
            'before': [],
            'after': []
        }

        # Process red alliance
        red_teams = self._parse_team_keys(match_row.get('alliances.red.team_keys', []))
        if red_teams:
            result['before'].extend(self._get_team_metrics_before(red_teams, 'red', match_row))

        # Process blue alliance
        blue_teams = self._parse_team_keys(match_row.get('alliances.blue.team_keys', []))
        if blue_teams:
            result['before'].extend(self._get_team_metrics_before(blue_teams, 'blue', match_row))

        # Update metrics for red alliance
        if red_teams:
            self._update_alliance_metrics(red_teams, 'red', match_row, components)
            # Update matches played counter before getting after metrics
            for team in red_teams:
                self.matches_played[team] += 1
            result['after'].extend(self._get_team_metrics_after(red_teams, 'red', match_row))

        # Update metrics for blue alliance
        if blue_teams:
            self._update_alliance_metrics(blue_teams, 'blue', match_row, components)
            # Update matches played counter before getting after metrics
            for team in blue_teams:
                self.matches_played[team] += 1
            result['after'].extend(self._get_team_metrics_after(blue_teams, 'blue', match_row))

        return result

    def _get_team_metrics_before(self, team_numbers: List[int], color: str, match_row: pd.Series) -> List[Dict]:
        """Get team metrics before match processing."""
        team_data = []
        for team in team_numbers:
            if team in self.team_index:
                metrics = self.rls_filter.get_team_metrics(self.team_index[team])
                team_data.append({
                    'team': team,
                    'alliance': color,
                    'phase': 'before',
                    'matches_played': self.matches_played.get(team, 0),
                    **metrics,
                    'match_key': match_row.get('key'),
                    'event_key': match_row.get('event_key'),
                    'match_number': match_row.get('match_number')
                })
        return team_data

    def _get_team_metrics_after(self, team_numbers: List[int], color: str, match_row: pd.Series) -> List[Dict]:
        """Get team metrics after match processing."""
        team_data = []
        for team in team_numbers:
            if team in self.team_index:
                metrics = self.rls_filter.get_team_metrics(self.team_index[team])
                team_data.append({
                    'team': team,
                    'alliance': color,
                    'phase': 'after',
                    'matches_played': self.matches_played.get(team, 0),
                    **metrics,
                    'match_key': match_row.get('key'),
                    'event_key': match_row.get('event_key'),
                    'match_number': match_row.get('match_number')
                })
        return team_data

    def _update_alliance_metrics(self, team_numbers: List[int], color: str, match_row: pd.Series, components: List[str]) -> None:
        """Update metrics for an alliance using RLS filter."""
        if not team_numbers:
            return

        # Get team indices
        team_indices = [self.team_index[team] for team in team_numbers]

        # Build alliance vector x
        x = self._build_alliance_vector(team_numbers)

        # Build target vector y
        y = self._build_target_vector(match_row, color, components)

        # Calculate gain vector
        K = self.rls_filter.calculate_gain_vector(x)

        # Update parameters using RLS
        residual = self.rls_filter.update_parameters(x, y, K)

        # Update residual variances (adaptive learning)
        score_residual = float(residual[0])
        self.rls_filter.score_resid_var = 0.98 * self.rls_filter.score_resid_var + 0.02 * (score_residual ** 2)

        # Update component residual variances
        for i, component in enumerate(['totalPoints', 'autoPoints', 'teleopPoints', 'foulPoints'], start=2):
            if i < len(residual):
                comp_residual = float(residual[i])
                comp_name = component
                if comp_name in self.rls_filter.component_resid_vars:
                    self.rls_filter.component_resid_vars[comp_name] = (
                        0.98 * self.rls_filter.component_resid_vars[comp_name] +
                        0.02 * (comp_residual ** 2)
                    )

    def process_matches(self, match_data: pd.DataFrame, components: List[str]) -> pd.DataFrame:
        """
        Process all matches in chronological order and return metrics history.

        Args:
            match_data: DataFrame containing all match data
            components: List of score breakdown components to track

        Returns:
            DataFrame containing before/after metrics for all teams across all matches
        """
        # Sort matches chronologically
        sorted_matches = self._sort_matches(match_data)

        all_results = []

        for _, match_row in sorted_matches.iterrows():
            try:
                result = self.process_match(match_row, components)
                all_results.extend(result['before'])
                all_results.extend(result['after'])
                self.match_history.append(result)
            except Exception as e:
                print(f"Error processing match {match_row.get('key')}: {e}")
                continue

        return pd.DataFrame(all_results)

    def _sort_matches(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sort matches chronologically."""
        sort_cols = ['actual_time', 'time', 'event_key', 'match_number', 'set_number']
        available_cols = [col for col in sort_cols if col in df.columns]

        if available_cols:
            return df.sort_values(available_cols, na_position='last').reset_index(drop=True)
        return df.reset_index(drop=True)

    def get_current_metrics(self) -> pd.DataFrame:
        """
        Get current metrics for all teams.

        Returns:
            DataFrame containing current metrics for all teams
        """
        data = []
        for team in self.teams:
            metrics = self.rls_filter.get_team_metrics(self.team_index[team])
            data.append({
                'team': team,
                'matches_played': self.matches_played.get(team, 0),
                **metrics
            })

        return pd.DataFrame(data)

    def save_metrics_to_csv(self, filename: str) -> None:
        """
        Save current team metrics to CSV file.

        Args:
            filename: Output CSV filename
        """
        metrics_df = self.get_current_metrics()
        metrics_df.to_csv(filename, index=False)
        print(f"Saved team metrics to {filename}")


def infer_score_components(df: pd.DataFrame) -> List[str]:
    """
    Infer available score breakdown components from match data.

    Args:
        df: DataFrame containing match data

    Returns:
        List of available score breakdown components
    """
    components = set()

    for col in df.columns:
        if col.startswith('score_breakdown.'):
            parts = col.split('.', 2)
            if len(parts) == 3:
                component = parts[2]
                # Check if component has actual data
                if df[col].notna().any():
                    components.add(component)

    # Ensure we have the required components
    required = {'totalPoints', 'autoPoints', 'teleopPoints', 'foulPoints'}
    found = components & required

    # If we don't have the required components, use what we can find
    if not found:
        # Fall back to using all numeric breakdown components
        for col in df.columns:
            if col.startswith('score_breakdown.') and df[col].dtype in ['int64', 'float64']:
                parts = col.split('.', 2)
                if len(parts) == 3:
                    components.add(parts[2])

    return sorted(components)


# Global instance for the application
updater_agent = DeltaUpdaterAgent()

def initialize_system(match_data: pd.DataFrame) -> None:
    """
    Initialize the calculation system with match data.

    Args:
        match_data: DataFrame containing match data
    """
    global updater_agent
    components = infer_score_components(match_data)
    updater_agent.initialize_from_match_data(match_data)
    return components

def process_all_matches(match_data: pd.DataFrame) -> pd.DataFrame:
    """
    Process all matches and return the results.

    Args:
        match_data: DataFrame containing match data

    Returns:
        DataFrame with before/after metrics for all teams
    """
    global updater_agent
    components = infer_score_components(match_data)
    return updater_agent.process_matches(match_data, components)

def get_current_team_metrics() -> pd.DataFrame:
    """
    Get current metrics for all teams.

    Returns:
        DataFrame containing current metrics for all teams
    """
    global updater_agent
    return updater_agent.get_current_metrics()

def update_with_new_match(match_data: Dict[str, Any]) -> Dict:
    """
    Update the system with a new match.

    Args:
        match_data: Dictionary containing match data

    Returns:
        Dictionary with updated metrics
    """
    global updater_agent

    # Convert to DataFrame
    match_df = pd.DataFrame([match_data])
    components = infer_score_components(match_df)

    # Process the match
    result = updater_agent.process_match(match_df.iloc[0], components)

    return result

if __name__ == "__main__":
    print("Core Calculation Engine")
    print("=" * 50)

    # Example usage
    sample_data = pd.DataFrame([
        {
            'key': '2026_m1',
            'event_key': '2026test',
            'match_number': 1,
            'alliances.red.team_keys': ['frc254', 'frc1678', 'frc971'],
            'alliances.blue.team_keys': ['frc1114', 'frc2056', 'frc1323'],
            'alliances.red.score': 120,
            'alliances.blue.score': 100,
            'score_breakdown.red.totalPoints': 120,
            'score_breakdown.red.autoPoints': 40,
            'score_breakdown.red.teleopPoints': 75,
            'score_breakdown.red.foulPoints': 5,
            'score_breakdown.blue.totalPoints': 100,
            'score_breakdown.blue.autoPoints': 30,
            'score_breakdown.blue.teleopPoints': 65,
            'score_breakdown.blue.foulPoints': 5,
            'actual_time': '2026-01-01 10:00:00'
        }
    ])

    # Initialize and process
    components = initialize_system(sample_data)
    print(f"Inferred components: {components}")

    results = process_all_matches(sample_data)
    print(f"\nProcessed {len(results)} team-match records")
    print("\nSample results:")
    print(results.head(10))

    print("\nCurrent team metrics:")
    current_metrics = get_current_team_metrics()
    print(current_metrics)
