#!/usr/bin/env python3
"""
Simplified Delta Updater

This module replaces the overly complex DeltaUpdaterAgent with a simpler,
more focused implementation that handles the core RLS filtering functionality
without unnecessary abstractions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import re


class SimpleRLSFilter:
    """
    Simplified Recursive Least Squares (RLS) Filter for updating team performance metrics.

    This class implements the core RLS algorithm without unnecessary complexity.
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

        # Initialize parameter vector (theta) - contains EPA and OPR values
        # Structure: theta[team_idx, 0] = EPA, theta[team_idx, 1] = OPR
        self.theta = np.zeros((num_teams, 2))

        # Initialize error covariance matrix P
        self.P = np.eye(num_teams) / regularization

        # Track residual variance for adaptive learning
        self.score_resid_var = 400.0

        # Learning rate for EPA updates
        self.alpha = 0.10

    def update(self, alliance_teams: List[int], actual_score: float) -> None:
        """
        Update team metrics using RLS filter.

        Args:
            alliance_teams: List of team indices in the alliance
            actual_score: Actual score achieved by the alliance
        """
        # Create alliance assignment vector
        x = np.zeros(self.num_teams)
        x[alliance_teams] = 1.0

        # Predict score using current OPR values
        predicted_score = float(np.dot(x, self.theta[:, 1]))

        # Calculate gain vector
        denominator = 1.0 + np.dot(x.T, np.dot(self.P, x))
        if denominator <= 0:
            raise RuntimeError("Non-positive update denominator in RLS filter")
        K = np.dot(self.P, x) / denominator

        # Update parameters
        residual = actual_score - predicted_score
        self.theta[:, 1] += K * residual  # Update OPR
        self.theta[:, 0] += self.alpha * residual / len(alliance_teams)  # Update EPA

        # Update error covariance matrix
        self.P = self.P - np.outer(K, np.dot(x.T, self.P))

        # Update residual variance (adaptive learning)
        self.score_resid_var = 0.98 * self.score_resid_var + 0.02 * (residual ** 2)

    def get_team_metrics(self, team_idx: int) -> Dict[str, float]:
        """
        Get metrics for a specific team.

        Args:
            team_idx: Team index

        Returns:
            Dictionary containing EPA and OPR for the team
        """
        return {
            'epa': float(self.theta[team_idx, 0]),
            'opr': float(self.theta[team_idx, 1])
        }

    def predict_score(self, alliance_teams: List[int]) -> Tuple[float, float]:
        """
        Predict alliance score and variance.

        Args:
            alliance_teams: List of team indices in the alliance

        Returns:
            Tuple of (predicted_score, variance)
        """
        x = np.zeros(self.num_teams)
        x[alliance_teams] = 1.0

        predicted_score = float(np.dot(x, self.theta[:, 1]))
        variance = float(np.dot(x.T, np.dot(self.P, x)))

        return predicted_score, variance


