import { memo } from 'react'
import { AlertTriangle, ArrowRight } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { DashboardWarnings } from '@/lib/types'

interface TopFindingsProps {
  warnings: DashboardWarnings
}

export const TopFindings = memo(function TopFindings({ warnings }: TopFindingsProps) {
  const topDetectors = [...warnings.detector_breakdown]
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)

  if (topDetectors.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Top Findings</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-neutral-600">No warnings found. The codebase looks clean.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Findings</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {topDetectors.map((detector) => (
            <div key={detector.detector_name} className="flex items-start gap-3">
              <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-warning/10">
                <AlertTriangle className="h-3.5 w-3.5 text-warning" aria-hidden="true" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-neutral-900">
                  {detector.detector_name.replace(/_/g, ' ')}
                </p>
                <p className="text-xs text-neutral-600">
                  {detector.count} warning{detector.count !== 1 ? 's' : ''}
                </p>
              </div>
              <ArrowRight className="mt-0.5 h-4 w-4 shrink-0 text-neutral-400" aria-hidden="true" />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
})
