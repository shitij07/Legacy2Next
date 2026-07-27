import { client } from './client'
import type {
  AnalysisListItem,
  Analysis,
  PaginatedResponse,
  DashboardResponse,
  AnalysisMetric,
  AnalysisTechnology,
  AnalysisWarning,
} from '@/lib/types'

export async function getUploadAnalyses(uploadId: number): Promise<PaginatedResponse<AnalysisListItem>> {
  return client.get(`analysis/upload/${uploadId}`).json()
}

export async function getAnalysisSummary(analysisId: number): Promise<Analysis> {
  return client.get(`analysis/${analysisId}`).json()
}

export async function getAnalysisDashboard(analysisId: number): Promise<DashboardResponse> {
  return client.get(`analysis/${analysisId}/dashboard`).json()
}

export async function getAnalysisMetrics(analysisId: number): Promise<AnalysisMetric[]> {
  return client.get(`analysis/${analysisId}/metrics`).json()
}

export async function getAnalysisTechnologies(analysisId: number): Promise<AnalysisTechnology[]> {
  return client.get(`analysis/${analysisId}/technologies`).json()
}

export async function getAnalysisWarnings(
  analysisId: number,
  page = 1,
  size = 20,
): Promise<PaginatedResponse<AnalysisWarning>> {
  return client
    .get(`analysis/${analysisId}/warnings`, { searchParams: { page, size } })
    .json()
}
