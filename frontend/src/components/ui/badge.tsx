import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-neutral-200 text-neutral-700',
        success: 'bg-success/15 text-success',
        warning: 'bg-warning/15 text-warning',
        error: 'bg-error/15 text-error',
        info: 'bg-info/15 text-info',
      },
      size: {
        sm: 'px-1.5 py-0 text-[11px]',
        md: 'px-2.5 py-0.5 text-xs',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  },
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  isDot?: boolean
}

function Badge({ className, variant, size, isDot, children, ...props }: BadgeProps) {
  if (isDot) {
    return (
      <span
        className={cn('inline-block h-2 w-2 rounded-full', {
          'bg-neutral-500': variant === 'default' || !variant,
          'bg-success': variant === 'success',
          'bg-warning': variant === 'warning',
          'bg-error': variant === 'error',
          'bg-info': variant === 'info',
        })}
        aria-hidden="true"
      />
    )
  }

  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props}>
      {children}
    </div>
  )
}

export { Badge, badgeVariants }
