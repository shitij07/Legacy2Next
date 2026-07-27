import { DashboardLayout } from '@/layouts/DashboardLayout'
import { ProjectsPage } from '@/features/projects/pages/ProjectsPage'
import { ProjectWorkspacePage } from '@/features/projects/pages/ProjectWorkspacePage'
import { UploadsPage } from '@/features/uploads/pages/UploadsPage'
import { AnalysisDashboardPage } from '@/features/analysis/pages/AnalysisDashboardPage'

export const projectsRoutes = {
  element: <DashboardLayout />,
  children: [
    { path: 'projects', element: <ProjectsPage /> },
    { path: 'projects/:projectId', element: <ProjectWorkspacePage /> },
    { path: 'projects/:projectId/uploads', element: <UploadsPage /> },
    { path: 'projects/:projectId/analyses/:analysisId', element: <AnalysisDashboardPage /> },
  ],
}
