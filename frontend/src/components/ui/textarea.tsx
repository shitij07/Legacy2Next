import * as React from 'react'
import { cn } from '@/lib/utils'

const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        'flex min-h-[80px] w-full rounded-md border border-border bg-neutral-50 px-3 py-2 text-sm text-neutral-800',
        'placeholder:text-neutral-500',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/20 focus-visible:border-primary-500',
        'disabled:cursor-not-allowed disabled:opacity-40',
        className,
      )}
      ref={ref}
      {...props}
    />
  )
})
Textarea.displayName = 'Textarea'

export { Textarea }
