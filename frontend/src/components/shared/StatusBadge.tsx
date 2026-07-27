import { Badge } from '@/components/ui/badge'

type Status = 'completed' | 'pending' | 'failed' | 'running' | 'uploaded'

const statusConfig: Record<Status, { variant: 'success' | 'warning' | 'error' | 'info'; label: string }> = {
  completed: { variant: 'success', label: 'Completed' },
  pending: { variant: 'warning', label: 'Pending' },
  failed: { variant: 'error', label: 'Failed' },
  running: { variant: 'info', label: 'Running' },
  uploaded: { variant: 'info', label: 'Uploaded' },
}

interface StatusBadgeProps {
  status: string
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status as Status]

  if (!config) {
    return <Badge>{status}</Badge>
  }

  return <Badge variant={config.variant}>{config.label}</Badge>
}
