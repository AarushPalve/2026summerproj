// Team types
export interface TeamMetric {
  team: number;
  matches_played: number;
  epa: number;
  opr: number;
  copr_totalPoints: number;
  copr_autoPoints: number;
  copr_teleopPoints: number;
  copr_foulPoints: number;
}

export interface TeamRanking extends TeamMetric {
  rank?: number;
}

// Match types
export interface MatchData {
  key: string;
  event_key: string;
  match_number: number;
  alliances: {
    red: {
      team_keys: string[];
      score: number;
    };
    blue: {
      team_keys: string[];
      score: number;
    };
  };
  score_breakdown?: {
    red: Record<string, number>;
    blue: Record<string, number>;
  };
  actual_time?: string;
  played_time_utc?: string;
}

// Prediction types
export interface PredictionResult {
  dnn_logit: number;
  dnn_prob: number;
  rf_prob: number | null;
  ensemble_prob: number;
  blue_win_prob: number;
}

export interface MatchPrediction extends PredictionResult {
  red_alliance: number[];
  blue_alliance: number[];
  predicted_winner: 'red' | 'blue';
  confidence: number;
}

// API Response types
export interface ApiResponse<T> {
  status: string;
  data?: T;
  message?: string;
  error?: string;
  count?: number;
}

// System types
export interface SystemInfo {
  teams_loaded: number;
  data_files: number;
  model_files: number;
  data_directory: string;
  models_directory: string;
}

// Stats types
export interface CalculationStats {
  teams: number;
  total_matches_played: number;
  avg_matches_per_team: number;
  epa_range: {
    min: number;
    max: number;
    mean: number;
    std: number;
  };
  opr_range: {
    min: number;
    max: number;
    mean: number;
    std: number;
  };
}

export interface DistributionStats {
  [key: string]: {
    mean: number;
    median: number;
    std: number;
    min: number;
    max: number;
    q25: number;
    q75: number;
  };
}

// Component types
export interface NavbarItem {
  name: string;
  path: string;
  icon: React.ReactNode;
}

// Chart types
export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
    borderWidth?: number;
  }[];
}
