// Data Repository - Database Access Layer
// Spec: 01_system_architecture.md Section 3.3

import '../core/database.dart';
import '../models/frc_models.dart';
import 'package:sqflite/sqflite.dart';

class DataRepository {
  final FRCDatabase database;

  DataRepository({required this.database});

  // Event operations
  Future<void> insertEvent(Event event) async {
    final db = await database.database;
    await db.insert('events', event.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Event>> getEvents() async {
    final db = await database.database;
    final maps = await db.query('events');
    return List.generate(maps.length, (i) => Event.fromMap(maps[i]));
  }

  Future<Event?> getEventById(String eventId) async {
    final db = await database.database;
    final maps = await db.query('events', where: 'event_id = ?', whereArgs: [eventId]);
    if (maps.isEmpty) return null;
    return Event.fromMap(maps.first);
  }

  // Team operations
  Future<void> insertTeam(Team team) async {
    final db = await database.database;
    await db.insert('teams', team.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Team>> getTeams() async {
    final db = await database.database;
    final maps = await db.query('teams');
    return List.generate(maps.length, (i) => Team.fromMap(maps[i]));
  }

  Future<Team?> getTeamById(String teamId) async {
    final db = await database.database;
    final maps = await db.query('teams', where: 'team_id = ?', whereArgs: [teamId]);
    if (maps.isEmpty) return null;
    return Team.fromMap(maps.first);
  }

  // Match operations
  Future<void> insertMatch(Match match) async {
    final db = await database.database;
    await db.insert('matches', match.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Match>> getMatchesByEvent(String eventId) async {
    final db = await database.database;
    final maps = await db.query('matches', where: 'event_id = ?', whereArgs: [eventId], orderBy: 'match_type, match_number');
    return List.generate(maps.length, (i) => Match.fromMap(maps[i]));
  }

  // Match Team operations
  Future<void> insertMatchTeam(MatchTeam matchTeam) async {
    final db = await database.database;
    await db.insert('match_teams', matchTeam.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<MatchTeam>> getMatchTeams(String matchId) async {
    final db = await database.database;
    final maps = await db.query('match_teams', where: 'match_id = ?', whereArgs: [matchId], orderBy: 'alliance_color, position');
    return List.generate(maps.length, (i) => MatchTeam.fromMap(maps[i]));
  }

  // Match Result operations
  Future<void> insertMatchResult(MatchResult result) async {
    final db = await database.database;
    await db.insert('match_results', result.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<MatchResult?> getMatchResult(String matchId) async {
    final db = await database.database;
    final maps = await db.query('match_results', where: 'match_id = ?', whereArgs: [matchId]);
    if (maps.isEmpty) return null;
    return MatchResult.fromMap(maps.first);
  }

  // Team Metric operations
  Future<void> insertTeamMetric(TeamMetric metric) async {
    final db = await database.database;
    await db.insert('team_metrics', metric.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<TeamMetric>> getTeamMetricsByEvent(String eventId, String metricType) async {
    final db = await database.database;
    final maps = await db.query(
      'team_metrics',
      where: 'event_id = ? AND metric_type = ?',
      whereArgs: [eventId, metricType],
      orderBy: 'value DESC',
    );
    return List.generate(maps.length, (i) => TeamMetric.fromMap(maps[i]));
  }

  Future<double?> getTeamMetric(String teamId, String eventId, String metricType) async {
    final db = await database.database;
    final maps = await db.query(
      'team_metrics',
      where: 'team_id = ? AND event_id = ? AND metric_type = ?',
      whereArgs: [teamId, eventId, metricType],
    );
    if (maps.isEmpty) return null;
    return TeamMetric.fromMap(maps.first).value;
  }

  // Bulk operations for synchronization
  Future<void> bulkInsertEvents(List<Event> events) async {
    final db = await database.database;
    Batch batch = db.batch();
    for (var event in events) {
      batch.insert('events', event.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
    }
    await batch.commit(noResult: true);
  }

  Future<void> bulkInsertTeams(List<Team> teams) async {
    final db = await database.database;
    Batch batch = db.batch();
    for (var team in teams) {
      batch.insert('teams', team.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
    }
    await batch.commit(noResult: true);
  }

  Future<void> bulkInsertMatches(List<Match> matches) async {
    final db = await database.database;
    Batch batch = db.batch();
    for (var match in matches) {
      batch.insert('matches', match.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
    }
    await batch.commit(noResult: true);
  }

  Future<void> bulkInsertMatchTeams(List<MatchTeam> matchTeams) async {
    final db = await database.database;
    Batch batch = db.batch();
    for (var matchTeam in matchTeams) {
      batch.insert('match_teams', matchTeam.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
    }
    await batch.commit(noResult: true);
  }

  Future<void> bulkInsertMatchResults(List<MatchResult> results) async {
    final db = await database.database;
    Batch batch = db.batch();
    for (var result in results) {
      batch.insert('match_results', result.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
    }
    await batch.commit(noResult: true);
  }

  // Clear and reset database (for testing or fresh sync)
  Future<void> clearDatabase() async {
    final db = await database.database;
    await db.execute('DELETE FROM team_metrics');
    await db.execute('DELETE FROM match_results');
    await db.execute('DELETE FROM match_teams');
    await db.execute('DELETE FROM matches');
    await db.execute('DELETE FROM teams');
    await db.execute('DELETE FROM events');
  }
}