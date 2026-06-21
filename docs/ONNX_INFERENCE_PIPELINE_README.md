# ONNX Inference Pipeline

This directory contains the complete ONNX-based inference pipeline for match winner prediction using a stacked ensemble of DNN and Random Forest models.

## Overview

The pipeline implements the architecture specified in `04_ml_inference_pipeline.md` with the following key components:

1. **ONNX Model Conversion**: Converts PyTorch models to ONNX format for cross-platform compatibility
2. **Input Data Packaging**: Packages 293-dimensional feature vectors according to specification
3. **Runtime Normalization**: Applies training statistics to prevent inference skew
4. **Ensemble Blending**: Combines DNN and Random Forest predictions using soft-voting
5. **ONNX Runtime Inference**: Efficient inference using ONNX Runtime

## Architecture

### Feature Vector (293 Dimensions)

```
Red Alliance Statistics (Dimensions 0-144)
├── Mean features: 72 (indices 0-71)
└── Std features: 73 (indices 72-144)

Blue Alliance Statistics (Dimensions 145-289)
├── Mean features: 72 (indices 145-216)
└── Std features: 73 (indices 217-289)

Context Features (Dimensions 290-292)
├── Index 290: Qualification match flag (comp_level_qm)
├── Index 291: Semifinal match flag (comp_level_sf)
└── Index 292: Final match flag (comp_level_f)
```

### DNN Architecture

```
Input: 293 features
├── Linear Layer: 293 → 128
├── ReLU Activation
├── Dropout (p=0.25)
├── Linear Layer: 128 → 64
├── ReLU Activation
├── Dropout (p=0.15)
└── Linear Layer: 64 → 1 (logit output)
```

### Ensemble Blending Formula

```
P(Red_Win) = (σ(Logit_DNN) + P_RF(Red_Win)) / 2
```

Where:
- σ is the sigmoid function
- Logit_DNN is the raw DNN output
- P_RF(Red_Win) is the Random Forest probability

## Files

### Core Implementation

1. **`onnx_inference_pipeline.py`**
   - Main inference pipeline implementation
   - ONNX model conversion from PyTorch
   - Complete inference workflow with normalization and ensemble blending

2. **`input_packaging_utils.py`**
   - Input data packaging utilities
   - Feature vector construction and validation
   - Helper methods for creating test data

3. **`runtime_normalization.py`**
   - Runtime normalization layer
   - Handles feature normalization using training statistics
   - Batch processing support

4. **`ensemble_blending.py`**
   - Ensemble probability blending implementation
   - Combines DNN and Random Forest predictions
   - Uncertainty calculation

### Testing

5. **`test_onnx_pipeline.py`**
   - Comprehensive test suite
   - Validates all pipeline components
   - Ensures correctness of the implementation

## Setup

### Prerequisites

```bash
pip install numpy onnx onnxruntime torch
```

### Model Conversion

Convert the PyTorch model to ONNX format:

```python
from onnx_inference_pipeline import convert_pytorch_to_onnx

convert_pytorch_to_onnx(
    pytorch_model_path='match_winner_all_features_2026.pt',
    onnx_output_path='match_winner_dnn_2026.onnx',
    feature_mean=feature_mean,
    feature_std=feature_std
)
```

### Running Inference

```python
from onnx_inference_pipeline import ONNXInferencePipeline

# Load normalization parameters
feature_mean = [...]  # 293 training mean values
feature_std = [...]   # 293 training std values

# Initialize pipeline
pipeline = ONNXInferencePipeline(
    onnx_model_path='match_winner_dnn_2026.onnx',
    feature_mean=feature_mean,
    feature_std=feature_std
)

# Create feature vectors
red_mean_features = [...]  # 72 features
red_std_features = [...]   # 73 features
blue_mean_features = [...] # 72 features
blue_std_features = [...]  # 73 features

# Run prediction
result = pipeline.predict_from_components(
    red_mean_features=red_mean_features,
    red_std_features=red_std_features,
    blue_mean_features=blue_mean_features,
    blue_std_features=blue_std_features,
    is_qm=True
)

print(f"Red Win Probability: {result['ensemble_prob']:.4f}")
print(f"Blue Win Probability: {result['blue_win_prob']:.4f}")
```

## Performance Considerations

### Memory Retention

The pipeline loads models into memory once at initialization and retains them throughout the application lifecycle. This prevents file system reads between predictions and ensures low-latency inference.

### Batch Processing

For processing multiple matches simultaneously, use batch operations:

```python
# Package multiple feature vectors
features_list = [
    packager.package_features(red_mean_1, red_std_1, blue_mean_1, blue_std_1, is_qm=True),
    packager.package_features(red_mean_2, red_std_2, blue_mean_2, blue_std_2, is_qm=True),
    # ... more features
]

# Normalize batch
normalized_batch = normalizer.normalize_batch(np.stack(features_list, axis=0))

# Run batch inference
inputs = {session.get_inputs()[0].name: normalized_batch}
outputs = session.run(None, inputs)
```

### Thread Safety

The ONNX Runtime session is thread-safe for concurrent inference requests. For high-throughput scenarios, consider:

```python
# Create multiple sessions for parallel inference
sessions = [
    ort.InferenceSession('model.onnx', providers=['CPUExecutionProvider'])
    for _ in range(num_threads)
]
```

## Testing

Run the comprehensive test suite:

```bash
python test_onnx_pipeline.py
```

The test suite validates:
- PyTorch to ONNX conversion
- Input data packaging
- Runtime normalization
- Ensemble blending
- Full pipeline integration

## Error Handling

The pipeline includes validation for:
- Feature vector dimensions (must be 293)
- Normalization parameter lengths
- Context flag encoding
- Probability range validation

## Future Enhancements

1. **GPU Acceleration**: Add CUDAExecutionProvider for GPU inference
2. **Quantization**: Implement INT8 quantization for reduced model size and faster inference
3. **Model Caching**: Add model versioning and caching mechanisms
4. **Monitoring**: Add performance monitoring and logging
5. **Fallback Mechanisms**: Implement graceful degradation when models fail to load

## License

This code is part of the Summer2026proj system and is licensed under the project's main license.
