import { cn } from '@/lib/utils'

interface KeyValueProps {
  label: string
  value: string | number | React.ReactNode
  direction?: 'row' | 'column'
  className?: string
}

export function KeyValue({ label, value, direction = 'column', className }: KeyValueProps) {
  return (
    <div
      className={cn(
        {
          'flex flex-col gap-0.5': direction === 'column',
          'flex items-center gap-2': direction === 'row',
        },
        className,
      )}
    >
      <dt className="text-xs font-medium text-neutral-600">{label}</dt>
      <dd className="text-sm text-neutral-800">
        {typeof value === 'string' || typeof value === 'number' ? (
          <span className="font-mono text-sm">{value}</span>
        ) : (
          value
        )}
      </dd>
    </div>
  )
}
