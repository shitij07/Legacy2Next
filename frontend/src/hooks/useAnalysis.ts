import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@/lib/queryKeys'
import {
  getAnalysisDashboard,
  getAnalysisMetrics,
  getAnalysisTechnologies,
  getAnalysisWarnings,
  getAnalysisSummary,
} from '@/services/analysis'

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

export function useAnalysisWarnings(analysisId: number, page = 1, size = 20) {
  return useQuery({
    queryKey: queryKeys.analysis.warnings(analysisId, { page, size }),
    queryFn: () => getAnalysisWarnings(analysisId, page, size),
    enabled: !!analysisId,
  })
}
