// FRC Data Models
// Spec: 01_system_architecture.md Section 3

class Event {
  final String eventId;
  final String name;
  final String startDate;
  final String endDate;
  final String? location;
  final String? eventType;
  final int year;

  Event({
    required this.eventId,
    required this.name,
    required this.startDate,
    required this.endDate,
    this.location,
    this.eventType,
    required this.year,
  });

  Map<String, dynamic> toMap() {
    return {
      'event_id': eventId,
      'name': name,
      'start_date': startDate,
      'end_date': endDate,
      'location': location,
      'event_type': eventType,
      'year': year,
    };
  }

  factory Event.fromMap(Map<String, dynamic> map) {
    return Event(
      eventId: map['event_id'],
      name: map['name'],
      startDate: map['start_date'],
      endDate: map['end_date'],
      location: map['location'],
      eventType: map['event_type'],
      year: map['year'],
    );
  }
}

class Team {
  final String teamId;
  final String? name;
  final String? nickname;
  final int? rookieYear;
  final String? location;

  Team({
    required this.teamId,
    this.name,
    this.nickname,
    this.rookieYear,
    this.location,
  });

  Map<String, dynamic> toMap() {
    return {
      'team_id': teamId,
      'name': name,
      'nickname': nickname,
      'rookie_year': rookieYear,
      'location': location,
    };
  }

  factory Team.fromMap(Map<String, dynamic> map) {
    return Team(
      teamId: map['team_id'],
      name: map['name'],
      nickname: map['nickname'],
      rookieYear: map['rookie_year'],
      location: map['location'],
    );
  }
}

class Match {
  final String matchId;
  final String eventId;
  final int matchNumber;
  final int? setNumber;
  final String matchType; // 'qualification', 'playoff', 'practice'
  final String? scheduledTime;
  final String? actualTime;

  Match({
    required this.matchId,
    required this.eventId,
    required this.matchNumber,
    this.setNumber,
    required this.matchType,
    this.scheduledTime,
    this.actualTime,
  });

  Map<String, dynamic> toMap() {
    return {
      'match_id': matchId,
      'event_id': eventId,
      'match_number': matchNumber,
      'set_number': setNumber,
      'match_type': matchType,
      'scheduled_time': scheduledTime,
      'actual_time': actualTime,
    };
  }

  factory Match.fromMap(Map<String, dynamic> map) {
    return Match(
      matchId: map['match_id'],
      eventId: map['event_id'],
      matchNumber: map['match_number'],
      setNumber: map['set_number'],
      matchType: map['match_type'],
      scheduledTime: map['scheduled_time'],
      actualTime: map['actual_time'],
    );
  }
}

class MatchTeam {
  final String matchId;
  final String teamId;
  final String allianceColor; // 'red' or 'blue'
  final int position; // 1, 2, or 3
  final bool surrogate;
  final bool dq;

  MatchTeam({
    required this.matchId,
    required this.teamId,
    required this.allianceColor,
    required this.position,
    this.surrogate = false,
    this.dq = false,
  });

  Map<String, dynamic> toMap() {
    return {
      'match_id': matchId,
      'team_id': teamId,
      'alliance_color': allianceColor,
      'position': position,
      'surrogate': surrogate ? 1 : 0,
      'dq': dq ? 1 : 0,
    };
  }

  factory MatchTeam.fromMap(Map<String, dynamic> map) {
    return MatchTeam(
      matchId: map['match_id'],
      teamId: map['team_id'],
      allianceColor: map['alliance_color'],
      position: map['position'],
      surrogate: map['surrogate'] == 1,
      dq: map['dq'] == 1,
    );
  }
}

class MatchResult {
  final String matchId;
  final int? redScore;
  final int? blueScore;
  final int redRp;
  final int blueRp;
  final String? winningAlliance;
  final String status; // 'scheduled', 'in_progress', 'completed', 'postponed'

  MatchResult({
    required this.matchId,
    this.redScore,
    this.blueScore,
    this.redRp = 0,
    this.blueRp = 0,
    this.winningAlliance,
    this.status = 'scheduled',
  });

  Map<String, dynamic> toMap() {
    return {
      'match_id': matchId,
      'red_score': redScore,
      'blue_score': blueScore,
      'red_rp': redRp,
      'blue_rp': blueRp,
      'winning_alliance': winningAlliance,
      'status': status,
    };
  }

  factory MatchResult.fromMap(Map<String, dynamic> map) {
    return MatchResult(
      matchId: map['match_id'],
      redScore: map['red_score'],
      blueScore: map['blue_score'],
      redRp: map['red_rp'],
      blueRp: map['blue_rp'],
      winningAlliance: map['winning_alliance'],
      status: map['status'],
    );
  }
}

class TeamMetric {
  final String teamId;
  final String eventId;
  final String metricType; // 'opr', 'epa', 'ccwm', 'dpr', etc.
  final double value;
  final String lastUpdated;

  TeamMetric({
    required this.teamId,
    required this.eventId,
    required this.metricType,
    required this.value,
    required this.lastUpdated,
  });

  Map<String, dynamic> toMap() {
    return {
      'team_id': teamId,
      'event_id': eventId,
      'metric_type': metricType,
      'value': value,
      'last_updated': lastUpdated,
    };
  }

  factory TeamMetric.fromMap(Map<String, dynamic> map) {
    return TeamMetric(
      teamId: map['team_id'],
      eventId: map['event_id'],
      metricType: map['metric_type'],
      value: map['value'],
      lastUpdated: map['last_updated'],
    );
  }
}