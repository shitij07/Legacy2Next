import { useParams } from 'react-router-dom'
import { PageHeader } from '@/components/layout/PageHeader'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Section } from '@/components/shared/Section'
import { useProject } from '@/hooks/useProjects'
import { ProjectStats } from '../components/ProjectStats'
import { QuickActions } from '../components/QuickActions'
import { RecentActivity } from '../components/RecentActivity'
import { ProjectMetadata } from '../components/ProjectMetadata'

export function ProjectWorkspacePage() {
  const { projectId } = useParams<{ projectId: string }>()
  const id = Number(projectId)
  const { data: project, isLoading, isError, error } = useProject(id)

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Loading project..." />
        <LoadingState variant="page" />
      </div>
    )
  }

  if (isError) {
    return (
      <div>
        <PageHeader title="Project not found" />
        <ErrorState
          title="Failed to load project"
          message={error?.message ?? 'An unexpected error occurred.'}
        />
      </div>
    )
  }

  if (!project) {
    return (
      <div>
        <PageHeader title="Project not found" />
        <ErrorState
          title="Project not found"
          message="The project you are looking for does not exist or has been deleted."
        />
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title={project.name}
        description={project.description ?? undefined}
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Section title="Overview">
            <ProjectStats
              uploadCount={0}
              analysisCount={0}
              fileCount={project.file_count}
              warningCount={0}
            />
          </Section>

          <Section title="Quick Actions">
            <QuickActions projectId={project.id} />
          </Section>

          <Section title="Recent Activity">
            <RecentActivity />
          </Section>
        </div>

        <aside className="space-y-6">
          <ProjectMetadata project={project} />
        </aside>
      </div>
    </div>
  )
}
