import { useState, useMemo } from 'react'
import { Search, AlertTriangle } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { EmptyState } from '@/components/shared/EmptyState'
import { useAnalysisWarnings } from '@/hooks/useAnalysis'
import { useDebounce } from '@/hooks/useDebounce'
import { PaginationBar } from '../explorer/PaginationBar'
import type { AnalysisWarningsParams, AnalysisWarning } from '@/lib/types'

interface WarningsTabProps {
  analysisId: number
}

function formatTimestamp(ts: string): string {
  try {
    const date = new Date(ts)
    return date.toLocaleString()
  } catch {
    return ts
  }
}

export function WarningsTab({ analysisId }: WarningsTabProps) {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [detectorName, setDetectorName] = useState('all')
  const [sortBy, setSortBy] = useState('created_at')
  const [sortDir, setSortDir] = useState('desc')

  const debouncedSearch = useDebounce(search, 300)

  const params: AnalysisWarningsParams = useMemo(
    () => ({
      page,
      size: 50,
      search: debouncedSearch || undefined,
      detector_name: detectorName && detectorName !== 'all' ? detectorName : undefined,
      sort_by: sortBy,
      sort_dir: sortDir,
    }),
    [page, debouncedSearch, detectorName, sortBy, sortDir],
  )

  const { data, isLoading, isError, error, refetch } = useAnalysisWarnings(analysisId, params)

  const uniqueDetectors = useMemo(() => {
    if (!data?.items) return []
    return [...new Set(data.items.map((w) => w.detector_name))].sort()
  }, [data])

  if (isLoading) {
    return <LoadingState variant="card" count={4} />
  }

  if (isError) {
    return (
      <ErrorState
        title="Failed to load warnings"
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
            placeholder="Search warnings..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            className="pl-9"
            aria-label="Search warnings"
          />
        </div>
        <Select value={detectorName} onValueChange={(v) => { setDetectorName(v); setPage(1) }}>
          <SelectTrigger className="w-40" aria-label="Filter by detector">
            <SelectValue placeholder="Detector" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Detectors</SelectItem>
            {uniqueDetectors.map((d) => (
              <SelectItem key={d} value={d}>{d}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={sortBy} onValueChange={(v) => { setSortBy(v); setPage(1) }}>
          <SelectTrigger className="w-36" aria-label="Sort warnings">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="created_at">Date</SelectItem>
            <SelectItem value="detector_name">Detector</SelectItem>
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
          title="No warnings found"
          description={debouncedSearch ? 'Try a different search term.' : 'This analysis has no warnings.'}
        />
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2">
            {items.map((warning) => (
              <WarningCard key={warning.id} warning={warning} />
            ))}
          </div>
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

function WarningCard({ warning }: { warning: AnalysisWarning }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-start gap-3 pb-2">
        <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-warning/10">
          <AlertTriangle className="h-3.5 w-3.5 text-warning" aria-hidden="true" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <Badge variant="warning" size="sm">{warning.detector_name}</Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-sm text-neutral-800">{warning.message}</p>
        <p className="mt-2 text-xs text-neutral-500">{formatTimestamp(warning.created_at)}</p>
      </CardContent>
    </Card>
  )
}
