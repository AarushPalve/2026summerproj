import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../services/data_importer.dart';
import '../database/database_service.dart';

class HotspotSyncService {
  final DatabaseService _databaseService;
  final DataImporter _dataImporter;
  final String _apiBaseUrl;
  final String _eventKey;

  HotspotSyncService({
    required DatabaseService databaseService,
    required DataImporter dataImporter,
    required String apiBaseUrl,
    required String eventKey,
  })  : _databaseService = databaseService,
    _dataImporter = dataImporter,
    _apiBaseUrl = apiBaseUrl,
    _eventKey = eventKey;

  /// Start the 30-second hotspot sync process
  /// This method should be called when the user connects to a hotspot
  Future<void> startSync() async {
    print('Starting 30-second hotspot sync...');

    try {
      // Start timer for 30 seconds
      final stopwatch = Stopwatch()..start();

      // 1. Fetch match data from API
      final matchData = await _fetchMatchData();

      // Check if we have time left
      if (stopwatch.elapsed.inSeconds >= 25) {
        print('Warning: API fetch took too long, skipping import to avoid timeout');
        return;
      }

      // 2. Import data into database
      await _dataImporter.importMatchData(matchData);

      print('Sync completed successfully in ${stopwatch.elapsed.inSeconds} seconds');
    } catch (e) {
      print('Sync failed: $e');
      rethrow;
    }
  }

  /// Fetch match data from the API
  Future<List<dynamic>> _fetchMatchData() async {
    try {
      final url = '$_apiBaseUrl/matches/$_eventKey';
      print('Fetching match data from: $url');

      final response = await http.get(Uri.parse(url)).timeout(Duration(seconds: 20));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        // Filter out unplayed matches (played_index == 0 or null)
        final playedMatches = (data as List).where((match) {
          final playedIndex = match['played_index'] ?? 0;
          return playedIndex > 0;
        }).toList();

        print('Fetched ${playedMatches.length} played matches');
        return playedMatches;
      } else {
        throw Exception('Failed to fetch match data: ${response.statusCode}');
      }
    } on TimeoutException {
      throw Exception('API request timed out');
    } catch (e) {
      throw Exception('Failed to fetch match data: $e');
    }
  }

  /// Alternative method for testing with local JSON data
  Future<void> importFromLocalJson(String jsonData) async {
    try {
      final data = json.decode(jsonData) as List;
      await _dataImporter.importMatchData(data);
      print('Imported ${data.length} matches from local JSON');
    } catch (e) {
      print('Failed to import from local JSON: $e');
      rethrow;
    }
  }

  /// Get sync status and statistics
  Future<Map<String, dynamic>> getSyncStatus() async {
    final db = await _databaseService.database;

    final matchCount = Sqflite.firstIntValue(
      await db.rawQuery('SELECT COUNT(*) FROM matches WHERE played_index > 0')) ?? 0;
    final teamCount = Sqflite.firstIntValue(
      await db.rawQuery('SELECT COUNT(*) FROM teams')) ?? 0;

    return {
      'last_sync': DateTime.now().toIso8601String(),
      'match_count': matchCount,
      'team_count': teamCount,
      'status': 'ready',
    };
  }
}