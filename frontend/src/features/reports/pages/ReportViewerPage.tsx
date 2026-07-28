import { useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useReport, useDeleteReport } from '../hooks'
import { ReportStatusBadge } from '../components/common/ReportStatusBadge'
import { ReportFormatBadge } from '../components/common/ReportFormatBadge'
import { MarkdownReport } from '../components/viewer/MarkdownReport'
import { JsonReport } from '../components/viewer/JsonReport'
import { ReportActions } from '../components/viewer/ReportActions'
import { DeleteReportDialog } from '../components/dialogs/DeleteReportDialog'
import { ReportFormat, ReportStatus } from '../types'

export function ReportViewerPage() {
  const { projectId, reportId } = useParams<{ projectId: string; reportId: string }>()
  const navigate = useNavigate()
  const pid = Number(projectId)
  const rid = Number(reportId)

  const [deleteOpen, setDeleteOpen] = useState(false)

  const { data: report, isLoading, isError, error, refetch } = useReport(rid)
  const deleteMutation = useDeleteReport(pid, { project_id: pid })

  const handleDelete = useCallback(() => {
    deleteMutation.mutate(rid, {
      onSuccess: () => navigate(`/projects/${pid}/reports`),
    })
  }, [rid, pid, deleteMutation, navigate])

  if (isLoading) {
    return (
      <div>
        <div className="mb-6">
          <h1 className="text-xl font-semibold text-neutral-900">Loading report...</h1>
        </div>
        <LoadingState variant="page" />
      </div>
    )
  }

  if (isError || !report) {
    return (
      <div>
        <h1 className="mb-6 text-xl font-semibold text-neutral-900">Report not found</h1>
        <ErrorState
          title="Failed to load report"
          message={(error as Error)?.message}
          onRetry={() => refetch()}
        />
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold text-neutral-900">{report.title}</h1>
            <div className="mt-2 flex items-center gap-3">
              <ReportFormatBadge format={report.format} />
              <ReportStatusBadge status={report.status} />
              <span className="text-sm text-neutral-600">
                {new Date(report.created_at).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
        <div className="mt-4">
          <ReportActions
            title={report.title}
            content={report.content ?? ''}
            reportId={rid}
            projectId={pid}
            onDelete={() => setDeleteOpen(true)}
            format={report.format}
          />
        </div>
      </div>

      {report.status === ReportStatus.GENERATING && (
        <div className="flex items-center gap-2 rounded-lg border border-border bg-neutral-50 p-4">
          <LoadingState variant="text" count={1} />
          <span className="text-sm text-neutral-600">Report is being generated...</span>
        </div>
      )}

      {report.status === ReportStatus.FAILED && (
        <ErrorState
          title="Report generation failed"
          message="The report could not be generated. Please try again."
        />
      )}

      {report.status === ReportStatus.READY && report.content && (
        <>
          {report.format === ReportFormat.MARKDOWN && (
            <MarkdownReport content={report.content} />
          )}
          {report.format === ReportFormat.JSON && (
            <JsonReport content={report.content} />
          )}
        </>
      )}

      {report.status === ReportStatus.READY && !report.content && (
        <ErrorState
          title="Empty report"
          message="This report has no content."
        />
      )}

      <DeleteReportDialog
        title={report.title}
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        onConfirm={handleDelete}
        isDeleting={deleteMutation.isPending}
      />
    </div>
  )
}
