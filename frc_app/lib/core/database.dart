// Core Database Layer - SQLite Implementation
// Spec: 01_system_architecture.md Section 2.2

import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class FRCDatabase {
  static final FRCDatabase _instance = FRCDatabase._internal();
  factory FRCDatabase() => _instance;

  static Database? _database;

  FRCDatabase._internal();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    // Get database path
    String path = join(await getDatabasesPath(), 'frc_strategy.db');

    // Open/create database
    return await openDatabase(
      path,
      version: 1,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    // Create Events table
    await db.execute('''
      CREATE TABLE events (
        event_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        location TEXT,
        event_type TEXT,
        year INTEGER NOT NULL
      )
    ''');

    // Create Teams table
    await db.execute('''
      CREATE TABLE teams (
        team_id TEXT PRIMARY KEY,
        name TEXT,
        nickname TEXT,
        rookie_year INTEGER,
        location TEXT
      )
    ''');

    // Create Matches table
    await db.execute('''
      CREATE TABLE matches (
        match_id TEXT PRIMARY KEY,
        event_id TEXT NOT NULL,
        match_number INTEGER NOT NULL,
        set_number INTEGER,
        match_type TEXT NOT NULL,
        scheduled_time TEXT,
        actual_time TEXT,
        FOREIGN KEY (event_id) REFERENCES events(event_id)
      )
    ''');

    // Create Match Teams (Alliance assignments)
    await db.execute('''
      CREATE TABLE match_teams (
        match_id TEXT NOT NULL,
        team_id TEXT NOT NULL,
        alliance_color TEXT NOT NULL, -- 'red' or 'blue'
        position INTEGER NOT NULL, -- 1, 2, or 3
        surrogate BOOLEAN DEFAULT 0,
        dq BOOLEAN DEFAULT 0,
        PRIMARY KEY (match_id, team_id, alliance_color),
        FOREIGN KEY (match_id) REFERENCES matches(match_id),
        FOREIGN KEY (team_id) REFERENCES teams(team_id)
      )
    ''');

    // Create Match Results
    await db.execute('''
      CREATE TABLE match_results (
        match_id TEXT PRIMARY KEY,
        red_score INTEGER,
        blue_score INTEGER,
        red_rp INTEGER DEFAULT 0,
        blue_rp INTEGER DEFAULT 0,
        winning_alliance TEXT,
        status TEXT DEFAULT 'scheduled',
        FOREIGN KEY (match_id) REFERENCES matches(match_id)
      )
    ''');

    // Create Team Performance Metrics (for EPA, OPR calculations)
    await db.execute('''
      CREATE TABLE team_metrics (
        team_id TEXT NOT NULL,
        event_id TEXT NOT NULL,
        metric_type TEXT NOT NULL, -- 'opr', 'epa', 'ccwm', etc.
        value REAL NOT NULL,
        last_updated TEXT NOT NULL,
        PRIMARY KEY (team_id, event_id, metric_type),
        FOREIGN KEY (team_id) REFERENCES teams(team_id),
        FOREIGN KEY (event_id) REFERENCES events(event_id)
      )
    ''');

    // Create composite indexes for performance
    await db.execute('CREATE INDEX idx_matches_event ON matches(event_id, match_type, match_number)');
    await db.execute('CREATE INDEX idx_match_teams_alliance ON match_teams(match_id, alliance_color, position)');
    await db.execute('CREATE INDEX idx_team_metrics_event ON team_metrics(event_id, metric_type, value DESC)');
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    // Handle database migrations
    if (oldVersion < 2) {
      // Future migration logic
    }
  }

  // Transaction wrapper for atomic operations
  Future<void> runInTransaction(Function(Database) action) async {
    final db = await database;
    await db.transaction((txn) async {
      await action(txn);
    });
  }

  // Close database
  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
    }
  }
}