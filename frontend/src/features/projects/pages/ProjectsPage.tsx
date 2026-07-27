import { useState } from 'react'
import { Plus } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorState } from '@/components/shared/ErrorState'
import { ConfirmDialog } from '@/components/shared/ConfirmDialog'
import { Pagination } from '@/components/ui/pagination'
import {
  PaginationContent,
  PaginationItem,
  PaginationPrevious,
  PaginationNext,
  PaginationLink,
} from '@/components/ui/pagination'
import { useProjects, useCreateProject, useDeleteProject } from '@/hooks/useProjects'
import type { Project } from '@/lib/types'
import { PAGINATION } from '@/lib/constants'
import { ProjectList } from '../components/ProjectList'
import { CreateProjectDialog } from '../components/CreateProjectDialog'

export function ProjectsPage() {
  const [page, setPage] = useState(1)
  const [createOpen, setCreateOpen] = useState(false)
  const [deleting, setDeleting] = useState<Project | null>(null)

  const size = PAGINATION.DEFAULT_PAGE_SIZE_LIST
  const { data, isLoading, isError, error } = useProjects(page, size)
  const createMutation = useCreateProject()
  const deleteMutation = useDeleteProject()

  const handleCreate = async (formData: { name: string; description?: string }) => {
    await createMutation.mutateAsync(formData)
    setCreateOpen(false)
  }

  const handleDelete = async () => {
    if (!deleting) return
    await deleteMutation.mutateAsync(deleting.id)
    setDeleting(null)
  }

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Projects" description="Manage your legacy codebase analysis projects." />
        <LoadingState variant="card" count={6} />
      </div>
    )
  }

  if (isError) {
    return (
      <div>
        <PageHeader title="Projects" description="Manage your legacy codebase analysis projects." />
        <ErrorState
          title="Failed to load projects"
          message={error?.message ?? 'An unexpected error occurred.'}
          onRetry={() => setPage(1)}
        />
      </div>
    )
  }

  const projects = data?.items ?? []
  const totalPages = data?.pages ?? 0
  const total = data?.total ?? 0

  return (
    <div>
      <PageHeader
        title="Projects"
        description="Manage your legacy codebase analysis projects."
        actions={
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4" aria-hidden="true" />
            New Project
          </Button>
        }
      />

      {projects.length === 0 ? (
        <EmptyState
          title="No projects yet"
          description="Create your first project to start analysing a legacy codebase."
          action={{ label: 'Create Project', onClick: () => setCreateOpen(true) }}
        />
      ) : (
        <>
          <ProjectList projects={projects} onDelete={(p) => setDeleting(p)} />

          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between">
              <p className="text-sm text-neutral-600">
                Showing {(page - 1) * size + 1}–{Math.min(page * size, total)} of {total}
              </p>
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      aria-disabled={page <= 1}
                      className={page <= 1 ? 'pointer-events-none opacity-40' : ''}
                    />
                  </PaginationItem>
                  {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                    let pageNum: number
                    if (totalPages <= 7) {
                      pageNum = i + 1
                    } else if (page <= 4) {
                      pageNum = i + 1
                    } else if (page >= totalPages - 3) {
                      pageNum = totalPages - 6 + i
                    } else {
                      pageNum = page - 3 + i
                    }
                    return (
                      <PaginationItem key={pageNum}>
                        <PaginationLink
                          isActive={pageNum === page}
                          onClick={() => setPage(pageNum)}
                        >
                          {pageNum}
                        </PaginationLink>
                      </PaginationItem>
                    )
                  })}
                  <PaginationItem>
                    <PaginationNext
                      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                      aria-disabled={page >= totalPages}
                      className={page >= totalPages ? 'pointer-events-none opacity-40' : ''}
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          )}
        </>
      )}

      <CreateProjectDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        onSubmit={handleCreate}
      />

      <ConfirmDialog
        open={!!deleting}
        onOpenChange={(open) => { if (!open) setDeleting(null) }}
        title="Delete project?"
        description={`This will permanently delete "${deleting?.name}" and all associated uploads and analyses. This action cannot be undone.`}
        confirmLabel="Delete"
        variant="danger"
        isLoading={deleteMutation.isPending}
        onConfirm={handleDelete}
      />
    </div>
  )
}
