import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader } from '@/components/ui/card'

interface SectionCardProps {
  children: ReactNode
  className?: string
}

export function SectionCard({ children, className }: SectionCardProps) {
  return (
    <Card className={cn('', className)}>
      {children}
    </Card>
  )
}

export { CardHeader, CardContent }
