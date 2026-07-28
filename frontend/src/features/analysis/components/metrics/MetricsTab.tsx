import { useState, useMemo } from 'react'
import { Search, BarChart3 } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { EmptyState } from '@/components/shared/EmptyState'
import { useAnalysisMetrics } from '@/hooks/useAnalysis'
import { useDebounce } from '@/hooks/useDebounce'
import type { AnalysisMetric } from '@/lib/types'

interface MetricsTabProps {
  analysisId: number
}

export function MetricsTab({ analysisId }: MetricsTabProps) {
  const [search, setSearch] = useState('')
  const debouncedSearch = useDebounce(search, 300)

  const { data, isLoading, isError, error, refetch } = useAnalysisMetrics(analysisId)

  const filtered = useMemo(() => {
    if (!data) return []
    if (!debouncedSearch) return data
    const q = debouncedSearch.toLowerCase()
    return data.filter(
      (m) =>
        m.key.toLowerCase().includes(q) ||
        String(m.value ?? '').toLowerCase().includes(q),
    )
  }, [data, debouncedSearch])

  if (isLoading) {
    return <LoadingState variant="card" count={6} />
  }

  if (isError) {
    return (
      <ErrorState
        title="Failed to load metrics"
        message={error?.message ?? 'An unexpected error occurred.'}
        onRetry={() => refetch()}
      />
    )
  }

  if (!data || data.length === 0) {
    return (
      <EmptyState
        title="No metrics available"
        description="This analysis has no metrics data."
      />
    )
  }

  return (
    <div className="space-y-4">
      <div className="relative flex-1 sm:max-w-xs">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500" aria-hidden="true" />
        <Input
          placeholder="Search metrics..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
          aria-label="Search metrics"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="No metrics match"
          description="Try a different search term."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((metric) => (
            <MetricCard key={metric.id} metric={metric} />
          ))}
        </div>
      )}
    </div>
  )
}

function MetricCard({ metric }: { metric: AnalysisMetric }) {
  const displayKey = metric.key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-neutral-500" aria-hidden="true" />
          <CardTitle className="text-sm font-medium text-neutral-700">{displayKey}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-2xl font-semibold text-neutral-900">
          {metric.value !== null && metric.value !== undefined ? String(metric.value) : '—'}
        </p>
      </CardContent>
    </Card>
  )
}
