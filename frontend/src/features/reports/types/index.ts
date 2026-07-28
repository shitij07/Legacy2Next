export enum ReportFormat {
  MARKDOWN = 'markdown',
  JSON = 'json',
}

export enum ReportStatus {
  GENERATING = 'generating',
  READY = 'ready',
  FAILED = 'failed',
}

export interface ReportSummary {
  id: number
  project_id: number
  analysis_id: number
  title: string
  format: ReportFormat
  status: ReportStatus
  created_at: string
}

export interface ReportResponse {
  id: number
  project_id: number
  analysis_id: number
  user_id: number
  title: string
  format: ReportFormat
  status: ReportStatus
  content: string | null
  file_path: string | null
  created_at: string
  updated_at: string | null
}

export interface ReportListResponse {
  items: ReportSummary[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ReportCreatePayload {
  project_id: number
  analysis_id: number
  format?: ReportFormat
  title?: string
}

export interface ReportListParams {
  project_id: number
  analysis_id?: number
  status?: ReportStatus
  format?: ReportFormat
  page?: number
  size?: number
  sort_by?: string
  sort_dir?: string
}
