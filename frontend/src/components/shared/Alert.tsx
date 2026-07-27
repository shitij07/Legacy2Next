import { AlertTriangle, CheckCircle2, Info, XCircle } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AlertProps {
  variant?: 'info' | 'success' | 'warning' | 'error'
  title?: string
  children: string
  className?: string
}

const config: Record<string, { icon: LucideIcon; bgClass: string; textClass: string }> = {
  info: {
    icon: Info,
    bgClass: 'bg-info/10',
    textClass: 'text-info',
  },
  success: {
    icon: CheckCircle2,
    bgClass: 'bg-success/10',
    textClass: 'text-success',
  },
  warning: {
    icon: AlertTriangle,
    bgClass: 'bg-warning/10',
    textClass: 'text-warning',
  },
  error: {
    icon: XCircle,
    bgClass: 'bg-error/10',
    textClass: 'text-error',
  },
}

export function Alert({ variant = 'info', title, children, className }: AlertProps) {
  const { icon: Icon, bgClass, textClass } = config[variant]

  return (
    <div
      role="alert"
      className={cn('flex gap-3 rounded-lg p-4', bgClass, className)}
    >
      <Icon className={cn('mt-0.5 h-5 w-5 shrink-0', textClass)} aria-hidden="true" />
      <div>
        {title && <p className="text-sm font-medium text-neutral-900">{title}</p>}
        <p className="text-sm text-neutral-700">{children}</p>
      </div>
    </div>
  )
}
