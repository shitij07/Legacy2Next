import { Badge } from '@/components/ui/badge'
import { ReportFormat } from '../../types'

const formatConfig: Record<ReportFormat, { label: string; variant: 'default' | 'info' }> = {
  [ReportFormat.MARKDOWN]: { label: 'Markdown', variant: 'default' },
  [ReportFormat.JSON]: { label: 'JSON', variant: 'info' },
}

interface ReportFormatBadgeProps {
  format: ReportFormat
}

export function ReportFormatBadge({ format }: ReportFormatBadgeProps) {
  const config = formatConfig[format]
  return <Badge variant={config.variant}>{config.label}</Badge>
}
