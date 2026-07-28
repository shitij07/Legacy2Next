import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

interface DiffStat {
  label: string
  value: number
  variant?: 'added' | 'removed' | 'changed' | 'neutral'
}

interface DiffCardProps {
  title: string
  stats: DiffStat[]
  isLoading?: boolean
  className?: string
}

function DiffStatRow({ stat }: { stat: DiffStat }) {
  const colorClass = {
    added: 'text-success',
    removed: 'text-error',
    changed: 'text-warning',
    neutral: 'text-neutral-900',
  }[stat.variant ?? 'neutral']

  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-sm text-neutral-600">{stat.label}</span>
      <span className={cn('text-sm font-semibold', colorClass)}>{stat.value}</span>
    </div>
  )
}

export function DiffCard({ title, stats, isLoading, className }: DiffCardProps) {
  if (isLoading) {
    return (
      <Card className={cn('p-4', className)}>
        <Skeleton className="mb-3 h-4 w-32" />
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="mb-2 h-3 w-full" />
        ))}
      </Card>
    )
  }

  return (
    <Card className={cn('p-4', className)}>
      <h3 className="mb-2 text-sm font-medium text-neutral-800">{title}</h3>
      <div className="space-y-0.5">
        {stats.map((stat) => (
          <DiffStatRow key={stat.label} stat={stat} />
        ))}
      </div>
    </Card>
  )
}
