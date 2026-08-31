export type Stage =
  | "idle"
  | "fetch"
  | "normalize"
  | "tokenize"
  | "chunk"
  | "map"
  | "reduce"
  | "complete"
  | "error";

export type Metrics = {
  transcript_tokens?: number;
  number_of_chunks?: number;
  map_calls?: number;
  reduce_input_tokens?: number;
  execution_time_seconds?: number;
};

export type PipelineResult = {
  video_id?: string;
  summary?: string;
  transcript?: string;
  metrics?: Metrics;
};

export type PipelineEvent = {
  stage?: Stage;
  status?: "running" | "complete" | "error";
  message?: string;
  current?: number;
  total?: number;
  result?: PipelineResult;
};

export type MapProgress = {
  current: number;
  total: number;
};

export type EvaluationResult = {
  coverage: number;
  faithfulness: number;
  conciseness: number;
  overall: number;
  reason: string;
};