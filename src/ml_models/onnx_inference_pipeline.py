#!/usr/bin/env python3
"""
ONNX Inference Pipeline for Match Winner Prediction

This module implements the complete ONNX-based inference pipeline for predicting
match outcomes using a stacked ensemble of DNN and Random Forest models.

Key Components:
- ONNX model conversion from PyTorch
- Input data packaging for 293-dimensional feature vectors
- Runtime normalization using training statistics
- Ensemble probability blending
- ONNX Runtime inference
"""

import numpy as np
import onnx
import onnxruntime as ort
import torch
import torch.nn as nn
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


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


class MatchWinnerNet(nn.Module):
    """
    PyTorch implementation of the DNN architecture for ONNX conversion.

    Architecture:
    - Input: 293 features
    - Hidden Layer 1: 128 nodes (ReLU + Dropout 0.25)
    - Hidden Layer 2: 64 nodes (ReLU + Dropout 0.15)
    - Output: 1 node (logit)
    """

    def __init__(self, input_dim: int = 293):
        super(MatchWinnerNet, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.net(x)


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
        self.ort_session = ort.InferenceSession(
            self.onnx_model_path,
            options,
            providers=['CPUExecutionProvider']
        )

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


def convert_pytorch_to_onnx(pytorch_model_path: str,
                           onnx_output_path: str,
                           feature_mean: List[float],
                           feature_std: List[float]) -> None:
    """
    Convert PyTorch model to ONNX format.

    Args:
        pytorch_model_path: Path to PyTorch model file
        onnx_output_path: Output path for ONNX model
        feature_mean: Training mean for normalization
        feature_std: Training std for normalization
    """
    # Load PyTorch model
    model_dict = torch.load(pytorch_model_path, map_location='cpu')

    # Extract state dict from neural network
    nn_state = model_dict['neural_network_all_features']
    state_dict = nn_state['model_state_dict']

    # Create model instance
    model = MatchWinnerNet(input_dim=293)

    # Load state dict directly (keys already have 'net.' prefix)
    model.load_state_dict(state_dict)
    model.eval()

    # Create dummy input
    dummy_input = torch.randn(1, 293, dtype=torch.float32)

    # Export to ONNX
    torch.onnx.export(
        model,
        dummy_input,
        onnx_output_path,
        export_params=True,
        opset_version=13,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )

    print(f"Model converted to ONNX and saved to {onnx_output_path}")

    # Validate the ONNX model
    onnx_model = onnx.load(onnx_output_path)
    onnx.checker.check_model(onnx_model)
    print("ONNX model validation passed.")


def save_normalization_params(feature_mean: List[float],
                             feature_std: List[float],
                             output_path: str) -> None:
    """
    Save normalization parameters to JSON file.

    Args:
        feature_mean: Training mean values
        feature_std: Training std values
        output_path: Output JSON file path
    """
    params = {
        'feature_mean': feature_mean,
        'feature_std': feature_std,
        'num_features': len(feature_mean)
    }

    with open(output_path, 'w') as f:
        json.dump(params, f, indent=2)

    print(f"Normalization parameters saved to {output_path}")


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


def main():
    """Main function to demonstrate the pipeline."""
    # Example usage
    print("ONNX Inference Pipeline Setup")
    print("=" * 50)

    # Load the PyTorch model
    pytorch_model_path = 'match_winner_all_features_2026.pt'
    model_dict = torch.load(pytorch_model_path, map_location='cpu')

    # Extract normalization parameters
    feature_mean = model_dict['feature_mean']
    feature_std = model_dict['feature_std']

    # Define output paths
    onnx_model_path = 'match_winner_dnn_2026.onnx'
    norm_params_path = 'normalization_params.json'

    # Convert to ONNX
    print("\nConverting PyTorch model to ONNX...")
    convert_pytorch_to_onnx(
        pytorch_model_path,
        onnx_model_path,
        feature_mean,
        feature_std
    )

    # Save normalization parameters
    print("\nSaving normalization parameters...")
    save_normalization_params(feature_mean, feature_std, norm_params_path)

    # Initialize inference pipeline
    print("\nInitializing inference pipeline...")
    pipeline = ONNXInferencePipeline(
        onnx_model_path=onnx_model_path,
        feature_mean=feature_mean,
        feature_std=feature_std
    )

    # Example prediction
    print("\nRunning example prediction...")

    # Create dummy features (in a real scenario, these would come from your data)
    red_mean = [45.0] * 72
    red_std = [1.0] * 73
    blue_mean = [44.0] * 72
    blue_std = [1.1] * 73

    result = pipeline.predict_from_components(
        red_mean_features=red_mean,
        red_std_features=red_std,
        blue_mean_features=blue_mean,
        blue_std_features=blue_std,
        is_qm=True
    )

    print("\nPrediction Results:")
    print(f"  DNN Logit: {result['dnn_logit']:.4f}")
    print(f"  DNN Probability (Red Win): {result['dnn_prob']:.4f}")
    print(f"  Ensemble Probability (Red Win): {result['ensemble_prob']:.4f}")
    print(f"  Blue Win Probability: {result['blue_win_prob']:.4f}")

    print("\nPipeline setup complete!")


if __name__ == '__main__':
    main()
