import { useState, useMemo } from 'react'
import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { EmptyState } from '@/components/shared/EmptyState'
import { useAnalysisTechnologies } from '@/hooks/useAnalysis'
import { useDebounce } from '@/hooks/useDebounce'

interface TechnologiesTabProps {
  analysisId: number
}

export function TechnologiesTab({ analysisId }: TechnologiesTabProps) {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('all')
  const debouncedSearch = useDebounce(search, 300)

  const { data, isLoading, isError, error, refetch } = useAnalysisTechnologies(analysisId)

  const categories = useMemo(() => {
    if (!data) return []
    return [...new Set(data.map((t) => t.category))].sort()
  }, [data])

  const filtered = useMemo(() => {
    if (!data) return []
    return data.filter((t) => {
      if (category !== 'all' && t.category !== category) return false
      if (debouncedSearch) {
        const q = debouncedSearch.toLowerCase()
        return (
          t.name.toLowerCase().includes(q) ||
          t.category.toLowerCase().includes(q) ||
          (t.evidence ?? '').toLowerCase().includes(q)
        )
      }
      return true
    })
  }, [data, category, debouncedSearch])

  const confidenceVariant = (confidence: string): 'success' | 'warning' | 'info' | 'default' => {
    switch (confidence) {
      case 'high': return 'success'
      case 'medium': return 'warning'
      case 'low': return 'info'
      default: return 'default'
    }
  }

  if (isLoading) {
    return <LoadingState variant="card" count={6} />
  }

  if (isError) {
    return (
      <ErrorState
        title="Failed to load technologies"
        message={error?.message ?? 'An unexpected error occurred.'}
        onRetry={() => refetch()}
      />
    )
  }

  if (!data || data.length === 0) {
    return (
      <EmptyState
        title="No technologies detected"
        description="This analysis did not detect any technologies."
      />
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500" aria-hidden="true" />
          <Input
            placeholder="Search technologies..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
            aria-label="Search technologies"
          />
        </div>
        <Select value={category} onValueChange={setCategory}>
          <SelectTrigger className="w-44" aria-label="Filter by category">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map((cat) => (
              <SelectItem key={cat} value={cat}>{cat}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-sm text-neutral-600">
          {filtered.length} of {data.length} technologies
        </p>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="No technologies match"
          description="Try adjusting your search or filter."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((tech) => (
            <Card key={tech.id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-sm font-medium">{tech.name}</CardTitle>
                  <Badge variant={confidenceVariant(tech.confidence)} size="sm">
                    {tech.confidence}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-2 pt-0">
                <div className="flex flex-wrap gap-1">
                  <Badge variant="info" size="sm">{tech.category}</Badge>
                </div>
                {tech.evidence && (
                  <p className="text-xs text-neutral-600 line-clamp-2">{tech.evidence}</p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
