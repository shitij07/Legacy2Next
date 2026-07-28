import { AlertTriangle } from 'lucide-react'

interface ErrorCardProps {
  message?: string
}

export function ErrorCard({ message }: ErrorCardProps) {
  return (
    <div className="rounded-lg border border-error/30 bg-error/5 p-4">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-error/10">
          <AlertTriangle className="h-3.5 w-3.5 text-error" aria-hidden="true" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-error">Generation failed</p>
          <p className="mt-1 text-sm text-error/80">
            {message ?? 'An unexpected error occurred. Please try again.'}
          </p>
        </div>
      </div>
    </div>
  )
}
