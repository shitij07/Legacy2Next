import { CheckCircle, Loader2, AlertTriangle, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { DashboardGeneral } from '@/lib/types'

interface DashboardSummaryProps {
  general: DashboardGeneral
}

const statusConfig: Record<string, { label: string; variant: 'default' | 'success' | 'warning' | 'error'; icon: React.ReactNode }> = {
  COMPLETED: {
    label: 'Completed',
    variant: 'success',
    icon: <CheckCircle className="h-4 w-4" aria-hidden="true" />,
  },
  COMPLETED_WITH_ERRORS: {
    label: 'Completed with errors',
    variant: 'warning',
    icon: <AlertTriangle className="h-4 w-4" aria-hidden="true" />,
  },
  FAILED: {
    label: 'Failed',
    variant: 'error',
    icon: <AlertCircle className="h-4 w-4" aria-hidden="true" />,
  },
  RUNNING: {
    label: 'Running',
    variant: 'default',
    icon: <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />,
  },
}

function formatDuration(ms: number | null): string {
  if (ms == null) return '—'
  if (ms < 1000) return `${ms}ms`
  if (ms < 60_000) return `${(ms / 1000).toFixed(1)}s`
  return `${Math.floor(ms / 60_000)}m ${Math.floor((ms % 60_000) / 1000)}s`
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function DashboardSummary({ general }: DashboardSummaryProps) {
  const status = statusConfig[general.status] ?? {
    label: general.status,
    variant: 'default' as const,
    icon: null,
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Analysis Overview</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap items-center gap-x-8 gap-y-3">
          <div className="flex items-center gap-2">
            <span className="text-sm text-neutral-600">Status</span>
            <Badge variant={status.variant} className="gap-1">
              {status.icon}
              {status.label}
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-neutral-600">Duration</span>
            <span className="text-sm font-medium text-neutral-900">
              {formatDuration(general.duration_ms)}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-neutral-600">Started</span>
            <span className="text-sm font-medium text-neutral-900">
              {formatDate(general.created_at)}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-neutral-600">Completed</span>
            <span className="text-sm font-medium text-neutral-900">
              {formatDate(general.completed_at)}
            </span>
          </div>
        </div>

        {general.error_detail && (
          <p className="mt-3 rounded-md bg-error/10 p-3 text-sm text-error">
            {general.error_detail}
          </p>
        )}
      </CardContent>
    </Card>
  )
}
