import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface ContainerProps {
  children: ReactNode
  className?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const maxWidths = {
  sm: 'max-w-3xl',
  md: 'max-w-5xl',
  lg: 'max-w-7xl',
  xl: 'max-w-[1600px]',
}

export function Container({ children, className, size = 'lg' }: ContainerProps) {
  return (
    <div className={cn('mx-auto w-full px-6', maxWidths[size], className)}>
      {children}
    </div>
  )
}