class SimpleDeltaUpdater:
    """
    Simplified Delta Updater that processes match data and updates team metrics.

    This class handles the core workflow without unnecessary abstractions.
    """

    def __init__(self):
        """Initialize the Delta Updater."""
        self.team_index = {}  # Mapping from team numbers to indices
        self.teams = []       # List of team numbers in order
        self.rls_filter = None
        self.matches_played = {}  # Track matches played per team

    def initialize(self, match_data: pd.DataFrame) -> None:
        """
        Initialize the updater by extracting all unique teams from match data.

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
        self.rls_filter = SimpleRLSFilter(len(self.teams))

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

    def process_match(self, match_row: pd.Series) -> Dict:
        """
        Process a single match and update team metrics.

        Args:
            match_row: Row containing match data for one match

        Returns:
            Dictionary containing metrics for all teams in the match
        """
        result = {
            'match_key': match_row.get('key'),
            'event_key': match_row.get('event_key'),
            'match_number': match_row.get('match_number'),
            'teams': []
        }

        # Process red alliance
        red_teams = self._parse_team_keys(match_row.get('alliances.red.team_keys', []))
        red_score = self._get_numeric_value(match_row.get('alliances.red.score'))

        if red_teams and not pd.isna(red_score):
            # Get before metrics
            for team in red_teams:
                if team in self.team_index:
                    metrics = self.rls_filter.get_team_metrics(self.team_index[team])
                    result['teams'].append({
                        'team': team,
                        'alliance': 'red',
                        'phase': 'before',
                        'matches_played': self.matches_played.get(team, 0),
                        **metrics,
                        'match_key': match_row.get('key'),
                        'event_key': match_row.get('event_key'),
                        'match_number': match_row.get('match_number')
                    })

            # Update metrics
            team_indices = [self.team_index[team] for team in red_teams]
            self.rls_filter.update(team_indices, red_score)

            # Update matches played counter
            for team in red_teams:
                self.matches_played[team] += 1

            # Get after metrics
            for team in red_teams:
                if team in self.team_index:
                    metrics = self.rls_filter.get_team_metrics(self.team_index[team])
                    result['teams'].append({
                        'team': team,
                        'alliance': 'red',
                        'phase': 'after',
                        'matches_played': self.matches_played.get(team, 0),
                        **metrics,
                        'match_key': match_row.get('key'),
                        'event_key': match_row.get('event_key'),
                        'match_number': match_row.get('match_number')
                    })

        # Process blue alliance
        blue_teams = self._parse_team_keys(match_row.get('alliances.blue.team_keys', []))
        blue_score = self._get_numeric_value(match_row.get('alliances.blue.score'))

        if blue_teams and not pd.isna(blue_score):
            # Get before metrics
            for team in blue_teams:
                if team in self.team_index:
                    metrics = self.rls_filter.get_team_metrics(self.team_index[team])
                    result['teams'].append({
                        'team': team,
                        'alliance': 'blue',
                        'phase': 'before',
                        'matches_played': self.matches_played.get(team, 0),
                        **metrics,
                        'match_key': match_row.get('key'),
                        'event_key': match_row.get('event_key'),
                        'match_number': match_row.get('match_number')
                    })

            # Update metrics
            team_indices = [self.team_index[team] for team in blue_teams]
            self.rls_filter.update(team_indices, blue_score)

            # Update matches played counter
            for team in blue_teams:
                self.matches_played[team] += 1

            # Get after metrics
            for team in blue_teams:
                if team in self.team_index:
                    metrics = self.rls_filter.get_team_metrics(self.team_index[team])
                    result['teams'].append({
                        'team': team,
                        'alliance': 'blue',
                        'phase': 'after',
                        'matches_played': self.matches_played.get(team, 0),
                        **metrics,
                        'match_key': match_row.get('key'),
                        'event_key': match_row.get('event_key'),
                        'match_number': match_row.get('match_number')
                    })

        return result

    def _get_numeric_value(self, value) -> float:
        """
        Convert value to numeric, handling None/NaN cases.

        Args:
            value: Input value

        Returns:
            Numeric value or NaN if conversion fails
        """
        if value is None or pd.isna(value):
            return float('nan')
        try:
            return float(value)
        except (ValueError, TypeError):
            return float('nan')

    def process_matches(self, match_data: pd.DataFrame) -> pd.DataFrame:
        """
        Process all matches in chronological order and return metrics history.

        Args:
            match_data: DataFrame containing all match data

        Returns:
            DataFrame containing before/after metrics for all teams across all matches
        """
        # Sort matches chronologically
        sorted_matches = self._sort_matches(match_data)

        all_results = []

        for _, match_row in sorted_matches.iterrows():
            try:
                result = self.process_match(match_row)
                all_results.extend(result['teams'])
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


def test_simple_delta_updater():
    """Test the simplified delta updater with sample data."""
    print("Simple Delta Updater Test")
    print("=" * 50)

    # Create sample match data
    sample_data = pd.DataFrame([
        {
            'key': '2026_m1',
            'event_key': '2026test',
            'match_number': 1,
            'alliances.red.team_keys': ['frc254', 'frc1678', 'frc971'],
            'alliances.blue.team_keys': ['frc1114', 'frc2056', 'frc1323'],
            'alliances.red.score': 120,
            'alliances.blue.score': 100,
            'actual_time': '2026-01-01 10:00:00'
        },
        {
            'key': '2026_m2',
            'event_key': '2026test',
            'match_number': 2,
            'alliances.red.team_keys': ['frc254', 'frc1114', 'frc1323'],
            'alliances.blue.team_keys': ['frc1678', 'frc2056', 'frc971'],
            'alliances.red.score': 110,
            'alliances.blue.score': 105,
            'actual_time': '2026-01-01 11:00:00'
        }
    ])

    # Initialize and test updater
    updater = SimpleDeltaUpdater()
    updater.initialize(sample_data)

    # Process matches
    results_df = updater.process_matches(sample_data)
    print(f"\nProcessed {len(results_df)} team-match records")
    print("\nSample results:")
    print(results_df.head(10))

    # Save metrics
    updater.save_metrics_to_csv('team_metrics_simple.csv')

    print("\nSimple Delta Updater test completed successfully!")


if __name__ == '__main__':
    test_simple_delta_updater()