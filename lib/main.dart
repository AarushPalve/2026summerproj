import 'package:flutter/material.dart';
import 'database/database_service.dart';
import 'services/data_importer.dart';
import 'services/hotspot_sync_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize services
  final databaseService = DatabaseService();
  final dataImporter = DataImporter(databaseService);

  // Example usage
  final hotspotSyncService = HotspotSyncService(
    databaseService: databaseService,
    dataImporter: dataImporter,
    apiBaseUrl: 'https://api.example.com/frc',
    eventKey: '2026cascmp',
  );

  runApp(MyApp(hotspotSyncService: hotspotSyncService));
}

class MyApp extends StatelessWidget {
  final HotspotSyncService hotspotSyncService;

  const MyApp({Key? key, required this.hotspotSyncService}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FRC Data Importer',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: SyncScreen(hotspotSyncService: hotspotSyncService),
    );
  }
}

class SyncScreen extends StatefulWidget {
  final HotspotSyncService hotspotSyncService;

  const SyncScreen({Key? key, required this.hotspotSyncService}) : super(key: key);

  @override
  _SyncScreenState createState() => _SyncScreenState();
}

class _SyncScreenState extends State<SyncScreen> {
  bool _isSyncing = false;
  String _status = 'Ready to sync';
  Map<String, dynamic> _syncStats = {};

  Future<void> _startSync() async {
    setState(() {
      _isSyncing = true;
      _status = 'Syncing...';
    });

    try {
      await widget.hotspotSyncService.startSync();
      final stats = await widget.hotspotSyncService.getSyncStatus();

      setState(() {
        _status = 'Sync completed!';
        _syncStats = stats;
      });
    } catch (e) {
      setState(() {
        _status = 'Sync failed: $e';
      });
    } finally {
      setState(() {
        _isSyncing = false;
      });
    }
  }

  Future<void> _importTestData() async {
    setState(() {
      _isSyncing = true;
      _status = 'Importing test data...';
    });

    try {
      // Example test data
      final testData = '''[
        {
          "match_key": "2026cascmp_qm72",
          "comp_level": "qm",
          "match_number": 72,
          "set_number": 1,
          "played_index": 43,
          "winning_alliance": "red",
          "alliances": {
            "red": {"score": 85, "team_keys": ["frc254", "frc1323", "frc1678"]},
            "blue": {"score": 72, "team_keys": ["frc971", "frc118", "frc1619"]}
          },
          "score_breakdown": {
            "red": {
              "totalPoints": 85,
              "autoPoints": 30,
              "teleopPoints": 45,
              "foulPoints": 10,
              "rp": 4
            },
            "blue": {
              "totalPoints": 72,
              "autoPoints": 22,
              "teleopPoints": 50,
              "foulPoints": 0,
              "rp": 1
            }
          }
        }
      ]''';

      await widget.hotspotSyncService.importFromLocalJson(testData);
      final stats = await widget.hotspotSyncService.getSyncStatus();

      setState(() {
        _status = 'Test data imported!';
        _syncStats = stats;
      });
    } catch (e) {
      setState(() {
        _status = 'Import failed: $e';
      });
    } finally {
      setState(() {
        _isSyncing = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('FRC Data Sync'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              _status,
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 20),
            if (_syncStats.isNotEmpty) ...[
              Text('Matches: ${_syncStats['match_count'] ?? 0}'),
              Text('Teams: ${_syncStats['team_count'] ?? 0}'),
              SizedBox(height: 20),
            ],
            ElevatedButton(
              onPressed: _isSyncing ? null : _startSync,
              child: Text('Start Hotspot Sync'),
            ),
            SizedBox(height: 10),
            ElevatedButton(
              onPressed: _isSyncing ? null : _importTestData,
              child: Text('Import Test Data'),
            ),
            if (_isSyncing) ...[
              SizedBox(height: 20),
              CircularProgressIndicator(),
            ],
          ],
        ),
      ),
    );
  }
}