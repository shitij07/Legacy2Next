import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { generateReport, getReports, getReport, deleteReport } from '../api'
import type { ReportCreatePayload, ReportListParams, ReportListResponse } from '../types'

const reportsKey = (params: ReportListParams) => ['reports', params] as const
const reportKey = (id: number) => ['reports', id] as const

export function useReports(params: ReportListParams) {
  return useQuery({
    queryKey: reportsKey(params),
    queryFn: () => getReports(params),
    placeholderData: (prev) => prev,
  })
}

export function useReport(reportId: number) {
  return useQuery({
    queryKey: reportKey(reportId),
    queryFn: () => getReport(reportId),
    enabled: !!reportId,
  })
}

export function useGenerateReport(projectId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: ReportCreatePayload) => generateReport(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] })
      toast.success('Report generated successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to generate report')
    },
  })
}

export function useDeleteReport(projectId: number, params: ReportListParams) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (reportId: number) => deleteReport(reportId),
    onMutate: async (reportId) => {
      await queryClient.cancelQueries({ queryKey: reportsKey(params) })

      const previousData = queryClient.getQueryData<ReportListResponse>(reportsKey(params))

      if (previousData) {
        queryClient.setQueryData<ReportListResponse>(reportsKey(params), {
          ...previousData,
          items: previousData.items.filter((item) => item.id !== reportId),
          total: previousData.total - 1,
        })
      }

      return { previousData }
    },
    onError: (_err, _id, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(reportsKey(params), context.previousData)
      }
      toast.error('Failed to delete report')
    },
    onSuccess: () => {
      toast.success('Report deleted successfully')
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] })
    },
  })
}
