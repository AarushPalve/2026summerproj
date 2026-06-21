#!/usr/bin/env python3
"""
Test Script for ONNX Inference Pipeline

Comprehensive test suite for the ONNX inference pipeline components.
"""

import numpy as np
import torch
import json
import os
import sys
import io

# Set UTF-8 encoding for stdout/stderr to handle Unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from onnx_inference_pipeline import (
    ONNXInferencePipeline,
    convert_pytorch_to_onnx,
    save_normalization_params,
    load_normalization_params
)
from input_packaging_utils import InputPackager
from runtime_normalization import RuntimeNormalizer
from ensemble_blending import EnsembleBlender


def test_pytorch_to_onnx_conversion():
    """Test PyTorch to ONNX conversion."""
    print("\n" + "="*60)
    print("Testing PyTorch to ONNX Conversion")
    print("="*60)

    # Load PyTorch model
    pytorch_model_path = 'match_winner_all_features_2026.pt'
    model_dict = torch.load(pytorch_model_path, map_location='cpu')

    # Extract parameters
    feature_mean = model_dict['feature_mean']
    feature_std = model_dict['feature_std']

    # Define output paths
    onnx_model_path = 'test_match_winner_dnn_2026.onnx'

    # Convert to ONNX
    print("Converting model to ONNX...")
    convert_pytorch_to_onnx(
        pytorch_model_path,
        onnx_model_path,
        feature_mean,
        feature_std
    )

    # Verify file exists
    assert os.path.exists(onnx_model_path), "ONNX model file not created"
    print(f"ONNX model created at {onnx_model_path}")

    # Load and verify ONNX model
    import onnx
    onnx_model = onnx.load(onnx_model_path)
    onnx.checker.check_model(onnx_model)
    print("ONNX model validation passed")

    return onnx_model_path, feature_mean, feature_std


def test_input_packaging():
    """Test input data packaging."""
    print("\n" + "="*60)
    print("Testing Input Data Packaging")
    print("="*60)

    packager = InputPackager()

    # Create test features
    red_mean = [45.0 + i * 0.1 for i in range(72)]
    red_std = [1.0 + i * 0.01 for i in range(73)]
    blue_mean = [44.0 + i * 0.1 for i in range(72)]
    blue_std = [1.1 + i * 0.01 for i in range(73)]

    # Package features
    features = packager.package_features(
        red_mean, red_std, blue_mean, blue_std,
        is_qm=True, is_sf=False, is_f=False
    )

    print(f" Created feature vector with shape: {features.shape}")
    assert features.shape == (293,), f"Expected shape (293,), got {features.shape}"

    # Unpack and verify
    unpacked = packager.unpack_features(features)
    assert len(unpacked['red_mean']) == 72, "Red mean features incorrect"
    assert len(unpacked['red_std']) == 73, "Red std features incorrect"
    assert len(unpacked['blue_mean']) == 72, "Blue mean features incorrect"
    assert len(unpacked['blue_std']) == 73, "Blue std features incorrect"
    assert unpacked['is_qm'] == True, "Context flag incorrect"
    assert unpacked['is_sf'] == False, "Context flag incorrect"
    assert unpacked['is_f'] == False, "Context flag incorrect"
    print(" Feature packaging and unpacking successful")

    # Test dummy features
    dummy = packager.create_dummy_features()
    assert dummy.shape == (293,), "Dummy features shape incorrect"
    print(" Dummy feature generation successful")


def test_runtime_normalization():
    """Test runtime normalization."""
    print("\n" + "="*60)
    print("Testing Runtime Normalization")
    print("="*60)

    # Create test normalization parameters
    mean = [i * 0.1 for i in range(293)]
    std = [1.0 + i * 0.01 for i in range(293)]

    # Create normalizer
    normalizer = RuntimeNormalizer(mean, std)
    print(" RuntimeNormalizer initialized")

    # Create test features
    features = np.random.randn(293).astype(np.float32) * 10

    # Normalize
    normalized = normalizer.normalize(features)
    print(f" Normalized features: mean={np.mean(normalized):.4f}, std={np.std(normalized):.4f}")

    # Test batch normalization
    batch = np.stack([features, features * 2, features * 0.5], axis=0)
    normalized_batch = normalizer.normalize_batch(batch)
    assert normalized_batch.shape == (3, 293), "Batch normalization shape incorrect"
    print(f" Batch normalization successful: {normalized_batch.shape}")

    # Test denormalization
    denormalized = normalizer.denormalize(normalized)
    # Check that denormalization is approximately the inverse
    diff = np.abs(features - denormalized)
    assert np.mean(diff) < 1.0, "Denormalization error too large"
    print(f" Denormalization successful (mean error: {np.mean(diff):.4f})")


