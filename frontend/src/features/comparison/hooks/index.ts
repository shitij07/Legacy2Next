import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { compareAnalyses, getComparison, getComparisonHistory, deleteComparison } from '../api'
import type { ComparisonCreatePayload, ComparisonListParams, ComparisonListResponse } from '../types'

const comparisonKey = (id: number) => ['comparison', id] as const
const comparisonsKey = (params: ComparisonListParams) => ['comparisons', params] as const

export function useComparison(comparisonId: number) {
  return useQuery({
    queryKey: comparisonKey(comparisonId),
    queryFn: () => getComparison(comparisonId),
    enabled: !!comparisonId,
  })
}

export function useComparisonHistory(params: ComparisonListParams) {
  return useQuery({
    queryKey: comparisonsKey(params),
    queryFn: () => getComparisonHistory(params),
    placeholderData: (prev) => prev,
  })
}

export function useCreateComparison(projectId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: ComparisonCreatePayload) => compareAnalyses(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comparisons'] })
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] })
      toast.success('Comparison completed successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to compare analyses')
    },
  })
}

export function useDeleteComparison(projectId: number, params: ComparisonListParams) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (comparisonId: number) => deleteComparison(comparisonId),
    onMutate: async (comparisonId) => {
      await queryClient.cancelQueries({ queryKey: comparisonsKey(params) })

      const previousData = queryClient.getQueryData<ComparisonListResponse>(comparisonsKey(params))

      if (previousData) {
        queryClient.setQueryData<ComparisonListResponse>(comparisonsKey(params), {
          ...previousData,
          items: previousData.items.filter((item) => item.id !== comparisonId),
          total: previousData.total - 1,
        })
      }

      return { previousData }
    },
    onError: (_err, _id, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(comparisonsKey(params), context.previousData)
      }
      toast.error('Failed to delete comparison')
    },
    onSuccess: () => {
      toast.success('Comparison deleted successfully')
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['comparisons'] })
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] })
    },
  })
}
