import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@/lib/queryKeys'
import { getProjects, getProject, createProject, deleteProject } from '@/services/projects'
import type { CreateProjectPayload } from '@/services/projects'
import type { PaginatedResponse, Project } from '@/lib/types'

export function useProjects(page = 1, size = 20) {
  return useQuery({
    queryKey: queryKeys.projects.list(page, size),
    queryFn: () => getProjects(page, size),
    placeholderData: (previousData) => previousData,
  })
}

export function useProject(id: number) {
  return useQuery({
    queryKey: queryKeys.projects.detail(id),
    queryFn: () => getProject(id),
    enabled: !!id,
  })
}

export function useCreateProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateProjectPayload) => createProject(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all })
    },
  })
}

export function useDeleteProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => deleteProject(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.projects.all })

      const previousQueries =
        queryClient.getQueriesData<PaginatedResponse<Project>>({
          queryKey: queryKeys.projects.all,
        })

      for (const [queryKey, data] of previousQueries) {
        if (data) {
          queryClient.setQueryData<PaginatedResponse<Project>>(queryKey, {
            ...data,
            items: data.items.filter((item) => item.id !== id),
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
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all })
    },
  })
}
