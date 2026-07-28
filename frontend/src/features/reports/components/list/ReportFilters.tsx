import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ReportFormat, ReportStatus } from '../../types'

interface ReportFiltersProps {
  format: ReportFormat | ''
  status: ReportStatus | ''
  onFormatChange: (value: ReportFormat | '') => void
  onStatusChange: (value: ReportStatus | '') => void
}

export function ReportFilters({ format, status, onFormatChange, onStatusChange }: ReportFiltersProps) {
  return (
    <div className="flex items-center gap-3">
      <Select
        value={status}
        onValueChange={(v) => onStatusChange(v === 'all' ? '' : v as ReportStatus)}
      >
        <SelectTrigger className="w-[140px]" aria-label="Filter by status">
          <SelectValue placeholder="All Statuses" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Statuses</SelectItem>
          <SelectItem value={ReportStatus.READY}>Ready</SelectItem>
          <SelectItem value={ReportStatus.GENERATING}>Generating</SelectItem>
          <SelectItem value={ReportStatus.FAILED}>Failed</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={format}
        onValueChange={(v) => onFormatChange(v === 'all' ? '' : v as ReportFormat)}
      >
        <SelectTrigger className="w-[150px]" aria-label="Filter by format">
          <SelectValue placeholder="All Formats" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Formats</SelectItem>
          <SelectItem value={ReportFormat.MARKDOWN}>Markdown</SelectItem>
          <SelectItem value={ReportFormat.JSON}>JSON</SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}