def test_ensemble_blending():
    """Test ensemble probability blending."""
    print("\n" + "="*60)
    print("Testing Ensemble Probability Blending")
    print("="*60)

    blender = EnsembleBlender(use_rf=True)

    # Test with both models
    result = blender.blend_probabilities(dnn_logit=1.5, rf_prob=0.8)
    assert 'dnn_logit' in result, "Missing dnn_logit in result"
    assert 'dnn_prob' in result, "Missing dnn_prob in result"
    assert 'rf_prob' in result, "Missing rf_prob in result"
    assert 'ensemble_prob' in result, "Missing ensemble_prob in result"
    assert 'blue_win_prob' in result, "Missing blue_win_prob in result"
    print(f" Blending with both models: ensemble_prob={result['ensemble_prob']:.4f}")

    # Test with DNN only
    blender_no_rf = EnsembleBlender(use_rf=False)
    result_no_rf = blender_no_rf.blend_probabilities(dnn_logit=1.5)
    assert result_no_rf['ensemble_prob'] == result_no_rf['dnn_prob'], "DNN-only blending incorrect"
    print(f" DNN-only blending: ensemble_prob={result_no_rf['ensemble_prob']:.4f}")

    # Test batch blending
    dnn_logits = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
    rf_probs = np.array([0.1, 0.2, 0.5, 0.8, 0.9])
    batch_result = blender.blend_batch(dnn_logits, rf_probs)
    assert batch_result['ensemble_probs'].shape == (5,), "Batch blending shape incorrect"
    print(f" Batch blending successful: {batch_result['ensemble_probs'].shape}")


def test_full_pipeline(onnx_model_path: str, feature_mean: list, feature_std: list):
    """Test the complete inference pipeline."""
    print("\n" + "="*60)
    print("Testing Complete Inference Pipeline")
    print("="*60)

    # Initialize pipeline
    pipeline = ONNXInferencePipeline(
        onnx_model_path=onnx_model_path,
        feature_mean=feature_mean,
        feature_std=feature_std
    )
    print(" ONNXInferencePipeline initialized")

    # Create test features using packager
    packager = InputPackager()
    red_mean = [45.0] * 72
    red_std = [1.0] * 73
    blue_mean = [44.0] * 72
    blue_std = [1.1] * 73

    # Test predict_from_components
    result = pipeline.predict_from_components(
        red_mean, red_std, blue_mean, blue_std,
        is_qm=True
    )

    print(f"\nPrediction Results:")
    print(f"  DNN Logit: {result['dnn_logit']:.4f}")
    print(f"  DNN Probability: {result['dnn_prob']:.4f}")
    print(f"  RF Probability: {result['rf_prob'] if result['rf_prob'] is not None else 'N/A'}")
    print(f"  Ensemble Probability: {result['ensemble_prob']:.4f}")
    print(f"  Blue Win Probability: {result['blue_win_prob']:.4f}")

    # Verify probabilities are in valid range
    assert 0.0 <= result['ensemble_prob'] <= 1.0, "Ensemble probability out of range"
    assert 0.0 <= result['blue_win_prob'] <= 1.0, "Blue win probability out of range"
    print(" All probabilities in valid range [0, 1]")

    # Test direct prediction with packaged features
    features = packager.package_features(red_mean, red_std, blue_mean, blue_std, is_qm=True)
    direct_result = pipeline.predict_ensemble(features)

    # Results should be the same
    assert abs(result['ensemble_prob'] - direct_result['ensemble_prob']) < 1e-6, \
        "Results differ between methods"
    print(" Consistent results between prediction methods")


def test_normalization_params_io():
    """Test saving and loading normalization parameters."""
    print("\n" + "="*60)
    print("Testing Normalization Parameters I/O")
    print("="*60)

    # Create test parameters
    mean = [i * 0.1 for i in range(293)]
    std = [1.0 + i * 0.01 for i in range(293)]

    # Save to JSON
    json_path = 'test_norm_params.json'
    save_normalization_params(mean, std, json_path)
    assert os.path.exists(json_path), "JSON file not created"
    print(f" Parameters saved to {json_path}")

    # Load from JSON
    loaded_mean, loaded_std = load_normalization_params(json_path)
    assert len(loaded_mean) == 293, "Loaded mean has wrong length"
    assert len(loaded_std) == 293, "Loaded std has wrong length"
    assert np.allclose(loaded_mean, mean), "Loaded mean values incorrect"
    assert np.allclose(loaded_std, std), "Loaded std values incorrect"
    print(" Parameters loaded successfully")

    # Test RuntimeNormalizer from JSON
    normalizer = RuntimeNormalizer.from_json(json_path)
    assert normalizer.feature_mean.shape == (293,), "Normalizer mean shape incorrect"
    assert normalizer.feature_std.shape == (293,), "Normalizer std shape incorrect"
    print(" RuntimeNormalizer created from JSON")

    # Cleanup
    os.remove(json_path)


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "="*60)
    print("ONNX Inference Pipeline - Comprehensive Test Suite")
    print("="*60)

    try:
        # Test 1: PyTorch to ONNX conversion
        onnx_path, mean, std = test_pytorch_to_onnx_conversion()

        # Test 2: Input packaging
        test_input_packaging()

        # Test 3: Runtime normalization
        test_runtime_normalization()

        # Test 4: Ensemble blending
        test_ensemble_blending()

        # Test 5: Normalization params I/O
        test_normalization_params_io()

        # Test 6: Full pipeline
        test_full_pipeline(onnx_path, mean, std)

        print("\n" + "="*60)
        print("ALL TESTS PASSED SUCCESSFULLY")
        print("="*60)

        # Cleanup test ONNX file
        if os.path.exists(onnx_path):
            os.remove(onnx_path)

        return True

    except Exception as e:
        print(f"\nTEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
