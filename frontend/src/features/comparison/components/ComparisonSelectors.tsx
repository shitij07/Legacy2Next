import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useProjectAnalyses } from '@/hooks/useAnalysis'
import type { AnalysisListItem } from '@/lib/types'

interface ComparisonSelectorsProps {
  projectId: number
  onCompare: (analysisAId: number, analysisBId: number) => void
  isComparing: boolean
}

export function ComparisonSelectors({ projectId, onCompare, isComparing }: ComparisonSelectorsProps) {
  const { data, isLoading } = useProjectAnalyses(projectId)
  const [analysisAId, setAnalysisAId] = useState<string>('')
  const [analysisBId, setAnalysisBId] = useState<string>('')

  const allAnalyses: AnalysisListItem[] = data?.items ?? []

  const completedAnalyses = allAnalyses.filter(
    (a) => a.status === 'COMPLETED' || a.status === 'completed',
  )

  const canCompare = analysisAId && analysisBId && analysisAId !== analysisBId

  const handleCompare = () => {
    if (canCompare) {
      onCompare(Number(analysisAId), Number(analysisBId))
    }
  }

  return (
    <div className="flex flex-wrap items-end gap-4 rounded-lg border border-border bg-neutral-50 p-4">
      <div className="min-w-[200px] flex-1">
        <label htmlFor="analysis-a" className="mb-1 block text-xs font-medium text-neutral-600">
          Analysis A
        </label>
        <Select value={analysisAId} onValueChange={setAnalysisAId} disabled={isLoading}>
          <SelectTrigger id="analysis-a" className="w-full">
            <SelectValue placeholder={isLoading ? 'Loading...' : 'Select analysis A'} />
          </SelectTrigger>
          <SelectContent>
            {completedAnalyses.map((a) => (
              <SelectItem key={a.id} value={String(a.id)}>
                Analysis #{a.id} — {a.created_at ? new Date(a.created_at).toLocaleDateString() : ''}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="min-w-[200px] flex-1">
        <label htmlFor="analysis-b" className="mb-1 block text-xs font-medium text-neutral-600">
          Analysis B
        </label>
        <Select value={analysisBId} onValueChange={setAnalysisBId} disabled={isLoading}>
          <SelectTrigger id="analysis-b" className="w-full">
            <SelectValue placeholder={isLoading ? 'Loading...' : 'Select analysis B'} />
          </SelectTrigger>
          <SelectContent>
            {completedAnalyses.map((a) => (
              <SelectItem key={a.id} value={String(a.id)}>
                Analysis #{a.id} — {a.created_at ? new Date(a.created_at).toLocaleDateString() : ''}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Button onClick={handleCompare} disabled={!canCompare || isComparing} className="shrink-0">
        {isComparing ? 'Comparing...' : 'Compare'}
      </Button>
    </div>
  )
}
