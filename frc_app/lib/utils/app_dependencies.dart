// Dependency Injection Container
// Centralized management of app dependencies

import '../core/database.dart';
import '../data/data_repository.dart';
import '../workers/worker_manager.dart';
import '../ml/onnx_inference.dart';
import '../data/sync_manager.dart';

class AppDependencies {
  late final FRCDatabase database;
  late final DataRepository repository;
  late final WorkerManager workerManager;
  late final ONNXInferenceEngine onnxEngine;
  late final SyncManager syncManager;

  Future<void> initialize() async {
    // Initialize database
    database = FRCDatabase();

    // Initialize repository
    repository = DataRepository(database: database);

    // Initialize worker manager
    workerManager = WorkerManager();

    // Initialize ONNX inference engine
    onnxEngine = ONNXInferenceEngine();
    await onnxEngine.initialize(intraOpThreadCount: 2, interOpThreadCount: 2);

    // Initialize sync manager
    // In production, this would use the actual API base URL
    syncManager = SyncManager(
      repository: repository,
      workerManager: workerManager,
      apiBaseUrl: 'https://api.frc-events.com/v1', // Example API
    );
  }

  Future<void> dispose() async {
    await onnxEngine.close();
    await workerManager.stopAllWorkers();
    await database.close();
  }
}