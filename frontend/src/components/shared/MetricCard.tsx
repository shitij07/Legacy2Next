import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

interface MetricCardProps {
  label: string
  value: string | number
  trend?: { value: number; isPositive: boolean }
  isLoading?: boolean
  className?: string
}

export function MetricCard({ label, value, trend, isLoading, className }: MetricCardProps) {
  if (isLoading) {
    return (
      <Card className={cn('p-4', className)}>
        <Skeleton className="mb-2 h-3 w-20" />
        <Skeleton className="mb-1 h-7 w-12" />
        <Skeleton className="h-3 w-16" />
      </Card>
    )
  }

  return (
    <Card className={cn('p-4', className)}>
      <p className="text-xs font-medium text-neutral-600">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-neutral-900">{value}</p>
      {trend && (
        <p
          className={cn('mt-1 text-xs font-medium', {
            'text-success': trend.isPositive,
            'text-error': !trend.isPositive,
          })}
        >
          {trend.isPositive ? '+' : ''}
          {trend.value}% from last run
        </p>
      )}
    </Card>
  )
}
