# FRC Strategy & Forecasting App

An offline-first Flutter application for FRC teams with severe personnel constraints, implementing the Zero-Scouter Paradigm as specified in `01_system_architecture.md`.

## Architecture Overview

This implementation follows the specifications in `01_system_architecture.md`:

### 1. Cross-Platform UI Layer (Flutter)
- Single codebase for iOS and Android
- Hardware-accelerated UI rendering
- Strict type-safety with Dart

### 2. Data Management Layer (SQLite)
- Relational database with composite indexing
- ACID-compliant transactions
- Optimized for complex FRC queries

### 3. Edge ML Engine (ONNX Runtime Mobile)
- High-performance inference on-device
- Multi-threaded execution
- Preserves PyTorch model precision

### 4. Background Processing (Dart Isolates)
- UI thread protection
- Parallel data processing
- Worker pool management

## Key Components

### Database Layer (`lib/core/database.dart`)
- SQLite implementation with `sqflite` package
- Schema for Events, Teams, Matches, Alliances, and Metrics
- Atomic transaction support
- Composite indexes for performance

### Data Models (`lib/models/frc_models.dart`)
- Event, Team, Match, MatchTeam, MatchResult, TeamMetric
- JSON serialization/deserialization
- Type-safe data structures

### Data Repository (`lib/data/data_repository.dart`)
- CRUD operations for all entities
- Bulk insert operations for synchronization
- Query methods with proper indexing

### Worker System (`lib/workers/worker_manager.dart`)
- Dart Isolate-based background processing
- Worker pool management
- Message passing architecture
- Predefined worker functions for parsing, metrics, ML

### ML Inference (`lib/ml/onnx_inference.dart`)
- ONNX Runtime Mobile integration
- Multi-threaded inference
- Model loading and management
- FRC-specific prediction helpers

### Synchronization (`lib/data/sync_manager.dart`)
- 30-second hotspot window optimization
- Atomic data updates
- Progress tracking
- Error handling and recovery

### Dependency Injection (`lib/utils/app_dependencies.dart`)
- Centralized service management
- Lifecycle control
- Easy testing and mocking

## Setup Instructions

1. **Prerequisites:**
   - Flutter SDK (>= 2.18.0)
   - Dart SDK
   - Android Studio / Xcode for platform-specific builds

2. **Install dependencies:**
   ```bash
   flutter pub get
   ```

3. **Add ML models:**
   - Place ONNX models in `assets/models/`
   - Update model loading code in `ONNXInferenceEngine`

4. **Configure API:**
   - Update API base URL in `SyncManager`
   - Implement proper authentication if needed

5. **Run the app:**
   ```bash
   flutter run
   ```

## Data Flow

1. **Hotspot Sync (30s window):**
   - User connects via cellular hotspot
   - SyncManager fetches latest data from API
   - Data is passed to Isolate workers for parsing

2. **Database Storage:**
   - Workers store data in SQLite using atomic transactions
   - Composite indexes ensure fast lookups

3. **Metrics Calculation:**
   - Background workers compute OPR, EPA, cCPR
   - Results stored in team_metrics table

4. **ML Prediction:**
   - Feature vectors constructed from updated metrics
   - ONNX Runtime runs inference on-device
   - Predictions cached for offline use

## Performance Considerations

- **Isolate Workers:** Prevent UI jank during heavy calculations
- **SQLite Indexes:** Optimize complex relational queries
- **ONNX Threading:** Configure intra/inter-op thread counts
- **Batch Operations:** Minimize database I/O during sync

## Error Handling

- Network timeouts during sync
- Database constraint violations
- ML inference errors
- Worker communication failures

## Testing

The app includes basic test functionality:
- Database CRUD operations
- ML inference testing
- Sync simulation

## Future Enhancements

- Model versioning and updates
- Advanced caching strategies
- Offline-first UI patterns
- Comprehensive error recovery

## License

MIT License - see LICENSE file for details.