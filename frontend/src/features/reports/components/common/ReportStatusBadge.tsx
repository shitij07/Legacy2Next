import { Badge } from '@/components/ui/badge'
import { ReportStatus } from '../../types'

const statusConfig: Record<ReportStatus, { label: string; variant: 'warning' | 'success' | 'error' }> = {
  [ReportStatus.GENERATING]: { label: 'Generating', variant: 'warning' },
  [ReportStatus.READY]: { label: 'Ready', variant: 'success' },
  [ReportStatus.FAILED]: { label: 'Failed', variant: 'error' },
}

interface ReportStatusBadgeProps {
  status: ReportStatus
}

export function ReportStatusBadge({ status }: ReportStatusBadgeProps) {
  const config = statusConfig[status]
  return <Badge variant={config.variant}>{config.label}</Badge>
}
