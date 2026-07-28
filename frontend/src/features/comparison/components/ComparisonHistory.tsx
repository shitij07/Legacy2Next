import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Trash2, Eye } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationPrevious,
  PaginationNext,
} from '@/components/ui/pagination'
import { Section } from '@/components/shared/Section'
import { useComparisonHistory, useDeleteComparison } from '../hooks'
import { ConfirmDialog } from '@/components/shared/ConfirmDialog'
import type { ComparisonSummary } from '../types'

interface ComparisonHistoryProps {
  projectId: number
}

export function ComparisonHistory({ projectId }: ComparisonHistoryProps) {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)
  const size = 10

  const params = { project_id: projectId, page, size }
  const { data, isLoading, isError } = useComparisonHistory(params)
  const deleteMutation = useDeleteComparison(projectId, params)

  const [deleteTarget, setDeleteTarget] = useState<ComparisonSummary | null>(null)

  const handleDelete = () => {
    if (deleteTarget) {
      deleteMutation.mutate(deleteTarget.id)
      setDeleteTarget(null)
    }
  }

  if (isLoading) {
    return (
      <Section title="Comparison History">
        <p className="text-sm text-neutral-500">Loading history...</p>
      </Section>
    )
  }

  if (isError) {
    return (
      <Section title="Comparison History">
        <p className="text-sm text-error">Failed to load comparison history.</p>
      </Section>
    )
  }

  const items = data?.items ?? []

  return (
    <Section
      title="Comparison History"
      description={data ? `${data.total} comparison${data.total !== 1 ? 's' : ''} total` : undefined}
    >
      {items.length === 0 ? (
        <p className="text-sm text-neutral-500">No comparisons yet. Select two analyses above to compare.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm" role="table">
            <thead>
              <tr className="border-b border-border bg-neutral-100">
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-neutral-600">ID</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-neutral-600">Analyses</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-neutral-600">Summary</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-neutral-600">Date</th>
                <th scope="col" className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-neutral-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {items.map((item) => (
                <tr key={item.id} className="bg-neutral-50 hover:bg-neutral-100">
                  <td className="whitespace-nowrap px-4 py-3 text-neutral-800">#{item.id}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-neutral-800">
                    A:{item.analysis_a_id} vs B:{item.analysis_b_id}
                  </td>
                  <td className="max-w-xs truncate px-4 py-3 text-neutral-600">
                    {item.summary ?? '-'}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-neutral-600">
                    {new Date(item.created_at).toLocaleDateString()}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-right">
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => navigate(`/projects/${projectId}/comparison/${item.id}`)}
                        title="View comparison"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => setDeleteTarget(item)}
                        title="Delete comparison"
                      >
                        <Trash2 className="h-4 w-4 text-error" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data && data.pages > 1 && (
        <Pagination className="mt-4">
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className={page <= 1 ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
              />
            </PaginationItem>
            <PaginationItem>
              <span className="px-4 text-sm text-neutral-600">
                Page {data.page} of {data.pages}
              </span>
            </PaginationItem>
            <PaginationItem>
              <PaginationNext
                onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                className={page >= data.pages ? 'pointer-events-none opacity-50' : 'cursor-pointer'}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}

      <ConfirmDialog
        open={deleteTarget !== null}
        onOpenChange={(open) => { if (!open) setDeleteTarget(null) }}
        onConfirm={handleDelete}
        title="Delete Comparison"
        description="Are you sure you want to delete this comparison? This action cannot be undone."
        confirmLabel="Delete"
        isLoading={deleteMutation.isPending}
      />
    </Section>
  )
}
