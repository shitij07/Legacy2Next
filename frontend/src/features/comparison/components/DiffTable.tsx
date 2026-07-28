import { cn } from '@/lib/utils'

interface Column {
  key: string
  header: string
  render: (item: Record<string, unknown>) => React.ReactNode
}

interface DiffTableProps {
  columns: Column[]
  data: Array<Record<string, unknown>>
  emptyMessage?: string
  className?: string
}

export function DiffTable({ columns, data, emptyMessage = 'No items', className }: DiffTableProps) {
  if (data.length === 0) {
    return (
      <p className="py-2 text-sm text-neutral-500">{emptyMessage}</p>
    )
  }

  return (
    <div className={cn('overflow-x-auto rounded-lg border border-border', className)}>
      <table className="w-full text-sm" role="table">
        <thead>
          <tr className="border-b border-border bg-neutral-100">
            {columns.map((col) => (
              <th
                key={col.key}
                scope="col"
                className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-neutral-600"
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {data.map((item, index) => (
            <tr key={index} className="bg-neutral-50">
              {columns.map((col) => (
                <td key={col.key} className="whitespace-nowrap px-3 py-2 text-neutral-800">
                  {col.render(item)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
