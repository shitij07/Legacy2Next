import { lazy } from 'react'
import { DashboardLayout } from '@/layouts/DashboardLayout'
import { ProjectsPage } from '@/features/projects/pages/ProjectsPage'
import { ProjectWorkspacePage } from '@/features/projects/pages/ProjectWorkspacePage'
import { UploadsPage } from '@/features/uploads/pages/UploadsPage'
import { AnalysisDashboardPage } from '@/features/analysis/pages/AnalysisDashboardPage'
import { AnalysisExplorerPage } from '@/features/analysis/pages/AnalysisExplorerPage'
import { AIWorkspacePage } from '@/features/ai/pages/AIWorkspacePage'
import { ReportsListPage } from '@/features/reports/pages/ReportsListPage'

const ReportViewerPage = lazy(() =>
  import('@/features/reports/pages/ReportViewerPage').then((m) => ({ default: m.ReportViewerPage })),
)

export const projectsRoutes = {
  element: <DashboardLayout />,
  children: [
    { path: 'projects', element: <ProjectsPage /> },
    { path: 'projects/:projectId', element: <ProjectWorkspacePage /> },
    { path: 'projects/:projectId/uploads', element: <UploadsPage /> },
    { path: 'projects/:projectId/analyses/:analysisId', element: <AnalysisDashboardPage /> },
    { path: 'projects/:projectId/analyses/:analysisId/explorer', element: <AnalysisExplorerPage /> },
    { path: 'projects/:projectId/analyses/:analysisId/ai', element: <AIWorkspacePage /> },
    { path: 'projects/:projectId/reports', element: <ReportsListPage /> },
    { path: 'projects/:projectId/reports/:reportId', element: <ReportViewerPage /> },
  ],
}
