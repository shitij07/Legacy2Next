import { useNavigate } from 'react-router-dom'
import { Trash2, Eye } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ReportStatusBadge } from '../common/ReportStatusBadge'
import { ReportFormatBadge } from '../common/ReportFormatBadge'
import type { ReportSummary } from '../../types'

interface ReportTableProps {
  reports: ReportSummary[]
  projectId: number
  onDelete: (report: ReportSummary) => void
}

export function ReportTable({ reports, projectId, onDelete }: ReportTableProps) {
  const navigate = useNavigate()

  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm" role="table" aria-label="Reports list">
        <thead>
          <tr className="border-b border-border bg-neutral-50 text-left text-xs font-medium uppercase text-neutral-600">
            <th className="px-4 py-3" scope="col">Title</th>
            <th className="px-4 py-3" scope="col">Format</th>
            <th className="px-4 py-3" scope="col">Status</th>
            <th className="px-4 py-3" scope="col">Created</th>
            <th className="px-4 py-3" scope="col">Actions</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((report) => (
            <tr
              key={report.id}
              className="border-b border-border transition-colors hover:bg-neutral-50"
            >
              <td className="px-4 py-3 font-medium text-neutral-900">{report.title}</td>
              <td className="px-4 py-3">
                <ReportFormatBadge format={report.format} />
              </td>
              <td className="px-4 py-3">
                <ReportStatusBadge status={report.status} />
              </td>
              <td className="px-4 py-3 text-neutral-600">
                {new Date(report.created_at).toLocaleDateString()}
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate(`/projects/${projectId}/reports/${report.id}`)}
                    aria-label={`View report: ${report.title}`}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(report)}
                    aria-label={`Delete report: ${report.title}`}
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
  )
}
