import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@/lib/queryKeys'
import {
  getAnalysisDashboard,
  getAnalysisMetrics,
  getAnalysisTechnologies,
  getAnalysisWarnings,
  getAnalysisSummary,
  getAnalysisFiles,
  getAnalysisDependencies,
  getProjectAnalyses,
} from '@/services/analysis'
import type {
  AnalysisFilesParams,
  AnalysisDependenciesParams,
  AnalysisWarningsParams,
} from '@/lib/types'

export function useAnalysisDashboard(analysisId: number) {
  return useQuery({
    queryKey: queryKeys.analysis.dashboard(analysisId),
    queryFn: () => getAnalysisDashboard(analysisId),
    enabled: !!analysisId,
  })
}

export function useAnalysisSummary(analysisId: number) {
  return useQuery({
    queryKey: queryKeys.analysis.detail(analysisId),
    queryFn: () => getAnalysisSummary(analysisId),
    enabled: !!analysisId,
  })
}

export function useAnalysisMetrics(analysisId: number) {
  return useQuery({
    queryKey: queryKeys.analysis.metrics(analysisId),
    queryFn: () => getAnalysisMetrics(analysisId),
    enabled: !!analysisId,
  })
}

export function useAnalysisTechnologies(analysisId: number) {
  return useQuery({
    queryKey: queryKeys.analysis.technologies(analysisId),
    queryFn: () => getAnalysisTechnologies(analysisId),
    enabled: !!analysisId,
  })
}

export function useAnalysisWarnings(
  analysisId: number,
  params: AnalysisWarningsParams = {},
) {
  return useQuery({
    queryKey: queryKeys.analysis.warnings(analysisId, params),
    queryFn: () => getAnalysisWarnings(analysisId, params),
    enabled: !!analysisId,
    placeholderData: (prev) => prev,
  })
}

export function useAnalysisFiles(
  analysisId: number,
  params: AnalysisFilesParams = {},
) {
  return useQuery({
    queryKey: queryKeys.analysis.files(analysisId, params),
    queryFn: () => getAnalysisFiles(analysisId, params),
    enabled: !!analysisId,
    placeholderData: (prev) => prev,
  })
}

export function useAnalysisDependencies(
  analysisId: number,
  params: AnalysisDependenciesParams = {},
) {
  return useQuery({
    queryKey: queryKeys.analysis.dependencies(analysisId, params),
    queryFn: () => getAnalysisDependencies(analysisId, params),
    enabled: !!analysisId,
    placeholderData: (prev) => prev,
  })
}

export function useProjectAnalyses(
  projectId: number,
  page = 1,
  size = 100,
) {
  return useQuery({
    queryKey: ['projects', projectId, 'analyses', { page, size }] as const,
    queryFn: () => getProjectAnalyses(projectId, page, size),
    enabled: !!projectId,
  })
}
