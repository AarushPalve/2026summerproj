// Data Synchronization Manager
// Spec: 01_system_architecture.md Section 3.1

import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/database.dart';
import '../data/data_repository.dart';
import '../workers/worker_manager.dart';
import '../models/frc_models.dart';

class SyncManager {
  final DataRepository repository;
  final WorkerManager workerManager;
  final String apiBaseUrl;
  final Duration syncTimeout;

  SyncManager({
    required this.repository,
    required this.workerManager,
    required this.apiBaseUrl,
    this.syncTimeout = const Duration(seconds: 30),
  });

  // Perform a complete synchronization
  Future<SyncResult> performSync() async {
    final syncStartTime = DateTime.now();
    final result = SyncResult();

    try {
      // Start data parser worker
      await workerManager.startWorker('data_parser', WorkerFunctions.dataParserWorker);

      // 1. Fetch events
      result.eventsSync = await _syncEvents();

      // 2. Check if we're running out of time
      if (DateTime.now().difference(syncStartTime) > syncTimeout) {
        result.status = SyncStatus.partial;
        result.message = 'Timeout reached during sync';
        return result;
      }

      // 3. Fetch teams
      result.teamsSync = await _syncTeams();

      // 4. Check time again
      if (DateTime.now().difference(syncStartTime) > syncTimeout) {
        result.status = SyncStatus.partial;
        result.message = 'Timeout reached during sync';
        return result;
      }

      // 5. Fetch matches and results
      result.matchesSync = await _syncMatches();

      result.status = SyncStatus.success;
      result.message = 'Sync completed successfully';
    } catch (e) {
      result.status = SyncStatus.error;
      result.message = 'Sync failed: ${e.toString()}';
      result.error = e.toString();
    } finally {
      // Stop the worker
      await workerManager.stopWorker('data_parser');
    }

    return result;
  }

  // Sync events
  Future<SyncOperationResult> _syncEvents() async {
    final operation = SyncOperationResult(operation: 'events');
    final startTime = DateTime.now();

    try {
      // Fetch events from API
      final response = await http.get(
        Uri.parse('$apiBaseUrl/events'),
        headers: {'Accept': 'application/json'},
      ).timeout(syncTimeout);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final events = (data as List).map((e) => Event.fromMap(e)).toList();

        // Send to worker for processing
        await workerManager.sendToWorker('data_parser', {
          'action': 'parse_events',
          'events': events.map((e) => e.toMap()).toList(),
        });

        operation.successCount = events.length;
        operation.status = SyncOperationStatus.success;
      } else {
        throw Exception('Failed to fetch events: ${response.statusCode}');
      }
    } catch (e) {
      operation.status = SyncOperationStatus.error;
      operation.error = e.toString();
    }

