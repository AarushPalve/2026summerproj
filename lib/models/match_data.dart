class MatchData {
  final String matchKey;
  final String compLevel;
  final int matchNumber;
  final int setNumber;
  final int playedIndex;
  final String winningAlliance;
  final Map<String, AllianceData> alliances;
  final Map<String, ScoreBreakdown> scoreBreakdown;

  MatchData({
    required this.matchKey,
    required this.compLevel,
    required this.matchNumber,
    required this.setNumber,
    required this.playedIndex,
    required this.winningAlliance,
    required this.alliances,
    required this.scoreBreakdown,
  });

  factory MatchData.fromJson(Map<String, dynamic> json) {
    return MatchData(
      matchKey: json['match_key'] ?? '',
      compLevel: json['comp_level'] ?? '',
      matchNumber: json['match_number'] ?? 0,
      setNumber: json['set_number'] ?? 1,
      playedIndex: json['played_index'] ?? 0,
      winningAlliance: json['winning_alliance'] ?? '',
      alliances: _parseAlliances(json['alliances'] ?? {}),
      scoreBreakdown: _parseScoreBreakdown(json['score_breakdown'] ?? {}),
    );
  }

  static Map<String, AllianceData> _parseAlliances(Map<String, dynamic> alliancesJson) {
    final alliances = <String, AllianceData>{};
    alliancesJson.forEach((color, data) {
      alliances[color] = AllianceData.fromJson(data);
    });
    return alliances;
  }

  static Map<String, ScoreBreakdown> _parseScoreBreakdown(Map<String, dynamic> breakdownJson) {
    final breakdown = <String, ScoreBreakdown>{};
    breakdownJson.forEach((color, data) {
      breakdown[color] = ScoreBreakdown.fromJson(data);
    });
    return breakdown;
  }
}

class AllianceData {
  final int score;
  final List<String> teamKeys;

  AllianceData({required this.score, required this.teamKeys});

  factory AllianceData.fromJson(Map<String, dynamic> json) {
    return AllianceData(
      score: json['score'] ?? 0,
      teamKeys: List<String>.from(json['team_keys'] ?? []),
    );
  }
}

class ScoreBreakdown {
  final int totalPoints;
  final int autoPoints;
  final int teleopPoints;
  final int foulPoints;
  final int rp;

  ScoreBreakdown({
    required this.totalPoints,
    required this.autoPoints,
    required this.teleopPoints,
    required this.foulPoints,
    required this.rp,
  });

  factory ScoreBreakdown.fromJson(Map<String, dynamic> json) {
    return ScoreBreakdown(
      totalPoints: json['totalPoints'] ?? 0,
      autoPoints: json['autoPoints'] ?? 0,
      teleopPoints: json['teleopPoints'] ?? 0,
      foulPoints: json['foulPoints'] ?? 0,
      rp: json['rp'] ?? 0,
    );
  }
}