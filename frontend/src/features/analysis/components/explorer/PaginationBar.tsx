import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface PaginationBarProps {
  page: number
  size: number
  total: number
  pages: number
  onPageChange: (page: number) => void
}

export function PaginationBar({ page, size, total, pages, onPageChange }: PaginationBarProps) {
  if (total === 0) return null

  const startItem = (page - 1) * size + 1
  const endItem = Math.min(page * size, total)

  const getVisiblePages = (): (number | 'ellipsis')[] => {
    const visible: (number | 'ellipsis')[] = []
    if (pages <= 7) {
      for (let i = 1; i <= pages; i++) visible.push(i)
      return visible
    }
    visible.push(1)
    if (page > 3) visible.push('ellipsis')
    const start = Math.max(2, page - 1)
    const end = Math.min(pages - 1, page + 1)
    for (let i = start; i <= end; i++) visible.push(i)
    if (page < pages - 2) visible.push('ellipsis')
    visible.push(pages)
    return visible
  }

  return (
    <div className="flex flex-col items-center gap-3 sm:flex-row sm:justify-between">
      <p className="text-sm text-neutral-600" role="status">
        Showing <span className="font-medium">{startItem}</span> to{' '}
        <span className="font-medium">{endItem}</span> of{' '}
        <span className="font-medium">{total}</span> results
      </p>
      <nav aria-label="Pagination" className="flex items-center gap-1">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          aria-label="Go to previous page"
        >
          <ChevronLeft className="h-4 w-4" aria-hidden="true" />
        </Button>
        {getVisiblePages().map((p, i) =>
          p === 'ellipsis' ? (
            <span key={`ellipsis-${i}`} className="flex h-8 w-8 items-center justify-center text-sm text-neutral-500">
              ...
            </span>
          ) : (
            <Button
              key={p}
              variant={p === page ? 'primary' : 'outline'}
              size="sm"
              onClick={() => onPageChange(p)}
              aria-label={`Go to page ${p}`}
              aria-current={p === page ? 'page' : undefined}
            >
              {p}
            </Button>
          ),
        )}
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(page + 1)}
          disabled={page >= pages}
          aria-label="Go to next page"
        >
          <ChevronRight className="h-4 w-4" aria-hidden="true" />
        </Button>
      </nav>
    </div>
  )
}
