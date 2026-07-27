import { useParams, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { PageHeader } from '@/components/layout/PageHeader'
import { Button } from '@/components/ui/button'
import { Section } from '@/components/shared/Section'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useProject } from '@/hooks/useProjects'
import { useAnalysisDashboard } from '@/hooks/useAnalysis'
import { DashboardSummary } from '../components/DashboardSummary'
import { MetricsCards } from '../components/MetricsCards'
import { RiskIndicator } from '../components/RiskIndicator'
import { TopFindings } from '../components/TopFindings'
import { RecommendedNextSteps } from '../components/RecommendedNextSteps'
import { FileLanguageChart } from '../components/Charts/FileLanguageChart'
import { TechnologyChart } from '../components/Charts/TechnologyChart'
import { DependencyEcosystemChart } from '../components/Charts/DependencyEcosystemChart'

export function AnalysisDashboardPage() {
  const { projectId, analysisId } = useParams<{ projectId: string; analysisId: string }>()
  const pid = Number(projectId)
  const aid = Number(analysisId)

  const { data: project, isLoading: projectLoading, isError: projectError } = useProject(pid)
  const { data: dashboard, isLoading: dashboardLoading, isError: dashboardError, error: dashboardErrorObj } = useAnalysisDashboard(aid)

  const isLoading = projectLoading || dashboardLoading

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Loading dashboard..." />
        <LoadingState variant="page" />
      </div>
    )
  }

  if (projectError || !project) {
    return (
      <div>
        <PageHeader title="Project not found" />
        <ErrorState
          title="Failed to load project"
          message="The project could not be found or you do not have access."
        />
      </div>
    )
  }

  if (dashboardError) {
    return (
      <div>
        <PageHeader title="Analysis Dashboard" />
        <ErrorState
          title="Failed to load dashboard"
          message={dashboardErrorObj?.message ?? 'An unexpected error occurred.'}
        />
      </div>
    )
  }

  if (!dashboard) {
    return (
      <div>
        <PageHeader title="Analysis Dashboard" />
        <ErrorState
          title="Analysis not found"
          message="The analysis could not be found or has not been completed yet."
        />
      </div>
    )
  }

  const { general, files, technologies, dependencies, warnings, metrics } = dashboard

  return (
    <div>
      <PageHeader
        title={`Analysis — ${project.name}`}
        description="Overview of the legacy codebase analysis results."
        actions={
          <Button variant="ghost" asChild>
            <Link to={`/projects/${pid}`}>
              <ArrowLeft className="h-4 w-4" aria-hidden="true" />
              Back to Project
            </Link>
          </Button>
        }
      />

      <div className="space-y-6">
        <DashboardSummary general={general} />

        <MetricsCards
          files={files}
          technologies={technologies}
          dependencies={dependencies}
          metrics={metrics}
        />

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <Section title="Codebase Composition">
              <div className="grid gap-6 md:grid-cols-2">
                <FileLanguageChart data={files.language_distribution} />
                <TechnologyChart data={technologies.category_distribution} />
              </div>
              <DependencyEcosystemChart data={dependencies.ecosystem_breakdown} />
            </Section>
          </div>

          <aside className="space-y-6">
            <RiskIndicator
              general={general}
              warnings={warnings}
              metrics={metrics}
              technologies={technologies}
              dependencies={dependencies}
            />
            <TopFindings warnings={warnings} />
          </aside>
        </div>

        <RecommendedNextSteps />
      </div>
    </div>
  )
}
