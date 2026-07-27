import { useQueries } from '@tanstack/react-query'
import { queryKeys } from '@/lib/queryKeys'
import { getUploadAnalyses } from '@/services/analysis'
import type { AnalysisListItem, PaginatedResponse } from '@/lib/types'

export type UploadProcessingState =
  | { type: 'uploaded' }
  | { type: 'analysing'; analysis: AnalysisListItem }
  | { type: 'completed'; analysis: AnalysisListItem }
  | { type: 'completed_with_errors'; analysis: AnalysisListItem }
  | { type: 'failed'; analysis: AnalysisListItem }

function deriveState(analyses: AnalysisListItem[]): UploadProcessingState {
  if (analyses.length === 0) {
    return { type: 'uploaded' }
  }

  const latest = analyses[0]

  if (latest.status === 'COMPLETED') {
    return { type: 'completed', analysis: latest }
  }
  if (latest.status === 'COMPLETED_WITH_ERRORS') {
    return { type: 'completed_with_errors', analysis: latest }
  }
  if (latest.status === 'FAILED') {
    return { type: 'failed', analysis: latest }
  }

  return { type: 'analysing', analysis: latest }
}

function isTerminal(state: UploadProcessingState): boolean {
  return state.type !== 'analysing' && state.type !== 'uploaded'
}

export function useUploadAnalysisStatuses(uploadIds: number[]): Record<number, UploadProcessingState> {
  const results = useQueries({
    queries: uploadIds.map((uploadId) => ({
      queryKey: queryKeys.analysis.byUpload(uploadId),
      queryFn: () => getUploadAnalyses(uploadId),
      refetchInterval(query) {
        const data = query.state.data as PaginatedResponse<AnalysisListItem> | undefined
        if (!data || data.items.length === 0) return 5000
        const state = deriveState(data.items)
        return isTerminal(state) ? false : 5000
      },
      staleTime: 0,
    })),
  })

  const statuses: Record<number, UploadProcessingState> = {}
  for (let i = 0; i < uploadIds.length; i++) {
    const data = results[i]?.data
    statuses[uploadIds[i]] = data ? deriveState(data.items) : { type: 'uploaded' }
  }

  return statuses
}
