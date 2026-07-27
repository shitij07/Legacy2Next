import { MetricCard } from '@/components/shared/MetricCard'

interface ProjectStatsProps {
  uploadCount: number
  analysisCount: number
  fileCount: number
  warningCount: number
  isLoading?: boolean
}

export function ProjectStats({
  uploadCount,
  analysisCount,
  fileCount,
  warningCount,
  isLoading,
}: ProjectStatsProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard label="Uploads" value={uploadCount} isLoading={isLoading} />
      <MetricCard label="Analyses" value={analysisCount} isLoading={isLoading} />
      <MetricCard label="Files" value={fileCount} isLoading={isLoading} />
      <MetricCard label="Warnings" value={warningCount} isLoading={isLoading} />
    </div>
  )
}
