import 'package:sqflite/sqflite.dart';
import '../database/database_service.dart';
import '../models/match_data.dart';

class DataImporter {
  final DatabaseService _databaseService;

  DataImporter(this._databaseService);

  /// Main method to import match data from JSON
  /// This is called during the 30-second hotspot sync window
  Future<void> importMatchData(List<dynamic> matchDataList) async {
    final db = await _databaseService.database;

    await db.transaction((txn) async {
      for (final matchJson in matchDataList) {
        try {
          final matchData = MatchData.fromJson(matchJson);
          await _importSingleMatch(txn, matchData);
        } catch (e) {
          print('Error importing match: ${matchJson['match_key']} - $e');
          continue;
        }
      }
    });
  }

  /// Import a single match and update all related data
  Future<void> _importSingleMatch(Transaction txn, MatchData matchData) async {
    // Extract event key from match key (format: event_key_comp_level_match_number)
    final eventKey = matchData.matchKey.split('_').take(2).join('_');

    // 1. Ensure event exists
    await _ensureEventExists(txn, eventKey);

    // 2. Ensure all teams exist
    for (final alliance in matchData.alliances.values) {
      for (final teamKey in alliance.teamKeys) {
        await _ensureTeamExists(txn, teamKey);
      }
    }

    // 3. Insert or update the match
    await _upsertMatch(txn, matchData, eventKey);

    // 4. Insert alliance data
    await _insertAlliances(txn, matchData);

    // 5. Insert score breakdown
    await _insertScoreBreakdown(txn, matchData);

    // 6. Update team performance metrics (EPA, OPR, cOPR)
    await _updateTeamPerformanceMetrics(txn, matchData);
  }

