import { useCallback, useState } from 'react'
import { useParams } from 'react-router-dom'
import { PageHeader } from '@/components/layout/PageHeader'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useProject } from '@/hooks/useProjects'
import { useCreateComparison } from '../hooks'
import { ComparisonSelectors } from '../components/ComparisonSelectors'
import { ComparisonDashboard } from '../components/ComparisonDashboard'
import { ComparisonHistory } from '../components/ComparisonHistory'
import type { ComparisonData } from '../types'

export function ComparisonPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const pid = Number(projectId)

  const { data: project, isLoading: projectLoading, isError: projectError } = useProject(pid)
  const createComparison = useCreateComparison(pid)

  const [result, setResult] = useState<{ summary: string | null; data: ComparisonData } | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleCompare = useCallback(
    (analysisAId: number, analysisBId: number) => {
      setError(null)
      createComparison.mutate(
        { project_id: pid, analysis_a_id: analysisAId, analysis_b_id: analysisBId },
        {
          onSuccess: (data) => {
            if (data.comparison_data) {
              setResult({ summary: data.summary, data: data.comparison_data })
            }
          },
          onError: (err) => {
            setError(err.message || 'Comparison failed')
          },
        },
      )
    },
    [pid, createComparison],
  )

  if (projectLoading) {
    return (
      <div>
        <PageHeader title="Loading..." />
        <LoadingState variant="page" />
      </div>
    )
  }

  if (projectError || !project) {
    return (
      <div>
        <PageHeader title="Project not found" />
        <ErrorState
          title="Failed to load project"
          message="The project could not be found or you do not have access."
        />
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title="Analysis Comparison"
        description={`Compare two analyses for ${project.name}`}
      />

      <div className="mt-6 space-y-8">
        <ComparisonSelectors
          projectId={pid}
          onCompare={handleCompare}
          isComparing={createComparison.isPending}
        />

        {error && (
          <div className="rounded-lg border border-error/30 bg-error/5 p-4 text-sm text-error">
            {error}
          </div>
        )}

        {createComparison.isPending && (
          <div className="flex items-center justify-center py-12">
            <LoadingState variant="page" />
          </div>
        )}

        {result && (
          <div>
            {result.summary && (
              <div className="mb-6 rounded-lg border border-border bg-neutral-50 p-4">
                <p className="text-sm font-medium text-neutral-700">Summary</p>
                <p className="mt-1 text-neutral-800">{result.summary}</p>
              </div>
            )}
            <ComparisonDashboard data={result.data} />
          </div>
        )}

        <ComparisonHistory projectId={pid} />
      </div>
    </div>
  )
}
