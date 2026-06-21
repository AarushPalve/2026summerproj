#!/usr/bin/env python3
"""
Demo Script for ONNX Inference Pipeline

This script demonstrates the complete ONNX inference pipeline for match winner prediction.
"""

import sys
import io
import numpy as np
import torch

# Set UTF-8 encoding for stdout/stderr to handle Unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from onnx_inference_pipeline import (
    ONNXInferencePipeline,
    convert_pytorch_to_onnx,
    save_normalization_params
)
from input_packaging_utils import InputPackager


def main():
    print("=" * 70)
    print("ONNX Inference Pipeline Demo")
    print("=" * 70)

    # Step 1: Load PyTorch model and extract parameters
    print("\n[1/5] Loading PyTorch model...")
    pytorch_model_path = 'match_winner_all_features_2026.pt'
    model_dict = torch.load(pytorch_model_path, map_location='cpu')

    feature_mean = model_dict['feature_mean']
    feature_std = model_dict['feature_std']
    print(f"  Loaded model with {len(feature_mean)} features")
    print(f"  Feature mean range: [{min(feature_mean):.2f}, {max(feature_mean):.2f}]")
    print(f"  Feature std range: [{min(feature_std):.2f}, {max(feature_std):.2f}]")

    # Step 2: Convert to ONNX
    print("\n[2/5] Converting PyTorch model to ONNX...")
    onnx_model_path = 'match_winner_dnn_2026.onnx'
    convert_pytorch_to_onnx(
        pytorch_model_path,
        onnx_model_path,
        feature_mean,
        feature_std
    )
    print(f"  ONNX model saved to: {onnx_model_path}")

    # Step 3: Save normalization parameters
    print("\n[3/5] Saving normalization parameters...")
    norm_params_path = 'normalization_params.json'
    save_normalization_params(feature_mean, feature_std, norm_params_path)
    print(f"  Parameters saved to: {norm_params_path}")

    # Step 4: Initialize inference pipeline
    print("\n[4/5] Initializing inference pipeline...")
    pipeline = ONNXInferencePipeline(
        onnx_model_path=onnx_model_path,
        feature_mean=feature_mean,
        feature_std=feature_std
    )
    print("  Pipeline ready for inference!")

    # Step 5: Run example predictions
    print("\n[5/5] Running example predictions...")

    packager = InputPackager()

    # Scenario 1: Close match (similar team strengths)
    print("\n  Scenario 1: Close match (similar team strengths)")
    result1 = pipeline.predict_from_components(
        red_mean_features=[45.0] * 72,
        red_std_features=[1.0] * 73,
        blue_mean_features=[44.8] * 72,
        blue_std_features=[1.0] * 73,
        is_qm=True
    )
    print(f"    Red Win Probability: {result1['ensemble_prob']:.2%}")
    print(f"    Blue Win Probability: {result1['blue_win_prob']:.2%}")

    # Scenario 2: Strong red alliance
    print("\n  Scenario 2: Strong red alliance")
    result2 = pipeline.predict_from_components(
        red_mean_features=[50.0] * 72,
        red_std_features=[0.8] * 73,
        blue_mean_features=[40.0] * 72,
        blue_std_features=[1.2] * 73,
        is_qm=True
    )
    print(f"    Red Win Probability: {result2['ensemble_prob']:.2%}")
    print(f"    Blue Win Probability: {result2['blue_win_prob']:.2%}")

    # Scenario 3: Playoff final match
    print("\n  Scenario 3: Playoff final match (high stakes)")
    result3 = pipeline.predict_from_components(
        red_mean_features=[48.0] * 72,
        red_std_features=[0.9] * 73,
        blue_mean_features=[46.0] * 72,
        blue_std_features=[1.0] * 73,
        is_qm=False,
        is_f=True
    )
    print(f"    Red Win Probability: {result3['ensemble_prob']:.2%}")
    print(f"    Blue Win Probability: {result3['blue_win_prob']:.2%}")

    # Display detailed results for first scenario
    print("\n" + "=" * 70)
    print("Detailed Results for Scenario 1:")
    print("=" * 70)
    print(f"  DNN Logit: {result1['dnn_logit']:.4f}")
    print(f"  DNN Probability: {result1['dnn_prob']:.4f}")
    print(f"  RF Probability: {result1['rf_prob'] if result1['rf_prob'] is not None else 'N/A'}")
    print(f"  Ensemble Probability: {result1['ensemble_prob']:.4f}")
    print(f"  Blue Win Probability: {result1['blue_win_prob']:.4f}")

    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ PyTorch to ONNX conversion")
    print("  ✓ Runtime normalization")
    print("  ✓ Input data packaging (293-dimensional vector)")
    print("  ✓ ONNX Runtime inference")
    print("  ✓ Ensemble probability blending")
    print("  ✓ Memory-efficient model loading")


if __name__ == '__main__':
    main()
