import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { DashboardWarnings, DashboardMetrics, DashboardTechnologies, DashboardDependencies, DashboardGeneral } from '@/lib/types'

interface RiskIndicatorProps {
  general: DashboardGeneral
  warnings: DashboardWarnings
  metrics: DashboardMetrics
  technologies: DashboardTechnologies
  dependencies: DashboardDependencies
}

function calculateScore(input: RiskIndicatorProps): { readiness: number; risk: 'low' | 'medium' | 'high'; label: string } {
  const { general, warnings, metrics, technologies, dependencies } = input
  let score = 100

  if (general.status === 'FAILED') return { readiness: 0, risk: 'high', label: 'Critical' }
  if (general.status === 'COMPLETED_WITH_ERRORS') score -= 15

  score -= warnings.total_warnings * 2

  if (warnings.total_warnings === 0) score += 10

  if (technologies.primary_frameworks.length > 0) score += 10
  if (metrics.primary_language) score += 5
  if (dependencies.total_dependencies > 0) score += 5

  score = Math.max(0, Math.min(100, score))

  if (score >= 70) return { readiness: score, risk: 'low', label: 'Good' }
  if (score >= 40) return { readiness: score, risk: 'medium', label: 'Moderate' }
  return { readiness: score, risk: 'high', label: 'Poor' }
}

const colorMap: Record<string, string> = {
  low: 'bg-success text-white',
  medium: 'bg-warning text-white',
  high: 'bg-error text-white',
}

const ringColorMap: Record<string, string> = {
  low: 'stroke-success',
  medium: 'stroke-warning',
  high: 'stroke-error',
}

export function RiskIndicator(props: RiskIndicatorProps) {
  const { readiness, risk, label } = calculateScore(props)
  const circumference = 2 * Math.PI * 40
  const offset = circumference - (readiness / 100) * circumference

  return (
    <Card>
      <CardHeader>
        <CardTitle>Migration Readiness</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center">
        <div className="relative flex items-center justify-center">
          <svg width="100" height="100" className="-rotate-90">
            <circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" strokeWidth="8" className="text-neutral-300" />
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              strokeWidth="8"
              strokeLinecap="round"
              className={ringColorMap[risk]}
              strokeDasharray={circumference}
              strokeDashoffset={offset}
            />
          </svg>
          <span className="absolute text-2xl font-bold text-neutral-900">{readiness}</span>
        </div>

        <span className={cn('mt-3 rounded-full px-3 py-1 text-xs font-medium', colorMap[risk])}>
          {label}
        </span>

        <p className="mt-2 text-center text-xs text-neutral-600">
          {risk === 'low'
            ? 'This project is well-structured and ready for migration.'
            : risk === 'medium'
              ? 'Some issues found. Review warnings before proceeding.'
              : 'Significant issues detected. Consider addressing warnings first.'}
        </p>
      </CardContent>
    </Card>
  )
}
