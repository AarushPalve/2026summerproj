# FRC Data Importer with 30-Second Hotspot Sync

This project implements the SQLite database schema and data importer as specified in Spec 02: Data Importer & Local Storage Schema Lifecycle.

## Features

- **SQLite Database Schema**: Complete relational database design for FRC match data
- **30-Second Hotspot Sync**: Efficient data synchronization within tight time constraints
- **Performance Metrics**: EPA, OPR, and cOPR calculations with historical tracking
- **Data Parsing**: JSON parsing for match data with proper validation
- **Background Processing**: Transaction-based database operations for data integrity

## Architecture

### Database Schema

The database consists of the following main tables:

1. **events**: Event information (keys, names, dates, locations)
2. **teams**: Team information (keys, numbers, names)
3. **matches**: Match metadata (keys, levels, numbers, results)
4. **match_alliances**: Alliance scores and ranking points
5. **match_alliance_teams**: Team-to-alliance mappings
6. **match_score_breakdown**: Detailed score components
7. **team_performance_metrics**: Current EPA, OPR, and cOPR values
8. **team_performance_history**: Historical performance tracking

### Data Flow

1. **Hotspot Connection**: User connects to cellular hotspot
2. **API Fetch**: System fetches latest match data (20s timeout)
3. **Data Parsing**: JSON parsing and validation
4. **Database Import**: Transaction-based import with data integrity checks
5. **Performance Updates**: EPA/OPR/cOPR calculations using delta updates
6. **Completion**: Sync completes within 30-second window

## Implementation Details

### EPA Calculation

The system implements Expected Points Added (EPA) using exponential smoothing:

```
Δ_Alliance = Score_Actual - Σ EPA_i,before
EPA_i,after = EPA_i,before + α * (Δ_Alliance / N_teams)
```

Where α = 0.10 (learning rate) and N_teams = 3 for standard FRC matches.

### OPR and cOPR Calculation

The system uses a simplified delta update approach for performance. For a full Recursive Least Squares (RLS) implementation, see the delta updater specification.

## Usage

### Hotspot Sync

```dart
final hotspotSyncService = HotspotSyncService(
  databaseService: databaseService,
  dataImporter: dataImporter,
  apiBaseUrl: 'https://api.example.com/frc',
  eventKey: '2026cascmp',
);

// Start the 30-second sync
await hotspotSyncService.startSync();
```

### Test Data Import

```dart
final testData = '''[...]''';
await hotspotSyncService.importFromLocalJson(testData);
```

## File Structure

```
lib/
├── database/
│   ├── database_service.dart  # SQLite database management
│   └── schema.sql             # Database schema definition
├── models/
│   └── match_data.dart        # Data models and JSON parsing
├── services/
│   ├── data_importer.dart     # Core data import logic
│   └── hotspot_sync_service.dart # 30-second sync implementation
└── main.dart                  # Example usage and UI
```

## Dependencies

- `sqflite`: SQLite database support
- `path`: File path utilities
- `http`: HTTP client for API requests
- `path_provider`: Platform-specific path access

## Testing

The system includes test data import functionality for development and testing purposes. Use the "Import Test Data" button in the example UI to test the import pipeline.

## Performance Considerations

- All database operations use transactions for atomicity
- Indexes are created on frequently queried columns
- The 30-second sync includes timeout protection
- Data validation ensures only played matches are imported

## Future Enhancements

- Full RLS implementation for OPR/cOPR calculations
- Delta update optimization for large datasets
- Offline-first synchronization with conflict resolution
- Comprehensive error handling and retry logic