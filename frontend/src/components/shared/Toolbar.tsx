import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface ToolbarProps {
  children: ReactNode
  className?: string
}

export function Toolbar({ children, className }: ToolbarProps) {
  return (
    <div className={cn('flex flex-wrap items-center gap-2', className)}>
      {children}
    </div>
  )
}
