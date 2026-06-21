#!/usr/bin/env python3
"""
ML Inference Pipeline

This module implements the ONNX-based inference pipeline for predicting
match outcomes using a stacked ensemble of DNN and Random Forest models.
"""

import numpy as np
import onnxruntime as ort
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FeatureRanges:
    """Feature index ranges for the 293-dimensional input vector."""
    RED_MEAN_START: int = 0
    RED_MEAN_END: int = 72  # 0-71 (72 features)
    RED_STD_START: int = 72
    RED_STD_END: int = 145  # 72-144 (73 features)

    BLUE_MEAN_START: int = 145
    BLUE_MEAN_END: int = 217  # 145-216 (72 features)
    BLUE_STD_START: int = 217
    BLUE_STD_END: int = 290  # 217-289 (73 features)

    CONTEXT_QM: int = 290
    CONTEXT_SF: int = 291
    CONTEXT_F: int = 292


class ONNXInferencePipeline:
    """
    Complete ONNX inference pipeline with normalization and ensemble blending.

    Features:
    - Loads and caches ONNX models in memory
    - Runtime normalization using training statistics
    - Ensemble blending of DNN and Random Forest predictions
    - Thread-safe inference
    """

    def __init__(self, onnx_model_path: str,
                 feature_mean: List[float],
                 feature_std: List[float],
                 rf_model_path: Optional[str] = None):
        """
        Initialize the inference pipeline.

        Args:
            onnx_model_path: Path to the ONNX model file
            feature_mean: Training mean for normalization (293 elements)
            feature_std: Training std for normalization (293 elements)
            rf_model_path: Optional path to Random Forest model for ensemble
        """
        self.onnx_model_path = onnx_model_path
        self.feature_mean = np.array(feature_mean, dtype=np.float32)
        self.feature_std = np.array(feature_std, dtype=np.float32)
        self.rf_model_path = rf_model_path

        # Initialize ONNX runtime session
        self.ort_session = None
        self.rf_model = None

        # Load models into memory
        self._load_models()

    def _load_models(self):
        """Load models into memory (called once at initialization)."""
        # Set ONNX Runtime options for performance
        options = ort.SessionOptions()
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        # Load ONNX model
        try:
            self.ort_session = ort.InferenceSession(
                self.onnx_model_path,
                options,
                providers=['CPUExecutionProvider']
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load ONNX model: {e}")

        # Load Random Forest model if available
        if self.rf_model_path and os.path.exists(self.rf_model_path):
            try:
                import joblib
                self.rf_model = joblib.load(self.rf_model_path)
            except Exception as e:
                print(f"Warning: Could not load Random Forest model: {e}")
                self.rf_model = None

        print("Models loaded successfully into memory.")

    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """
        Apply runtime normalization: (X_raw - μ_train) / (σ_train + 1e-6)

        Args:
            features: Raw input features (293-dimensional)

        Returns:
            Normalized features
        """
        if features.shape != (293,):
            raise ValueError(f"Expected 293 features, got {features.shape}")

        # Apply normalization with epsilon for numerical stability
        normalized = (features - self.feature_mean) / (self.feature_std + 1e-6)
        return normalized.astype(np.float32)

    def _package_input(self, red_mean_features: List[float],
                      red_std_features: List[float],
                      blue_mean_features: List[float],
                      blue_std_features: List[float],
                      is_qm: bool = True,
                      is_sf: bool = False,
                      is_f: bool = False) -> np.ndarray:
        """
        Package input features into the 293-dimensional vector.

        Args:
            red_mean_features: 72 mean features for red alliance (indices 0-71)
            red_std_features: 73 std features for red alliance (indices 72-144)
            blue_mean_features: 72 mean features for blue alliance (indices 145-216)
            blue_std_features: 73 std features for blue alliance (indices 217-289)
            is_qm: Qualification match flag (context index 290)
            is_sf: Semifinal match flag (context index 291)
            is_f: Final match flag (context index 292)

        Returns:
            Packaged 293-dimensional feature vector
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
        feature_vector[FeatureRanges.RED_MEAN_START:FeatureRanges.RED_MEAN_END] = red_mean_features
        feature_vector[FeatureRanges.RED_STD_START:FeatureRanges.RED_STD_END] = red_std_features

        # Blue alliance features
        feature_vector[FeatureRanges.BLUE_MEAN_START:FeatureRanges.BLUE_MEAN_END] = blue_mean_features
        feature_vector[FeatureRanges.BLUE_STD_START:FeatureRanges.BLUE_STD_END] = blue_std_features

        # Context features (one-hot encoded)
        feature_vector[FeatureRanges.CONTEXT_QM] = 1.0 if is_qm else 0.0
        feature_vector[FeatureRanges.CONTEXT_SF] = 1.0 if is_sf else 0.0
        feature_vector[FeatureRanges.CONTEXT_F] = 1.0 if is_f else 0.0

        return feature_vector

    def predict_dnn(self, features: np.ndarray) -> Tuple[float, float]:
        """
        Run DNN prediction and return logit and probability.

        Args:
            features: Raw 293-dimensional feature vector

        Returns:
            Tuple of (logit, red_win_probability)
        """
        # Normalize features
        normalized = self._normalize_features(features)

        # Add batch dimension for ONNX Runtime
        input_tensor = normalized.reshape(1, -1)

        # Run inference
        inputs = {self.ort_session.get_inputs()[0].name: input_tensor}
        outputs = self.ort_session.run(None, inputs)

        # Get logit output
        logit = outputs[0][0][0]

        # Convert logit to probability using sigmoid
        red_win_prob = 1.0 / (1.0 + np.exp(-logit))

        return logit, float(red_win_prob)

    def predict_rf(self, features: np.ndarray) -> float:
        """
        Run Random Forest prediction.

        Args:
            features: Raw 293-dimensional feature vector

        Returns:
            Red win probability from Random Forest
        """
        if self.rf_model is None:
            raise RuntimeError("Random Forest model not loaded")

        # Normalize features
        normalized = self._normalize_features(features)

        # Reshape for sklearn
        input_features = normalized.reshape(1, -1)

        # Predict probability
        # Note: sklearn returns [prob_blue_win, prob_red_win] for binary classification
        probas = self.rf_model.predict_proba(input_features)[0]

        # Assuming class 1 is red win (need to verify this)
        red_win_prob = float(probas[1])

        return red_win_prob

    def predict_ensemble(self, features: np.ndarray) -> Dict[str, float]:
        """
        Run ensemble prediction with probability blending.

        Formula: P(Red_Win) = (σ(Logit_DNN) + P_RF(Red_Win)) / 2

        Args:
            features: Raw 293-dimensional feature vector

        Returns:
            Dictionary containing:
            - dnn_logit: Raw DNN logit
            - dnn_prob: DNN red win probability
            - rf_prob: Random Forest red win probability (if available)
            - ensemble_prob: Blended ensemble probability
            - blue_win_prob: 1 - ensemble_prob
        """
        # Get DNN prediction
        dnn_logit, dnn_prob = self.predict_dnn(features)

        # Get RF prediction if available
        rf_prob = None
        if self.rf_model is not None:
            rf_prob = self.predict_rf(features)

        # Calculate ensemble probability
        if rf_prob is not None:
            # Blend: (sigmoid(dnn_logit) + rf_prob) / 2
            ensemble_prob = (dnn_prob + rf_prob) / 2.0
        else:
            # Fallback to DNN only
            ensemble_prob = dnn_prob

        return {
            'dnn_logit': float(dnn_logit),
            'dnn_prob': dnn_prob,
            'rf_prob': rf_prob,
            'ensemble_prob': ensemble_prob,
            'blue_win_prob': 1.0 - ensemble_prob
        }

    def predict_from_components(self, red_mean_features: List[float],
                               red_std_features: List[float],
                               blue_mean_features: List[float],
                               blue_std_features: List[float],
                               is_qm: bool = True,
                               is_sf: bool = False,
                               is_f: bool = False) -> Dict[str, float]:
        """
        Convenience method: package input and run ensemble prediction.

        Args:
            red_mean_features: 72 mean features for red alliance
            red_std_features: 73 std features for red alliance
            blue_mean_features: 72 mean features for blue alliance
            blue_std_features: 73 std features for blue alliance
            is_qm: Qualification match flag
            is_sf: Semifinal match flag
            is_f: Final match flag

        Returns:
            Prediction results dictionary
        """
        features = self._package_input(
            red_mean_features, red_std_features,
            blue_mean_features, blue_std_features,
            is_qm, is_sf, is_f
        )
        return self.predict_ensemble(features)


def load_normalization_params(json_path: str) -> Tuple[List[float], List[float]]:
    """
    Load normalization parameters from JSON file.

    Args:
        json_path: Path to JSON file

    Returns:
        Tuple of (feature_mean, feature_std)
    """
    with open(json_path, 'r') as f:
        params = json.load(f)

    return params['feature_mean'], params['feature_std']


# Global instance for the ML pipeline
ml_pipeline = None


def initialize_ml_pipeline(model_dir: str = "data/models") -> ONNXInferencePipeline:
    """
    Initialize the ML inference pipeline.

    Args:
        model_dir: Directory containing ML models

    Returns:
        Initialized ONNXInferencePipeline instance
    """
    global ml_pipeline

    if ml_pipeline is not None:
        return ml_pipeline

    # Define model paths
    onnx_model_path = os.path.join(model_dir, "match_winner_dnn_2026.onnx")
    rf_model_path = os.path.join(model_dir, "match_winner_rf_2026.joblib")
    norm_params_path = os.path.join(model_dir, "normalization_params.json")

    # Check if models exist
    if not os.path.exists(onnx_model_path):
        raise FileNotFoundError(f"ONNX model not found at {onnx_model_path}")

    if not os.path.exists(norm_params_path):
        raise FileNotFoundError(f"Normalization parameters not found at {norm_params_path}")

    # Load normalization parameters
    feature_mean, feature_std = load_normalization_params(norm_params_path)

    # Initialize pipeline
    ml_pipeline = ONNXInferencePipeline(
        onnx_model_path=onnx_model_path,
        feature_mean=feature_mean,
        feature_std=feature_std,
        rf_model_path=rf_model_path if os.path.exists(rf_model_path) else None
    )

    return ml_pipeline


def predict_match_outcome(red_mean_features: List[float],
                        red_std_features: List[float],
                        blue_mean_features: List[float],
                        blue_std_features: List[float],
                        is_qm: bool = True,
                        is_sf: bool = False,
                        is_f: bool = False) -> Dict[str, float]:
    """
    Predict match outcome using the ML pipeline.

    Args:
        red_mean_features: 72 mean features for red alliance
        red_std_features: 73 std features for red alliance
        blue_mean_features: 72 mean features for blue alliance
        blue_std_features: 73 std features for blue alliance
        is_qm: Qualification match flag
        is_sf: Semifinal match flag
        is_f: Final match flag

    Returns:
        Prediction results dictionary
    """
    global ml_pipeline

    if ml_pipeline is None:
        ml_pipeline = initialize_ml_pipeline()

    return ml_pipeline.predict_from_components(
        red_mean_features, red_std_features,
        blue_mean_features, blue_std_features,
        is_qm, is_sf, is_f
    )


if __name__ == "__main__":
    print("ML Inference Pipeline")
    print("=" * 50)

    try:
        # Initialize pipeline
        pipeline = initialize_ml_pipeline()
        print("Pipeline initialized successfully")

        # Example prediction
        red_mean = [45.0] * 72
        red_std = [1.0] * 73
        blue_mean = [44.0] * 72
        blue_std = [1.1] * 73

        result = predict_match_outcome(red_mean, red_std, blue_mean, blue_std)

        print("\nExample Prediction Results:")
        print(f"  DNN Logit: {result['dnn_logit']:.4f}")
        print(f"  DNN Probability (Red Win): {result['dnn_prob']:.4f}")
        if result['rf_prob'] is not None:
            print(f"  RF Probability (Red Win): {result['rf_prob']:.4f}")
        print(f"  Ensemble Probability (Red Win): {result['ensemble_prob']:.4f}")
        print(f"  Blue Win Probability: {result['blue_win_prob']:.4f}")

    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure ML models are available in the data/models directory.")
