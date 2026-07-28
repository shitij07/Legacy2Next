import { Fragment, type ReactNode } from 'react'
import { cn } from '@/lib/utils'

export interface Column<T> {
  key: string
  header: string
  render: (item: T) => ReactNode
  className?: string
  sortable?: boolean
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  onRowClick?: (item: T) => void
  expandedRowId?: number | string | null
  renderExpandedRow?: (item: T) => ReactNode
  className?: string
}

export function DataTable<T>({
  columns,
  data,
  onRowClick,
  expandedRowId,
  renderExpandedRow,
  className,
}: DataTableProps<T>) {
  return (
    <div className={cn('overflow-x-auto rounded-lg border border-border', className)}>
      <table className="w-full text-sm" role="table">
        <thead>
          <tr className="border-b border-border bg-neutral-100">
            {columns.map((col) => (
              <th
                key={col.key}
                scope="col"
                className={cn(
                  'px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-neutral-600',
                  col.className,
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {data.map((item, index) => {
            const itemId = (item as { id?: unknown }).id
            const resolvedId = itemId != null ? String(itemId) : String(index)
            return (
              <Fragment key={resolvedId}>
                <tr
                  onClick={onRowClick ? () => onRowClick(item) : undefined}
                  className={cn(
                    'bg-neutral-50 transition-colors',
                    onRowClick && 'cursor-pointer hover:bg-neutral-100',
                  )}
                  tabIndex={onRowClick ? 0 : undefined}
                  onKeyDown={
                    onRowClick
                      ? (e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault()
                            onRowClick(item)
                          }
                        }
                      : undefined
                  }
                  role={onRowClick ? 'button' : undefined}
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={cn('whitespace-nowrap px-4 py-3 text-neutral-800', col.className)}
                    >
                      {col.render(item)}
                    </td>
                  ))}
                </tr>
                {expandedRowId != null && expandedRowId === itemId && renderExpandedRow && (
                  <tr className="bg-neutral-100">
                    <td
                      colSpan={columns.length}
                      className="border-t border-border px-4 py-3"
                    >
                      {renderExpandedRow(item)}
                    </td>
                  </tr>
                )}
              </Fragment>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
