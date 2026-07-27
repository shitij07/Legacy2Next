import { cn } from '@/lib/utils'
import { Skeleton } from '@/components/ui/skeleton'

interface LoadingStateProps {
  variant?: 'card' | 'table' | 'text' | 'page'
  count?: number
  className?: string
}

export function LoadingState({ variant = 'text', count = 3, className }: LoadingStateProps) {
  if (variant === 'card') {
    return (
      <div className={cn('grid gap-4 sm:grid-cols-2 lg:grid-cols-3', className)}>
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="rounded-lg border border-border p-4">
            <Skeleton className="mb-3 h-4 w-24" />
            <Skeleton className="mb-2 h-8 w-16" />
            <Skeleton className="h-3 w-32" />
          </div>
        ))}
      </div>
    )
  }

  if (variant === 'table') {
    return (
      <div className={cn('space-y-3', className)}>
        <Skeleton className="h-10 w-full" />
        {Array.from({ length: count }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    )
  }

  if (variant === 'page') {
    return (
      <div className={cn('space-y-6', className)}>
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-96" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
        <Skeleton className="h-64 w-full rounded-lg" />
      </div>
    )
  }

  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} className="h-4 w-full" style={{ width: `${70 + Math.random() * 30}%` }} />
      ))}
    </div>
  )
}
