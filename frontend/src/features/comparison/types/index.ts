export interface MetricDiff {
  key: string
  a_value: number | string | null
  b_value: number | string | null
  abs_diff: number | null
  pct_diff: number | null
}

export interface MetricsComparison {
  loc: MetricDiff | null
  file_count: MetricDiff | null
  dependency_count: MetricDiff | null
  technology_count: MetricDiff | null
  warning_count: MetricDiff | null
}

export interface TechnologyComparison {
  added: Array<Record<string, unknown>>
  removed: Array<Record<string, unknown>>
  common: Array<Record<string, unknown>>
  version_changes: Array<Record<string, unknown>>
}

export interface DependencyComparison {
  added: Array<Record<string, unknown>>
  removed: Array<Record<string, unknown>>
  updated: Array<Record<string, unknown>>
}

export interface FileComparison {
  added: Array<Record<string, unknown>>
  removed: Array<Record<string, unknown>>
  modified: Array<Record<string, unknown>>
  total_a: number
  total_b: number
}

export interface WarningComparison {
  added: Array<Record<string, unknown>>
  resolved: Array<Record<string, unknown>>
  persistent: Array<Record<string, unknown>>
  delta: number
}

export interface ComparisonData {
  technologies: TechnologyComparison
  dependencies: DependencyComparison
  files: FileComparison
  warnings: WarningComparison
  metrics: MetricsComparison
}

export interface ComparisonResponse {
  id: number
  project_id: number
  analysis_a_id: number
  analysis_b_id: number
  summary: string | null
  comparison_data: ComparisonData | null
  created_at: string
}

export interface ComparisonSummary {
  id: number
  project_id: number
  analysis_a_id: number
  analysis_b_id: number
  summary: string | null
  created_at: string
}

export interface ComparisonListResponse {
  items: ComparisonSummary[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ComparisonCreatePayload {
  project_id: number
  analysis_a_id: number
  analysis_b_id: number
}

export interface ComparisonListParams {
  project_id: number
  page?: number
  size?: number
}
