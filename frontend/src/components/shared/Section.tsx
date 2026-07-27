import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface SectionProps {
  title?: string
  description?: string
  children: ReactNode
  className?: string
  actions?: ReactNode
}

export function Section({ title, description, children, className, actions }: SectionProps) {
  return (
    <section className={cn('space-y-4', className)}>
      {(title || actions) && (
        <div className="flex items-start justify-between gap-4">
          <div>
            {title && <h2 className="text-lg font-medium text-neutral-900">{title}</h2>}
            {description && <p className="mt-1 text-sm text-neutral-600">{description}</p>}
          </div>
          {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
        </div>
      )}
      {children}
    </section>
  )
}
