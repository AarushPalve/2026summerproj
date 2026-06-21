-- SQLite Database Schema for FRC Data Importer
-- Based on Spec 02: Data Importer & Local Storage Schema Lifecycle

-- Main tables for storing match and team data
CREATE TABLE IF NOT EXISTS events (
    event_key TEXT PRIMARY KEY,
    event_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    location TEXT
);

CREATE TABLE IF NOT EXISTS teams (
    team_key TEXT PRIMARY KEY,
    team_number INTEGER NOT NULL,
    team_name TEXT,
    rookie_year INTEGER,
    location TEXT
);

CREATE TABLE IF NOT EXISTS matches (
    match_key TEXT PRIMARY KEY,
    event_key TEXT NOT NULL,
    comp_level TEXT NOT NULL,
    match_number INTEGER NOT NULL,
    set_number INTEGER NOT NULL,
    played_index INTEGER,
    winning_alliance TEXT,
    actual_start_time TEXT,
    scheduled_start_time TEXT,
    FOREIGN KEY (event_key) REFERENCES events(event_key)
);

CREATE TABLE IF NOT EXISTS match_alliances (
    match_key TEXT NOT NULL,
    alliance_color TEXT NOT NULL,
    score INTEGER,
    rp INTEGER DEFAULT 0,
    PRIMARY KEY (match_key, alliance_color),
    FOREIGN KEY (match_key) REFERENCES matches(match_key)
);

CREATE TABLE IF NOT EXISTS match_alliance_teams (
    match_key TEXT NOT NULL,
    alliance_color TEXT NOT NULL,
    team_key TEXT NOT NULL,
    PRIMARY KEY (match_key, alliance_color, team_key),
    FOREIGN KEY (match_key, alliance_color) REFERENCES match_alliances(match_key, alliance_color),
    FOREIGN KEY (team_key) REFERENCES teams(team_key)
);

CREATE TABLE IF NOT EXISTS match_score_breakdown (
    match_key TEXT NOT NULL,
    alliance_color TEXT NOT NULL,
    total_points INTEGER,
    auto_points INTEGER,
    teleop_points INTEGER,
    foul_points INTEGER,
    rp INTEGER DEFAULT 0,
    PRIMARY KEY (match_key, alliance_color),
    FOREIGN KEY (match_key) REFERENCES matches(match_key)
);

-- Performance metrics tables for EPA, OPR, and cOPR calculations
CREATE TABLE IF NOT EXISTS team_performance_metrics (
    team_key TEXT PRIMARY KEY,
    epa REAL DEFAULT 0.0,
    opr REAL DEFAULT 0.0,
    copr_total_points REAL DEFAULT 0.0,
    copr_auto_points REAL DEFAULT 0.0,
    copr_teleop_points REAL DEFAULT 0.0,
    copr_foul_points REAL DEFAULT 0.0,
    last_updated TEXT,
    FOREIGN KEY (team_key) REFERENCES teams(team_key)
);

-- Historical performance tracking for delta updates
CREATE TABLE IF NOT EXISTS team_performance_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_key TEXT NOT NULL,
    match_key TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    epa_before REAL,
    epa_after REAL,
    opr_before REAL,
    opr_after REAL,
    copr_total_points_before REAL,
    copr_total_points_after REAL,
    copr_auto_points_before REAL,
    copr_auto_points_after REAL,
    copr_teleop_points_before REAL,
    copr_teleop_points_after REAL,
    copr_foul_points_before REAL,
    copr_foul_points_after REAL,
    FOREIGN KEY (team_key) REFERENCES teams(team_key),
    FOREIGN KEY (match_key) REFERENCES matches(match_key)
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_matches_event ON matches(event_key);
CREATE INDEX IF NOT EXISTS idx_matches_comp_level ON matches(comp_level);
CREATE INDEX IF NOT EXISTS idx_matches_played ON matches(played_index);
CREATE INDEX IF NOT EXISTS idx_match_alliances_match ON match_alliances(match_key);
CREATE INDEX IF NOT EXISTS idx_match_alliance_teams_team ON match_alliance_teams(team_key);
CREATE INDEX IF NOT EXISTS idx_team_performance_metrics ON team_performance_metrics(team_key);
CREATE INDEX IF NOT EXISTS idx_team_performance_history_team ON team_performance_history(team_key);
CREATE INDEX IF NOT EXISTS idx_team_performance_history_match ON team_performance_history(match_key);