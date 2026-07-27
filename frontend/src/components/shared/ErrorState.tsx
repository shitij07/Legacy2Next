import { AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
  className?: string
}

export function ErrorState({
  title = 'Failed to load',
  message = 'This could be a network issue. Please try again.',
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-16 text-center', className)}>
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-error/10">
        <AlertTriangle className="h-6 w-6 text-error" aria-hidden="true" />
      </div>
      <h3 className="text-base font-semibold text-neutral-800">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-neutral-600">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 rounded-md bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600"
        >
          Try Again
        </button>
      )}
    </div>
  )
}
