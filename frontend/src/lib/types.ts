export interface User {
  id: number
  email: string
  name: string
}

export interface Project {
  id: number
  name: string
  description: string | null
  language: string
  framework: string
  file_count: number
  status: string
  created_at: string
  updated_at: string
}

export interface Upload {
  id: number
  project_id: number
  original_name: string
  file_size: number
  mime_type: string
  extension: string
  status: string
  created_at: string
}

export interface AnalysisListItem {
  id: number
  upload_id: number
  status: string
  error_detail: string | null
  created_at: string
  completed_at: string | null
}

export interface Analysis extends AnalysisListItem {
  duration_ms: number | null
  file_count: number
  technology_count: number
  dependency_count: number
  metric_count: number
  warning_count: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface DashboardGeneral {
  analysis_id: number
  upload_id: number
  status: string
  error_detail: string | null
  created_at: string
  completed_at: string | null
  duration_ms: number | null
}

export interface LanguageCount {
  language: string
  count: number
}

export interface ExtensionCount {
  extension: string
  count: number
}

export interface DirectorySize {
  relative_path: string
  file_size: number
}

export interface DashboardFiles {
  total_files: number
  total_directories: number
  language_distribution: LanguageCount[]
  extension_distribution: ExtensionCount[]
  largest_directories: DirectorySize[]
}

export interface CategoryCount {
  category: string
  count: number
}

export interface ConfidenceCount {
  confidence: string
  count: number
}

export interface DashboardTechnologies {
  total_technologies: number
  category_distribution: CategoryCount[]
  confidence_distribution: ConfidenceCount[]
  primary_frameworks: string[]
}

export interface EcosystemBreakdown {
  ecosystem: string
  count: number
}

export interface TopPackage {
  name: string
  version: string | null
  ecosystem: string | null
}

export interface DashboardDependencies {
  total_dependencies: number
  direct_count: number
  transitive_count: number
  ecosystem_breakdown: EcosystemBreakdown[]
  top_packages: TopPackage[]
}

export interface DetectorCount {
  detector_name: string
  count: number
}

export interface DashboardWarnings {
  total_warnings: number
  detector_breakdown: DetectorCount[]
}

export interface DashboardMetrics {
  total_metrics: number
  project_total_files: number | null
  project_total_file_size: number | null
  language_count: number | null
  primary_language: string | null
  framework_count: number | null
  dependency_count: number | null
  manifest_count: number | null
}

export interface DashboardResponse {
  general: DashboardGeneral
  files: DashboardFiles
  technologies: DashboardTechnologies
  dependencies: DashboardDependencies
  warnings: DashboardWarnings
  metrics: DashboardMetrics
}

export interface AnalysisMetric {
  id: number
  key: string
  value: number | string | null
}

export interface AnalysisTechnology {
  id: number
  name: string
  category: string
  evidence: string | null
  confidence: string
}

export interface AnalysisWarning {
  id: number
  detector_name: string
  message: string
  created_at: string
}