  Future<void> _ensureEventExists(Transaction txn, String eventKey) async {
    final result = await txn.query(
      'events',
      where: 'event_key = ?',
      whereArgs: [eventKey],
    );

    if (result.isEmpty) {
      await txn.insert(
        'events',
        {
          'event_key': eventKey,
          'event_name': 'Event $eventKey', // Will be updated later if needed
          'event_type': 'unknown',
          'start_date': DateTime.now().toIso8601String(),
          'end_date': DateTime.now().toIso8601String(),
          'location': 'Unknown',
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
  }

  Future<void> _ensureTeamExists(Transaction txn, String teamKey) async {
    final result = await txn.query(
      'teams',
      where: 'team_key = ?',
      whereArgs: [teamKey],
    );

    if (result.isEmpty) {
      // Extract team number from team key (format: frcXXXX)
      final teamNumber = int.tryParse(teamKey.replaceFirst('frc', '')) ?? 0;

      await txn.insert(
        'teams',
        {
          'team_key': teamKey,
          'team_number': teamNumber,
          'team_name': 'Team $teamNumber',
          'rookie_year': 2020, // Default value
          'location': 'Unknown',
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );

      // Initialize performance metrics for new team
      await txn.insert(
        'team_performance_metrics',
        {
          'team_key': teamKey,
          'epa': 0.0,
          'opr': 0.0,
          'copr_total_points': 0.0,
          'copr_auto_points': 0.0,
          'copr_teleop_points': 0.0,
          'copr_foul_points': 0.0,
          'last_updated': DateTime.now().toIso8601String(),
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
  }

  Future<void> _upsertMatch(Transaction txn, MatchData matchData, String eventKey) async {
    await txn.insert(
      'matches',
      {
        'match_key': matchData.matchKey,
        'event_key': eventKey,
        'comp_level': matchData.compLevel,
        'match_number': matchData.matchNumber,
        'set_number': matchData.setNumber,
        'played_index': matchData.playedIndex,
        'winning_alliance': matchData.winningAlliance,
        'actual_start_time': DateTime.now().toIso8601String(),
        'scheduled_start_time': DateTime.now().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<void> _insertAlliances(Transaction txn, MatchData matchData) async {
    for (final entry in matchData.alliances.entries) {
      final color = entry.key;
      final alliance = entry.value;

      // Insert alliance data
      await txn.insert(
        'match_alliances',
        {
          'match_key': matchData.matchKey,
          'alliance_color': color,
          'score': alliance.score,
          'rp': matchData.scoreBreakdown[color]?.rp ?? 0,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );

      // Insert team alliances
      for (final teamKey in alliance.teamKeys) {
        await txn.insert(
          'match_alliance_teams',
          {
            'match_key': matchData.matchKey,
            'alliance_color': color,
            'team_key': teamKey,
          },
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
    }
  }

  Future<void> _insertScoreBreakdown(Transaction txn, MatchData matchData) async {
    for (final entry in matchData.scoreBreakdown.entries) {
      final color = entry.key;
      final breakdown = entry.value;

      await txn.insert(
        'match_score_breakdown',
        {
          'match_key': matchData.matchKey,
          'alliance_color': color,
          'total_points': breakdown.totalPoints,
          'auto_points': breakdown.autoPoints,
          'teleop_points': breakdown.teleopPoints,
          'foul_points': breakdown.foulPoints,
          'rp': breakdown.rp,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
  }

  /// Update team performance metrics using EPA and OPR calculations
  Future<void> _updateTeamPerformanceMetrics(Transaction txn, MatchData matchData) async {
    final timestamp = DateTime.now().toIso8601String();

    // Get current metrics for all teams in this match
    final teamKeys = matchData.alliances.values.expand((a) => a.teamKeys).toList();
    final currentMetrics = await _getCurrentTeamMetrics(txn, teamKeys);

    // Calculate alliance deltas and update metrics
    for (final color in ['red', 'blue']) {
      if (matchData.alliances.containsKey(color) && matchData.scoreBreakdown.containsKey(color)) {
        final alliance = matchData.alliances[color]!;
        final breakdown = matchData.scoreBreakdown[color]!;
        final teamCount = alliance.teamKeys.length;

        // Calculate EPA delta for this alliance
        final actualScore = breakdown.totalPoints.toDouble();
        final predictedScore = alliance.teamKeys.fold(0.0, (sum, teamKey) {
          return sum + (currentMetrics[teamKey]?.epa ?? 0.0);
        });
        final allianceDelta = actualScore - predictedScore;
        final epaDeltaPerTeam = allianceDelta / teamCount;

        // Update each team's metrics
        for (final teamKey in alliance.teamKeys) {
          final currentMetric = currentMetrics[teamKey] ?? TeamPerformanceMetric(
            teamKey: teamKey,
            epa: 0.0,
            opr: 0.0,
            coprTotalPoints: 0.0,
            coprAutoPoints: 0.0,
            coprTeleopPoints: 0.0,
            coprFoulPoints: 0.0,
          );

          // Calculate new EPA (using learning rate alpha = 0.10)
          final alpha = 0.10;
          final newEpa = currentMetric.epa + alpha * epaDeltaPerTeam;

          // For simplicity, we'll use the same approach for other metrics
          // In a production system, we would implement the full RLS algorithm
          final newOpr = currentMetric.opr + alpha * (breakdown.totalPoints.toDouble() / teamCount - currentMetric.opr);
          final newCoprTotal = currentMetric.coprTotalPoints + alpha * (breakdown.totalPoints.toDouble() / teamCount - currentMetric.coprTotalPoints);
          final newCoprAuto = currentMetric.coprAutoPoints + alpha * (breakdown.autoPoints.toDouble() / teamCount - currentMetric.coprAutoPoints);
          final newCoprTeleop = currentMetric.coprTeleopPoints + alpha * (breakdown.teleopPoints.toDouble() / teamCount - currentMetric.coprTeleopPoints);
          final newCoprFoul = currentMetric.coprFoulPoints + alpha * (breakdown.foulPoints.toDouble() / teamCount - currentMetric.coprFoulPoints);

          // Update performance metrics
          await txn.update(
            'team_performance_metrics',
            {
              'epa': newEpa,
              'opr': newOpr,
              'copr_total_points': newCoprTotal,
              'copr_auto_points': newCoprAuto,
              'copr_teleop_points': newCoprTeleop,
              'copr_foul_points': newCoprFoul,
              'last_updated': timestamp,
            },
            where: 'team_key = ?',
            whereArgs: [teamKey],
          );

          // Record history
          await txn.insert(
            'team_performance_history',
            {
              'team_key': teamKey,
              'match_key': matchData.matchKey,
              'timestamp': timestamp,
              'epa_before': currentMetric.epa,
              'epa_after': newEpa,
              'opr_before': currentMetric.opr,
              'opr_after': newOpr,
              'copr_total_points_before': currentMetric.coprTotalPoints,
              'copr_total_points_after': newCoprTotal,
              'copr_auto_points_before': currentMetric.coprAutoPoints,
              'copr_auto_points_after': newCoprAuto,
              'copr_teleop_points_before': currentMetric.coprTeleopPoints,
              'copr_teleop_points_after': newCoprTeleop,
              'copr_foul_points_before': currentMetric.coprFoulPoints,
              'copr_foul_points_after': newCoprFoul,
            },
            conflictAlgorithm: ConflictAlgorithm.ignore,
          );
        }
      }
    }
  }

  Future<Map<String, TeamPerformanceMetric>> _getCurrentTeamMetrics(
      Transaction txn, List<String> teamKeys) async {
    if (teamKeys.isEmpty) return {};

    final placeholders = List.filled(teamKeys.length, '?').join(',');
    final result = await txn.query(
      'team_performance_metrics',
      where: 'team_key IN ($placeholders)',
      whereArgs: teamKeys,
    );

    final metrics = <String, TeamPerformanceMetric>{};
    for (final row in result) {
      metrics[row['team_key'] as String] = TeamPerformanceMetric(
        teamKey: row['team_key'] as String,
        epa: (row['epa'] as num).toDouble(),
        opr: (row['opr'] as num).toDouble(),
        coprTotalPoints: (row['copr_total_points'] as num).toDouble(),
        coprAutoPoints: (row['copr_auto_points'] as num).toDouble(),
        coprTeleopPoints: (row['copr_teleop_points'] as num).toDouble(),
        coprFoulPoints: (row['copr_foul_points'] as num).toDouble(),
      );
    }

    return metrics;
  }
}

class TeamPerformanceMetric {
  final String teamKey;
  final double epa;
  final double opr;
  final double coprTotalPoints;
  final double coprAutoPoints;
  final double coprTeleopPoints;
  final double coprFoulPoints;

  TeamPerformanceMetric({
    required this.teamKey,
    required this.epa,
    required this.opr,
    required this.coprTotalPoints,
    required this.coprAutoPoints,
    required this.coprTeleopPoints,
    required this.coprFoulPoints,
  });
}