import { client } from './client'
import type {
  AnalysisListItem,
  Analysis,
  PaginatedResponse,
  DashboardResponse,
  AnalysisMetric,
  AnalysisTechnology,
  AnalysisWarning,
  AnalysisFile,
  AnalysisDependency,
  AnalysisFilesParams,
  AnalysisDependenciesParams,
  AnalysisWarningsParams,
} from '@/lib/types'

function cleanParams(params: object): Record<string, string> {
  const cleaned: Record<string, string> = {}
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      cleaned[key] = String(value)
    }
  }
  return cleaned
}

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
  params: AnalysisWarningsParams = {},
): Promise<PaginatedResponse<AnalysisWarning>> {
  return client
    .get(`analysis/${analysisId}/warnings`, { searchParams: cleanParams(params) })
    .json()
}

export async function getAnalysisFiles(
  analysisId: number,
  params: AnalysisFilesParams = {},
): Promise<PaginatedResponse<AnalysisFile>> {
  return client
    .get(`analysis/${analysisId}/files`, { searchParams: cleanParams(params) })
    .json()
}

export async function getAnalysisDependencies(
  analysisId: number,
  params: AnalysisDependenciesParams = {},
): Promise<PaginatedResponse<AnalysisDependency>> {
  return client
    .get(`analysis/${analysisId}/dependencies`, { searchParams: cleanParams(params) })
    .json()
}
