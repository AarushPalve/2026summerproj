// ONNX Runtime Mobile Inference Engine
// Spec: 01_system_architecture.md Section 2.3

import 'dart:typed_data';
import 'package:onnxruntime/onnxruntime.dart' as onnx;
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';

class ONNXInferenceEngine {
  static final ONNXInferenceEngine _instance = ONNXInferenceEngine._internal();
  factory ONNXInferenceEngine() => _instance;

  onnx.ONNXRuntime? _runtime;
  Map<String, onnx.ONNXModel> _models = {};
  bool _initialized = false;

  ONNXInferenceEngine._internal();

  // Initialize ONNX Runtime
  Future<void> initialize({int intraOpThreadCount = 2, int interOpThreadCount = 2}) async {
    if (_initialized) return;

    try {
      // Create ONNX Runtime with multi-threading configuration
      _runtime = onnx.ONNXRuntime(
        intraOpThreadCount: intraOpThreadCount,
        interOpThreadCount: interOpThreadCount,
      );
      _initialized = true;
    } catch (e) {
      throw Exception('Failed to initialize ONNX Runtime: ${e.toString()}');
    }
  }

  // Load a model from assets
  Future<void> loadModel(String modelName, String assetPath) async {
    if (_runtime == null) {
      await initialize();
    }

    try {
      // Get the application documents directory
      final appDir = await getApplicationDocumentsDirectory();
      final modelPath = join(appDir.path, modelName);

      // Check if model is already loaded
      if (_models.containsKey(modelName)) {
        return;
      }

      // Load the model from assets and copy to app directory
      // In a real Flutter app, you would use rootBundle to load from assets
      // For this implementation, we'll assume the model is properly bundled

      final model = await _runtime!.loadModel(modelPath);
      _models[modelName] = model;
    } catch (e) {
      throw Exception('Failed to load model $modelName: ${e.toString()}');
    }
  }

  // Run inference on a model
  Future<Map<String, dynamic>> runInference(String modelName, List<double> input) async {
    if (!_models.containsKey(modelName)) {
      throw Exception('Model $modelName not loaded');
    }

    try {
      final model = _models[modelName]!;

      // Convert input to Float32List (ONNX expected format)
      final inputTensor = Float32List.fromList(input);
      final inputShape = [1, input.length]; // Batch size 1

      // Create input map
      final inputs = {
        'input': onnx.ONNXTensor(
          inputTensor,
          shape: inputShape,
          type: onnx.ONNXTensorType.float,
        )
      };

      // Run inference
      final outputs = await model.run(inputs);

      // Process outputs
      if (outputs.containsKey('output')) {
        final outputTensor = outputs['output']! as onnx.ONNXTensor;
        final outputData = outputTensor.data as Float32List;

        return {
          'success': true,
          'output': outputData.toList(),
          'shape': outputTensor.shape,
        };
      } else {
        throw Exception('No output tensor found');
      }
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  // Run inference with multiple inputs (for more complex models)
  Future<Map<String, dynamic>> runMultiInputInference(
    String modelName,
    Map<String, List<double>> inputs,
    Map<String, List<int>> inputShapes,
  ) async {
    if (!_models.containsKey(modelName)) {
      throw Exception('Model $modelName not loaded');
    }

    try {
      final model = _models[modelName]!;
      final onnxInputs = <String, onnx.ONNXTensor>{};

      // Convert all inputs to ONNX tensors
      inputs.forEach((name, data) {
        final tensorData = Float32List.fromList(data);
        final shape = inputShapes[name]!;

        onnxInputs[name] = onnx.ONNXTensor(
          tensorData,
          shape: shape,
          type: onnx.ONNXTensorType.float,
        );
      });

      // Run inference
      final outputs = await model.run(onnxInputs);

      // Process outputs
      final result = <String, dynamic>{};
      outputs.forEach((name, tensor) {
        final outputTensor = tensor as onnx.ONNXTensor;
        result[name] = {
          'data': (outputTensor.data as Float32List).toList(),
          'shape': outputTensor.shape,
        };
      });

      return {
        'success': true,
        'outputs': result,
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }

  // Get loaded models
  List<String> getLoadedModels() {
    return _models.keys.toList();
  }

  // Unload a model
  Future<void> unloadModel(String modelName) async {
    if (_models.containsKey(modelName)) {
      _models.remove(modelName);
    }
  }

  // Close the inference engine
  Future<void> close() async {
    _models.clear();
    _runtime = null;
    _initialized = false;
  }

  // Helper method to prepare FRC match prediction input
  Future<Map<String, dynamic>> predictMatchOutcome(
    String modelName,
    Map<String, double> redAllianceMetrics,
    Map<String, double> blueAllianceMetrics,
  ) async {
    try {
      // Combine metrics into a single input vector
      // This would be specific to your model's expected input format
      final inputVector = <double>[];

      // Add red alliance metrics
      final redMetrics = [
        'opr', 'epa', 'ccwm', 'auto_points', 'teleop_points', 'endgame_points'
      ];
      for (var metric in redMetrics) {
        inputVector.add(redAllianceMetrics[metric] ?? 0.0);
      }

      // Add blue alliance metrics
      final blueMetrics = [
        'opr', 'epa', 'ccwm', 'auto_points', 'teleop_points', 'endgame_points'
      ];
      for (var metric in blueMetrics) {
        inputVector.add(blueAllianceMetrics[metric] ?? 0.0);
      }

      // Run inference
      final result = await runInference(modelName, inputVector);

      if (result['success']) {
        final output = result['output'] as List<double>;
        return {
          'success': true,
          'red_win_probability': output[0],
          'blue_win_probability': output[1],
          'confidence': (output[0] - output[1]).abs(),
        };
      } else {
        return {
          'success': false,
          'error': result['error'],
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': e.toString(),
      };
    }
  }
}