    operation.duration = DateTime.now().difference(startTime);
    return operation;
  }

  // Sync teams
  Future<SyncOperationResult> _syncTeams() async {
    final operation = SyncOperationResult(operation: 'teams');
    final startTime = DateTime.now();

    try {
      // Fetch teams from API
      final response = await http.get(
        Uri.parse('$apiBaseUrl/teams'),
        headers: {'Accept': 'application/json'},
      ).timeout(syncTimeout);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final teams = (data as List).map((t) => Team.fromMap(t)).toList();

        // Send to worker for processing
        await workerManager.sendToWorker('data_parser', {
          'action': 'parse_teams',
          'teams': teams.map((t) => t.toMap()).toList(),
        });

        operation.successCount = teams.length;
        operation.status = SyncOperationStatus.success;
      } else {
        throw Exception('Failed to fetch teams: ${response.statusCode}');
      }
    } catch (e) {
      operation.status = SyncOperationStatus.error;
      operation.error = e.toString();
    }

    operation.duration = DateTime.now().difference(startTime);
    return operation;
  }

  // Sync matches
  Future<SyncOperationResult> _syncMatches() async {
    final operation = SyncOperationResult(operation: 'matches');
    final startTime = DateTime.now();

    try {
      // Get all events to fetch matches for
      final events = await repository.getEvents();
      int totalMatches = 0;

      for (var event in events) {
        // Fetch matches for this event
        final response = await http.get(
          Uri.parse('$apiBaseUrl/events/${event.eventId}/matches'),
          headers: {'Accept': 'application/json'},
        ).timeout(syncTimeout);

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          final matches = (data as List).map((m) => Match.fromMap(m)).toList();
          final matchTeams = <MatchTeam>[];
          final matchResults = <MatchResult>[];

          // Process each match
          for (var matchData in data) {
            // Parse match teams
            if (matchData['alliances'] != null) {
              final alliances = matchData['alliances'] as Map;

              // Red alliance
              if (alliances['red'] != null) {
                final redTeams = alliances['red']['team_keys'] as List;
                for (int i = 0; i < redTeams.length; i++) {
                  matchTeams.add(MatchTeam(
                    matchId: matchData['key'],
                    teamId: redTeams[i].toString().replaceFirst('frc', ''),
                    allianceColor: 'red',
                    position: i + 1,
                  ));
                }
              }

              // Blue alliance
              if (alliances['blue'] != null) {
                final blueTeams = alliances['blue']['team_keys'] as List;
                for (int i = 0; i < blueTeams.length; i++) {
                  matchTeams.add(MatchTeam(
                    matchId: matchData['key'],
                    teamId: blueTeams[i].toString().replaceFirst('frc', ''),
                    allianceColor: 'blue',
                    position: i + 1,
                  ));
                }
              }
            }

            // Parse match results
            if (matchData['score_breakdown'] != null) {
              final breakdown = matchData['score_breakdown'] as Map;
              if (breakdown['red'] != null && breakdown['blue'] != null) {
                matchResults.add(MatchResult(
                  matchId: matchData['key'],
                  redScore: breakdown['red']['totalPoints'] as int?,
                  blueScore: breakdown['blue']['totalPoints'] as int?,
                  redRp: _calculateRP(breakdown['red']),
                  blueRp: _calculateRP(breakdown['blue']),
                  winningAlliance: matchData['winning_alliance'],
                  status: matchData['actual_time'] != null ? 'completed' : 'scheduled',
                ));
              }
            }
          }

          // Send matches to worker
          await workerManager.sendToWorker('data_parser', {
            'action': 'parse_matches',
            'matches': matches.map((m) => m.toMap()).toList(),
          });

          // Send match teams to worker
          await workerManager.sendToWorker('data_parser', {
            'action': 'parse_match_teams',
            'match_teams': matchTeams.map((mt) => mt.toMap()).toList(),
          });

          // Send match results to worker
          await workerManager.sendToWorker('data_parser', {
            'action': 'parse_match_results',
            'match_results': matchResults.map((mr) => mr.toMap()).toList(),
          });

          totalMatches += matches.length;
        }
      }

      operation.successCount = totalMatches;
      operation.status = SyncOperationStatus.success;
    } catch (e) {
      operation.status = SyncOperationStatus.error;
      operation.error = e.toString();
    }

    operation.duration = DateTime.now().difference(startTime);
    return operation;
  }

  // Calculate ranking points from score breakdown
  int _calculateRP(Map<String, dynamic> allianceScore) {
    int rp = 0;
    // FRC ranking point calculation logic
    // This would be specific to the current game's rules
    return rp;
  }

  // Start metrics calculation after sync
  Future<void> calculateMetricsAfterSync() async {
    try {
      // Start metrics calculator worker
      await workerManager.startWorker('metrics_calculator', WorkerFunctions.metricsCalculatorWorker);

      // Get all events
      final events = await repository.getEvents();

      // Calculate metrics for each event
      for (var event in events) {
        await workerManager.sendToWorker('metrics_calculator', {
          'event_id': event.eventId,
        });
      }

      // Wait a bit for calculations to complete
      await Future.delayed(Duration(seconds: 2));
      await workerManager.stopWorker('metrics_calculator');
    } catch (e) {
      throw Exception('Failed to calculate metrics: ${e.toString()}');
    }
  }

  // Run ML predictions after metrics are calculated
  Future<void> runPredictionsAfterSync() async {
    try {
      // Start ML inference worker
      await workerManager.startWorker('ml_inference', WorkerFunctions.mlInferenceWorker);

      // Get upcoming matches that need predictions
      final events = await repository.getEvents();
      for (var event in events) {
        final matches = await repository.getMatchesByEvent(event.eventId);
        for (var match in matches) {
          if (match.matchType == 'qualification' || match.matchType == 'playoff') {
            // Prepare input data for prediction
            final matchTeams = await repository.getMatchTeams(match.matchId);
            final redTeams = matchTeams.where((mt) => mt.allianceColor == 'red').toList();
            final blueTeams = matchTeams.where((mt) => mt.allianceColor == 'blue').toList();

            // Get metrics for each team
            final redMetrics = <String, double>{};
            final blueMetrics = <String, double>{};

            for (var team in redTeams) {
              final opr = await repository.getTeamMetric(team.teamId, event.eventId, 'opr') ?? 0.0;
              final epa = await repository.getTeamMetric(team.teamId, event.eventId, 'epa') ?? 0.0;
              // Add more metrics as needed
              redMetrics['team_${team.position}_opr'] = opr;
              redMetrics['team_${team.position}_epa'] = epa;
            }

            for (var team in blueTeams) {
              final opr = await repository.getTeamMetric(team.teamId, event.eventId, 'opr') ?? 0.0;
              final epa = await repository.getTeamMetric(team.teamId, event.eventId, 'epa') ?? 0.0;
              // Add more metrics as needed
              blueMetrics['team_${team.position}_opr'] = opr;
              blueMetrics['team_${team.position}_epa'] = epa;
            }

            // Send prediction request
            await workerManager.sendToWorker('ml_inference', {
              'model_input': {
                'red_alliance': redMetrics,
                'blue_alliance': blueMetrics,
                'match_id': match.matchId,
              }
            });
          }
        }
      }

      // Wait for predictions to complete
      await Future.delayed(Duration(seconds: 5));
      await workerManager.stopWorker('ml_inference');
    } catch (e) {
      throw Exception('Failed to run predictions: ${e.toString()}');
    }
  }
}

// Sync result classes
enum SyncStatus { success, partial, error }

enum SyncOperationStatus { success, partial, error, skipped }

class SyncResult {
  SyncStatus status;
  String message;
  String? error;
  SyncOperationResult? eventsSync;
  SyncOperationResult? teamsSync;
  SyncOperationResult? matchesSync;
  Duration? totalDuration;

  SyncResult({
    this.status = SyncStatus.success,
    this.message = '',
    this.error,
    this.eventsSync,
    this.teamsSync,
    this.matchesSync,
    this.totalDuration,
  });
}

class SyncOperationResult {
  final String operation;
  SyncOperationStatus status;
  int successCount;
  int errorCount;
  Duration duration;
  String? error;

  SyncOperationResult({
    required this.operation,
    this.status = SyncOperationStatus.success,
    this.successCount = 0,
    this.errorCount = 0,
    this.duration = Duration.zero,
    this.error,
  });
}