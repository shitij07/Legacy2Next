import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Trash2 } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { ConfirmDialog } from '@/components/shared/ConfirmDialog'
import { useComparison, useDeleteComparison } from '../hooks'
import { ComparisonDashboard } from '../components/ComparisonDashboard'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export function ComparisonDetailPage() {
  const { projectId, comparisonId } = useParams<{ projectId: string; comparisonId: string }>()
  const pid = Number(projectId)
  const cid = Number(comparisonId)
  const navigate = useNavigate()

  const { data, isLoading, isError, error } = useComparison(cid)
  const deleteMutation = useDeleteComparison(pid, { project_id: pid, page: 1, size: 10 })
  const [showDelete, setShowDelete] = useState(false)

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Loading comparison..." />
        <LoadingState variant="page" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div>
        <PageHeader title="Comparison not found" />
        <ErrorState
          title="Failed to load comparison"
          message={(error as Error)?.message || 'The comparison could not be found or you do not have access.'}
        />
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title="Comparison Result"
        description={`Analysis #${data.analysis_a_id} vs Analysis #${data.analysis_b_id}`}
        actions={
          <div className="flex gap-2">
            <Button variant="outline" asChild>
              <Link to={`/projects/${pid}/comparison`}>
                <ArrowLeft className="mr-1 h-4 w-4" />
                Back
              </Link>
            </Button>
            <Button variant="danger" size="icon" onClick={() => setShowDelete(true)} title="Delete comparison">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        }
      />

      <div className="mt-6 space-y-6">
        {data.summary && (
          <div className="rounded-lg border border-border bg-neutral-50 p-4">
            <p className="text-sm font-medium text-neutral-700">Summary</p>
            <p className="mt-1 text-neutral-800">{data.summary}</p>
          </div>
        )}

        {data.comparison_data ? (
          <ComparisonDashboard data={data.comparison_data} />
        ) : (
          <p className="text-sm text-neutral-500">No comparison data available.</p>
        )}

        <p className="text-xs text-neutral-400">
          Created: {new Date(data.created_at).toLocaleString()}
        </p>
      </div>

      <ConfirmDialog
        open={showDelete}
        onOpenChange={setShowDelete}
        onConfirm={() => {
          deleteMutation.mutate(cid, {
            onSuccess: () => navigate(`/projects/${pid}/comparison`),
          })
        }}
        title="Delete Comparison"
        description="Are you sure you want to delete this comparison? This action cannot be undone."
        confirmLabel="Delete"
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
