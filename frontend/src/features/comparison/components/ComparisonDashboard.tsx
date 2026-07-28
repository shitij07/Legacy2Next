import { useMemo } from 'react'
import { Section } from '@/components/shared/Section'
import { DiffCard } from './DiffCard'
import { DiffTable } from './DiffTable'
import type { ComparisonData } from '../types'

function formatValue(v: unknown): string {
  if (v === null || v === undefined) return '-'
  return String(v)
}

interface ComparisonDashboardProps {
  data: ComparisonData
}

export function ComparisonDashboard({ data }: ComparisonDashboardProps) {
  const metrics = data.metrics
  const technologies = data.technologies
  const dependencies = data.dependencies
  const files = data.files
  const warnings = data.warnings

  const metricStats = useMemo(() => {
    const items = []
    if (metrics.loc) items.push({ label: 'Lines of Code', value: formatDelta(metrics.loc.abs_diff), variant: deltaVariant(metrics.loc.abs_diff) })
    if (metrics.file_count) items.push({ label: 'File Count', value: formatDelta(metrics.file_count.abs_diff), variant: deltaVariant(metrics.file_count.abs_diff) })
    if (metrics.dependency_count) items.push({ label: 'Dependencies', value: formatDelta(metrics.dependency_count.abs_diff), variant: deltaVariant(metrics.dependency_count.abs_diff) })
    if (metrics.technology_count) items.push({ label: 'Technologies', value: formatDelta(metrics.technology_count.abs_diff), variant: deltaVariant(metrics.technology_count.abs_diff) })
    if (metrics.warning_count) items.push({ label: 'Warnings', value: formatDelta(metrics.warning_count.abs_diff), variant: deltaVariant(metrics.warning_count.abs_diff) })
    return items
  }, [metrics])

  return (
    <div className="space-y-6">
      <Section title="Metrics Comparison" description="Key metric differences between the two analyses">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {metricStats.map((stat) => (
            <DiffCard
              key={stat.label}
              title={stat.label}
              stats={[{ label: 'Difference', value: stat.value, variant: stat.variant as 'added' | 'removed' | 'changed' | 'neutral' }]}
            />
          ))}
          {metricStats.length === 0 && (
            <p className="col-span-full text-sm text-neutral-500">No metric data available for comparison.</p>
          )}
        </div>
      </Section>

      <Section title="Technologies" description="Added, removed, and common technologies">
        <div className="grid gap-4 sm:grid-cols-3">
          <DiffCard
            title="Added"
            stats={[{ label: 'Technologies', value: technologies.added.length, variant: 'added' }]}
          />
          <DiffCard
            title="Removed"
            stats={[{ label: 'Technologies', value: technologies.removed.length, variant: 'removed' }]}
          />
          <DiffCard
            title="Common"
            stats={[{ label: 'Technologies', value: technologies.common.length, variant: 'neutral' }]}
          />
        </div>
        {technologies.version_changes.length > 0 && (
          <div className="mt-4">
            <p className="mb-2 text-sm font-medium text-neutral-700">Version Changes</p>
            <DiffTable
              columns={[
                { key: 'name', header: 'Name', render: (item) => <span>{formatValue(item.name)}</span> },
                { key: 'from', header: 'From', render: (item) => <span className="text-error">{formatValue((item.from as Record<string, unknown>)?.version ?? (item.from as Record<string, unknown>)?.confidence)}</span> },
                { key: 'to', header: 'To', render: (item) => <span className="text-success">{formatValue((item.to as Record<string, unknown>)?.version ?? (item.to as Record<string, unknown>)?.confidence)}</span> },
              ]}
              data={technologies.version_changes}
              emptyMessage="No version changes"
            />
          </div>
        )}
      </Section>

      <Section title="Dependencies" description="Added, removed, and updated dependencies">
        <div className="grid gap-4 sm:grid-cols-3">
          <DiffCard
            title="Added"
            stats={[{ label: 'Dependencies', value: dependencies.added.length, variant: 'added' }]}
          />
          <DiffCard
            title="Removed"
            stats={[{ label: 'Dependencies', value: dependencies.removed.length, variant: 'removed' }]}
          />
          <DiffCard
            title="Updated"
            stats={[{ label: 'Dependencies', value: dependencies.updated.length, variant: 'changed' }]}
          />
        </div>
      </Section>

      <Section title="Files" description="Added, removed, and modified files">
        <div className="grid gap-4 sm:grid-cols-3">
          <DiffCard
            title="Added"
            stats={[{ label: 'Files', value: files.added.length, variant: 'added' }, { label: 'Total B', value: files.total_b }]}
          />
          <DiffCard
            title="Removed"
            stats={[{ label: 'Files', value: files.removed.length, variant: 'removed' }, { label: 'Total A', value: files.total_a }]}
          />
          <DiffCard
            title="Modified"
            stats={[{ label: 'Files', value: files.modified.length, variant: 'changed' }]}
          />
        </div>
      </Section>

      <Section title="Warnings" description="Warning comparison between analyses">
        <div className="grid gap-4 sm:grid-cols-4">
          <DiffCard
            title="Added"
            stats={[{ label: 'Warnings', value: warnings.added.length, variant: 'added' }]}
          />
          <DiffCard
            title="Resolved"
            stats={[{ label: 'Warnings', value: warnings.resolved.length, variant: 'removed' }]}
          />
          <DiffCard
            title="Persistent"
            stats={[{ label: 'Warnings', value: warnings.persistent.length, variant: 'neutral' }]}
          />
          <DiffCard
            title="Delta"
            stats={[{ label: 'Change', value: warnings.delta, variant: warnings.delta > 0 ? 'added' : warnings.delta < 0 ? 'removed' : 'neutral' }]}
          />
        </div>
      </Section>
    </div>
  )
}

function formatDelta(v: number | null): number {
  return v ?? 0
}

function deltaVariant(v: number | null): 'added' | 'removed' | 'neutral' {
  if (v === null || v === 0) return 'neutral'
  return v > 0 ? 'added' : 'removed'
}
