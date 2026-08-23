export type Prediction = { date: string; aqi: number; risk: string };

export type PredictResponse = {
  city: string;
  generated_at: string;
  selection_mode: string;
  model: Record<string, string>;
  available_models?: string[];
  supports_model_override?: boolean;
  predictions: Prediction[];
};

export type MetricRow = { model: string; rmse: number; mae: number; r2: number };

export type OverallRow = {
  model: string;
  composite_rank_score: number;
  avg_rmse: number;
  avg_mae: number;
  avg_r2: number;
};

export type MetricsResponse = {
  city: string;
  evaluated_at: string;
  metrics: Record<string, MetricRow[]>;
  overall_winner?: OverallRow;
  overall_leaderboard?: OverallRow[];
};

export type PipelineRun = {
  pipeline_name: string;
  status: string;
  run_at: string;
  details?: Record<string, unknown>;
};

export type PipelineResponse = {
  recent_runs: PipelineRun[];
  github_actions?: { name: string; status: string; conclusion: string; html_url: string }[];
};

export type RegistryResponse = {
  city: string;
  registered_at: string;
  champion_model: Record<string, string>;
  available_models: string[];
  supports_model_override?: boolean;
  overall_winner?: OverallRow;
  overall_leaderboard?: OverallRow[];
  feature_columns: string[];
  gridfs_model_id?: string;
  metrics: Record<string, MetricRow[]>;
};

export type QualityResponse = {
  city: string;
  audited_at: string;
  row_count: number;
  duplicate_rows: number;
  aqi_out_of_range_rows: number;
  leakage_risk_hint: boolean;
  status: string;
  daily_training_rows?: number;
};

export type Horizon = "day_1" | "day_2" | "day_3";
