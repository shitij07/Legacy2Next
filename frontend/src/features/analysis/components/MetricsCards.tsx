import { memo } from 'react'
import type { DashboardFiles, DashboardTechnologies, DashboardDependencies, DashboardMetrics } from '@/lib/types'

interface MetricsCardsProps {
  files: DashboardFiles
  technologies: DashboardTechnologies
  dependencies: DashboardDependencies
  metrics: DashboardMetrics
}

export const MetricsCards = memo(function MetricsCards({ files, technologies, dependencies, metrics }: MetricsCardsProps) {
  const cards = [
    { label: 'Total Files', value: files.total_files },
    { label: 'Languages', value: metrics.language_count ?? technologies.category_distribution.length },
    { label: 'Frameworks', value: metrics.framework_count ?? technologies.primary_frameworks.length },
    { label: 'Dependencies', value: metrics.dependency_count ?? dependencies.total_dependencies },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <div key={card.label} className="rounded-lg border border-border bg-neutral-100 p-4">
          <p className="text-xs font-medium text-neutral-600">{card.label}</p>
          <p className="mt-1 text-2xl font-semibold text-neutral-900">{card.value}</p>
        </div>
      ))}
    </div>
  )
})
