import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { queryKeys } from '@/lib/queryKeys'
import { getUploads, uploadFile, deleteUpload } from '@/services/upload'
import type { PaginatedResponse, Upload } from '@/lib/types'

const uploadListPrefix = (projectId: number) => ['projects', projectId, 'uploads'] as const

export function useUploads(projectId: number, page = 1, size = 20) {
  return useQuery({
    queryKey: queryKeys.uploads.byProject(projectId, page, size),
    queryFn: () => getUploads(projectId, page, size),
    placeholderData: (previousData) => previousData,
    refetchInterval: 10_000,
  })
}

export function useUploadFile(projectId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (file: File) => uploadFile(projectId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: uploadListPrefix(projectId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(projectId) })
      toast.success('File uploaded successfully')
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to upload file')
    },
  })
}

export function useDeleteUpload(projectId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (uploadId: number) => deleteUpload(uploadId),
    onMutate: async (uploadId) => {
      await queryClient.cancelQueries({
        queryKey: uploadListPrefix(projectId),
      })

      const previousQueries = queryClient.getQueriesData<PaginatedResponse<Upload>>({
        queryKey: uploadListPrefix(projectId),
      })

      for (const [queryKey, data] of previousQueries) {
        if (data) {
          queryClient.setQueryData<PaginatedResponse<Upload>>(queryKey, {
            ...data,
            items: data.items.filter((item) => item.id !== uploadId),
            total: data.total - 1,
          })
        }
      }

      return { previousQueries }
    },
    onError: (_err, _id, context) => {
      if (context?.previousQueries) {
        for (const [queryKey, data] of context.previousQueries) {
          if (data) {
            queryClient.setQueryData(queryKey, data)
          }
        }
      }
      toast.error('Failed to delete upload')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.detail(projectId) })
      toast.success('Upload deleted successfully')
    },
    onSettled: () => {
      queryClient.invalidateQueries({
        queryKey: uploadListPrefix(projectId),
      })
    },
  })
}
