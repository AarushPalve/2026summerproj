#!/usr/bin/env python3
"""
Consolidated ML Utilities

This module replaces the separate input_packaging_utils.py and runtime_normalization.py
with a single, simplified utility module that uses standard library functions where possible.
"""

import numpy as np
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from scipy.special import expit  # Use stdlib sigmoid function


# Feature vector structure constants (293-dimensional)
RED_MEAN_START = 0
RED_MEAN_END = 72  # 0-71 (72 features)
RED_STD_START = 72
RED_STD_END = 145  # 72-144 (73 features)

BLUE_MEAN_START = 145
BLUE_MEAN_END = 217  # 145-216 (72 features)
BLUE_STD_START = 217
BLUE_STD_END = 290  # 217-289 (73 features)

CONTEXT_QM = 290
CONTEXT_SF = 291
CONTEXT_F = 292


class MLUtils:
    """
    Consolidated ML utilities for the FRC Dashboard.

    This class provides:
    - Input feature packaging for 293-dimensional vectors
    - Runtime normalization using training statistics
    - Standardized sigmoid function using scipy.special.expit
    """

    def __init__(self, feature_mean: Optional[List[float]] = None,
                 feature_std: Optional[List[float]] = None):
        """
        Initialize ML utilities.

        Args:
            feature_mean: Training mean values for normalization (293 elements)
            feature_std: Training std values for normalization (293 elements)
        """
        self.feature_mean = None
        self.feature_std = None

        if feature_mean is not None and feature_std is not None:
            self.set_normalization_params(feature_mean, feature_std)

    def set_normalization_params(self, feature_mean: List[float], feature_std: List[float]):
        """Set normalization parameters."""
        if len(feature_mean) != 293:
            raise ValueError(f"Expected 293 mean values, got {len(feature_mean)}")
        if len(feature_std) != 293:
            raise ValueError(f"Expected 293 std values, got {len(feature_std)}")

        self.feature_mean = np.array(feature_mean, dtype=np.float32)
        self.feature_std = np.array(feature_std, dtype=np.float32)

    def sigmoid(self, x: float) -> float:
        """
        Sigmoid function using scipy.special.expit (stdlib).

        Args:
            x: Input value

        Returns:
            Sigmoid output in range [0, 1]
        """
        return float(expit(x))

    def sigmoid_batch(self, logits: np.ndarray) -> np.ndarray:
        """
        Apply sigmoid to a batch of logits using scipy.special.expit.

        Args:
            logits: Array of logit values

        Returns:
            Array of probabilities
        """
        return expit(logits).astype(np.float32)

    def package_features(self,
                        red_mean_features: List[float],
                        red_std_features: List[float],
                        blue_mean_features: List[float],
                        blue_std_features: List[float],
                        is_qm: bool = True,
                        is_sf: bool = False,
                        is_f: bool = False) -> np.ndarray:
        """
        Package input features into the 293-dimensional vector.

        Args:
            red_mean_features: 72 mean features for red alliance
            red_std_features: 73 std features for red alliance
            blue_mean_features: 72 mean features for blue alliance
            blue_std_features: 73 std features for blue alliance
            is_qm: Qualification match flag
            is_sf: Semifinal match flag
            is_f: Final match flag

        Returns:
            293-dimensional numpy array
        """
        # Validate input sizes
        if len(red_mean_features) != 72:
            raise ValueError(f"Expected 72 red mean features, got {len(red_mean_features)}")
        if len(red_std_features) != 73:
            raise ValueError(f"Expected 73 red std features, got {len(red_std_features)}")
        if len(blue_mean_features) != 72:
            raise ValueError(f"Expected 72 blue mean features, got {len(blue_mean_features)}")
        if len(blue_std_features) != 73:
            raise ValueError(f"Expected 73 blue std features, got {len(blue_std_features)}")

        # Create feature vector
        feature_vector = np.zeros(293, dtype=np.float32)

        # Red alliance features
        feature_vector[RED_MEAN_START:RED_MEAN_END] = red_mean_features
        feature_vector[RED_STD_START:RED_STD_END] = red_std_features

        # Blue alliance features
        feature_vector[BLUE_MEAN_START:BLUE_MEAN_END] = blue_mean_features
        feature_vector[BLUE_STD_START:BLUE_STD_END] = blue_std_features

        # Context features (one-hot encoded)
        feature_vector[CONTEXT_QM] = 1.0 if is_qm else 0.0
        feature_vector[CONTEXT_SF] = 1.0 if is_sf else 0.0
        feature_vector[CONTEXT_F] = 1.0 if is_f else 0.0

        return feature_vector

    def unpack_features(self, feature_vector: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Unpack a 293-dimensional feature vector into its components.

        Args:
            feature_vector: 293-dimensional numpy array

        Returns:
            Dictionary with keys:
            - 'red_mean': 72 mean features for red
            - 'red_std': 73 std features for red
            - 'blue_mean': 72 mean features for blue
            - 'blue_std': 73 std features for blue
            - 'is_qm': Qualification match flag
            - 'is_sf': Semifinal match flag
            - 'is_f': Final match flag
        """
        if feature_vector.shape != (293,):
            raise ValueError(f"Expected 293 features, got {feature_vector.shape}")

        return {
            'red_mean': feature_vector[RED_MEAN_START:RED_MEAN_END],
            'red_std': feature_vector[RED_STD_START:RED_STD_END],
            'blue_mean': feature_vector[BLUE_MEAN_START:BLUE_MEAN_END],
            'blue_std': feature_vector[BLUE_STD_START:BLUE_STD_END],
            'is_qm': bool(feature_vector[CONTEXT_QM]),
            'is_sf': bool(feature_vector[CONTEXT_SF]),
            'is_f': bool(feature_vector[CONTEXT_F])
        }

    def normalize_features(self, features: np.ndarray) -> np.ndarray:
        """
        Apply runtime normalization: (X_raw - μ_train) / (σ_train + 1e-6)

        Args:
            features: Raw input features (293-dimensional)

        Returns:
            Normalized features
        """
        if features.shape != (293,):
            raise ValueError(f"Expected 293 features, got {features.shape}")

        if self.feature_mean is None or self.feature_std is None:
            raise RuntimeError("Normalization parameters not set")

        # Apply normalization with epsilon for numerical stability
        normalized = (features - self.feature_mean) / (self.feature_std + 1e-6)
        return normalized.astype(np.float32)

    def normalize_batch(self, features_batch: np.ndarray) -> np.ndarray:
        """
        Apply runtime normalization to a batch of features.

        Args:
            features_batch: Batch of raw input features (N x 293)

        Returns:
            Normalized features batch (N x 293)
        """
        if features_batch.shape[1] != 293:
            raise ValueError(f"Expected 293 features per sample, got {features_batch.shape[1]}")

        if self.feature_mean is None or self.feature_std is None:
            raise RuntimeError("Normalization parameters not set")

        # Apply normalization with epsilon for numerical stability
        normalized = (features_batch - self.feature_mean) / (self.feature_std + 1e-6)
        return normalized.astype(np.float32)

    def create_dummy_features(self,
                            red_mean_value: float = 0.0,
                            red_std_value: float = 1.0,
                            blue_mean_value: float = 0.0,
                            blue_std_value: float = 1.0,
                            is_qm: bool = True) -> np.ndarray:
        """
        Create dummy features for testing.

        Args:
            red_mean_value: Value to fill red mean features
            red_std_value: Value to fill red std features
            blue_mean_value: Value to fill blue mean features
            blue_std_value: Value to fill blue std features
            is_qm: Qualification match flag

        Returns:
            293-dimensional dummy feature vector
        """
        return self.package_features(
            red_mean_features=[red_mean_value] * 72,
            red_std_features=[red_std_value] * 73,
            blue_mean_features=[blue_mean_value] * 72,
            blue_std_features=[blue_std_value] * 73,
            is_qm=is_qm,
            is_sf=False,
            is_f=False
        )

    def get_feature_names(self) -> List[str]:
        """
        Get list of feature names based on the specification.

        Returns:
            List of 293 feature names
        """
        feature_names = []

        # Red mean features
        for i in range(72):
            feature_names.append(f'red_mean_{i:03d}')

        # Red std features
        for i in range(73):
            feature_names.append(f'red_std_{i:03d}')

        # Blue mean features
        for i in range(72):
            feature_names.append(f'blue_mean_{i:03d}')

        # Blue std features
        for i in range(73):
            feature_names.append(f'blue_std_{i:03d}')

        # Context features
        feature_names.append('comp_level_qm')
        feature_names.append('comp_level_sf')
        feature_names.append('comp_level_f')

        return feature_names

    def validate_feature_vector(self, feature_vector: np.ndarray) -> bool:
        """
        Validate that a feature vector has the correct shape and structure.

        Args:
            feature_vector: Input feature vector

        Returns:
            True if valid, False otherwise
        """
        if feature_vector.shape != (293,):
            return False

        if not isinstance(feature_vector, np.ndarray):
            return False

        if feature_vector.dtype not in [np.float32, np.float64]:
            return False

        return True

    def save_normalization_params(self, json_path: str) -> None:
        """
        Save normalization parameters to JSON file.

        Args:
            json_path: Output JSON file path
        """
        if self.feature_mean is None or self.feature_std is None:
            raise RuntimeError("Normalization parameters not set")

        params = {
            'feature_mean': self.feature_mean.tolist(),
            'feature_std': self.feature_std.tolist(),
            'num_features': 293
        }

        with open(json_path, 'w') as f:
            json.dump(params, f, indent=2)

    @classmethod
    def load_normalization_params(cls, json_path: str) -> 'MLUtils':
        """
        Load normalization parameters from JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            MLUtils instance with loaded parameters
        """
        with open(json_path, 'r') as f:
            params = json.load(f)

        return cls(
            feature_mean=params['feature_mean'],
            feature_std=params['feature_std']
        )


def print_feature_structure():
    """Print the feature vector structure for reference."""
    print("293-Dimensional Feature Vector Structure:")
    print("=" * 60)
    print("Red Alliance Statistics (Dimensions 0-144):")
    print("  - Mean features: 72 (indices 0-71)")
    print("  - Std features: 73 (indices 72-144)")
    print()
    print("Blue Alliance Statistics (Dimensions 145-289):")
    print("  - Mean features: 72 (indices 145-216)")
    print("  - Std features: 73 (indices 217-289)")
    print()
    print("Context Features (Dimensions 290-292):")
    print("  - Index 290: Qualification match flag (comp_level_qm)")
    print("  - Index 291: Semifinal match flag (comp_level_sf)")
    print("  - Index 292: Final match flag (comp_level_f)")
    print("=" * 60)


def test_ml_utils():
    """Test the ML utilities with various scenarios."""
    print("ML Utilities Test")
    print("=" * 60)

    # Create ML utils instance
    utils = MLUtils()

    # Test feature packaging
    print("\nFeature Packaging Test:")
    features = utils.package_features(
        red_mean_features=[45.0] * 72,
        red_std_features=[1.0] * 73,
        blue_mean_features=[44.0] * 72,
        blue_std_features=[1.1] * 73,
        is_qm=True
    )
    print(f"  Created feature vector with shape: {features.shape}")

    # Test sigmoid function
    print("\nSigmoid Function Test:")
    print(f"  sigmoid(0.0) = {utils.sigmoid(0.0):.4f}")
    print(f"  sigmoid(1.0) = {utils.sigmoid(1.0):.4f}")
    print(f"  sigmoid(-1.0) = {utils.sigmoid(-1.0):.4f}")

    # Test feature unpacking
    print("\nFeature Unpacking Test:")
    unpacked = utils.unpack_features(features)
    print(f"  Red mean features: {len(unpacked['red_mean'])} features")
    print(f"  Blue std features: {len(unpacked['blue_std'])} features")
    print(f"  Is qualification match: {unpacked['is_qm']}")

    print("\nML Utilities test completed successfully!")


if __name__ == '__main__':
    test_ml_utils()