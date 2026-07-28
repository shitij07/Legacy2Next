import { useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useProject } from '@/hooks/useProjects'
import { PaginationBar } from '@/features/analysis/components/explorer/PaginationBar'
import { ReportsHeader } from '../components/list/ReportsHeader'
import { ReportFilters } from '../components/list/ReportFilters'
import { ReportTable } from '../components/list/ReportTable'
import { GenerateReportDialog } from '../components/dialogs/GenerateReportDialog'
import { DeleteReportDialog } from '../components/dialogs/DeleteReportDialog'
import { useReports, useGenerateReport, useDeleteReport } from '../hooks'
import { ReportFormat, ReportStatus } from '../types'
import type { ReportSummary, ReportCreatePayload } from '../types'

const PAGE_SIZE = 20

export function ReportsListPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const pid = Number(projectId)

  const [page, setPage] = useState(1)
  const [formatFilter, setFormatFilter] = useState<ReportFormat | ''>('')
  const [statusFilter, setStatusFilter] = useState<ReportStatus | ''>('')
  const [generateOpen, setGenerateOpen] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<ReportSummary | null>(null)

  const params = {
    project_id: pid,
    page,
    size: PAGE_SIZE,
    ...(formatFilter && { format: formatFilter }),
    ...(statusFilter && { status: statusFilter }),
  }

  const { data: project, isLoading: projectLoading } = useProject(pid)
  const { data: reportsData, isLoading, isError, error, refetch } = useReports(params)
  const generateMutation = useGenerateReport(pid)
  const deleteMutation = useDeleteReport(pid, params)

  const handleGenerate = useCallback((data: ReportCreatePayload) => {
    generateMutation.mutate(data, {
      onSuccess: () => setGenerateOpen(false),
    })
  }, [generateMutation])

  const handleDelete = useCallback(() => {
    if (!deleteTarget) return
    deleteMutation.mutate(deleteTarget.id, {
      onSuccess: () => setDeleteTarget(null),
    })
  }, [deleteTarget, deleteMutation])

  if (projectLoading) {
    return (
      <div>
        <ReportsHeader onGenerate={() => setGenerateOpen(true)} />
        <LoadingState variant="table" />
      </div>
    )
  }

  return (
    <div>
      <ReportsHeader
        projectName={project?.name}
        onGenerate={() => setGenerateOpen(true)}
      />

      <div className="mb-4">
        <ReportFilters
          format={formatFilter}
          status={statusFilter}
          onFormatChange={(v) => { setFormatFilter(v); setPage(1) }}
          onStatusChange={(v) => { setStatusFilter(v); setPage(1) }}
        />
      </div>

      {isLoading ? (
        <LoadingState variant="table" />
      ) : isError ? (
        <ErrorState
          title="Failed to load reports"
          message={(error as Error)?.message}
          onRetry={() => refetch()}
        />
      ) : !reportsData || reportsData.items.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-border bg-white py-16">
          <p className="text-sm text-neutral-600">No reports yet.</p>
          <p className="mt-1 text-sm text-neutral-500">Generate your first report to get started.</p>
        </div>
      ) : (
        <>
          <ReportTable
            reports={reportsData.items}
            projectId={pid}
            onDelete={setDeleteTarget}
          />
          <div className="mt-4">
            <PaginationBar
              page={reportsData.page}
              size={reportsData.size}
              total={reportsData.total}
              pages={reportsData.pages}
              onPageChange={setPage}
            />
          </div>
        </>
      )}

      <GenerateReportDialog
        open={generateOpen}
        onOpenChange={setGenerateOpen}
        projectId={pid}
        onGenerate={handleGenerate}
        isGenerating={generateMutation.isPending}
      />

      <DeleteReportDialog
        title={deleteTarget?.title ?? ''}
        open={!!deleteTarget}
        onOpenChange={(open) => { if (!open) setDeleteTarget(null) }}
        onConfirm={handleDelete}
        isDeleting={deleteMutation.isPending}
      />
    </div>
  )
}
