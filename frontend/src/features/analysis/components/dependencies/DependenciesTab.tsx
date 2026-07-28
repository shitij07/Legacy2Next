import { useState, useMemo } from 'react'
import { Search, ChevronDown, ChevronRight, Package } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { EmptyState } from '@/components/shared/EmptyState'
import { useAnalysisDependencies } from '@/hooks/useAnalysis'
import { useDebounce } from '@/hooks/useDebounce'
import { DataTable, type Column } from '../explorer/DataTable'
import { PaginationBar } from '../explorer/PaginationBar'
import type { AnalysisDependency, AnalysisDependenciesParams } from '@/lib/types'

interface DependenciesTabProps {
  analysisId: number
}

export function DependenciesTab({ analysisId }: DependenciesTabProps) {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [ecosystem, setEcosystem] = useState('all')
  const [depType, setDepType] = useState('all')
  const [sortBy, setSortBy] = useState('name')
  const [sortDir, setSortDir] = useState('asc')
  const [expandedRow, setExpandedRow] = useState<number | null>(null)

  const debouncedSearch = useDebounce(search, 300)

  const params: AnalysisDependenciesParams = useMemo(
    () => ({
      page,
      size: 50,
      search: debouncedSearch || undefined,
      ecosystem: ecosystem && ecosystem !== 'all' ? ecosystem : undefined,
      type: depType && depType !== 'all' ? depType : undefined,
      sort_by: sortBy,
      sort_dir: sortDir,
    }),
    [page, debouncedSearch, ecosystem, depType, sortBy, sortDir],
  )

  const { data, isLoading, isError, error, refetch } = useAnalysisDependencies(analysisId, params)

  const uniqueEcosystems = useMemo(() => {
    if (!data?.items) return []
    return [...new Set(data.items.map((d) => d.ecosystem).filter(Boolean))].sort() as string[]
  }, [data])

  const columns: Column<AnalysisDependency>[] = useMemo(
    () => [
      {
        key: 'expand',
        header: '',
        render: (item) =>
          item.source_files.length > 0 ? (
            <button
              onClick={(e) => {
                e.stopPropagation()
                setExpandedRow(expandedRow === item.id ? null : item.id)
              }}
              className="text-neutral-500 hover:text-neutral-700"
              aria-label={expandedRow === item.id ? 'Collapse source files' : 'Expand source files'}
            >
              {expandedRow === item.id ? (
                <ChevronDown className="h-4 w-4" aria-hidden="true" />
              ) : (
                <ChevronRight className="h-4 w-4" aria-hidden="true" />
              )}
            </button>
          ) : (
            <span className="inline-block w-4" />
          ),
        className: 'w-8',
      },
      {
        key: 'name',
        header: 'Package',
        render: (item) => (
          <div className="flex items-center gap-2">
            <Package className="h-4 w-4 shrink-0 text-neutral-500" aria-hidden="true" />
            <span className="font-medium text-neutral-900">{item.name}</span>
          </div>
        ),
      },
      {
        key: 'version',
        header: 'Version',
        render: (item) =>
          item.version ? (
            <code className="rounded bg-neutral-200 px-1.5 py-0.5 text-xs text-neutral-700">{item.version}</code>
          ) : (
            <span className="text-neutral-500">—</span>
          ),
      },
      {
        key: 'type',
        header: 'Type',
        render: (item) => (
          <Badge variant={item.type === 'dev' ? 'warning' : 'info'} size="sm">
            {item.type}
          </Badge>
        ),
      },
      {
        key: 'ecosystem',
        header: 'Ecosystem',
        render: (item) =>
          item.ecosystem ? (
            <Badge variant="default" size="sm">{item.ecosystem}</Badge>
          ) : (
            <span className="text-neutral-500">—</span>
          ),
        className: 'hidden sm:table-cell',
      },
      {
        key: 'source_files_count',
        header: 'Source Files',
        render: (item) => (
          <span className="text-neutral-700">{item.source_files.length}</span>
        ),
        className: 'text-right',
      },
    ],
    [expandedRow],
  )

  if (isLoading) {
    return <LoadingState variant="table" count={5} />
  }

  if (isError) {
    return (
      <ErrorState
        title="Failed to load dependencies"
        message={error?.message ?? 'An unexpected error occurred.'}
        onRetry={() => refetch()}
      />
    )
  }

  const items = data?.items ?? []
  const total = data?.total ?? 0
  const pages = data?.pages ?? 1

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500" aria-hidden="true" />
          <Input
            placeholder="Search dependencies..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            className="pl-9"
            aria-label="Search dependencies"
          />
        </div>
        <Select value={ecosystem} onValueChange={(v) => { setEcosystem(v); setPage(1) }}>
          <SelectTrigger className="w-36" aria-label="Filter by ecosystem">
            <SelectValue placeholder="Ecosystem" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Ecosystems</SelectItem>
            {uniqueEcosystems.map((eco) => (
              <SelectItem key={eco} value={eco}>{eco}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={depType} onValueChange={(v) => { setDepType(v); setPage(1) }}>
          <SelectTrigger className="w-28" aria-label="Filter by type">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="library">Library</SelectItem>
            <SelectItem value="dev">Dev</SelectItem>
          </SelectContent>
        </Select>
        <Select value={sortBy} onValueChange={(v) => { setSortBy(v); setPage(1) }}>
          <SelectTrigger className="w-36" aria-label="Sort dependencies">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="name">Name</SelectItem>
            <SelectItem value="ecosystem">Ecosystem</SelectItem>
            <SelectItem value="type">Type</SelectItem>
          </SelectContent>
        </Select>
        <Select value={sortDir} onValueChange={(v) => { setSortDir(v); setPage(1) }}>
          <SelectTrigger className="w-28" aria-label="Sort direction">
            <SelectValue placeholder="Direction" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="asc">Ascending</SelectItem>
            <SelectItem value="desc">Descending</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {items.length === 0 ? (
        <EmptyState
          title="No dependencies found"
          description={debouncedSearch ? 'Try a different search term.' : 'This analysis has no dependencies.'}
        />
      ) : (
        <>
          <DataTable
            columns={columns}
            data={items}
            expandedRowId={expandedRow}
            renderExpandedRow={(item) => {
              const dep = item
              if (dep.source_files.length === 0) return null
              return (
                <div className="space-y-2">
                  <p className="text-xs font-medium uppercase tracking-wider text-neutral-600">Source Files</p>
                  <ul className="space-y-1">
                    {dep.source_files.map((sf, i) => (
                      <li key={i} className="flex items-center gap-2 text-sm text-neutral-700">
                        <span className="h-1 w-1 rounded-full bg-neutral-400" aria-hidden="true" />
                        <code className="text-xs">{sf}</code>
                      </li>
                    ))}
                  </ul>
                </div>
              )
            }}
          />
          <PaginationBar
            page={page}
            size={50}
            total={total}
            pages={pages}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  )
}
