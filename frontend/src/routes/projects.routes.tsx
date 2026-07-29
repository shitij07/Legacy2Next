import { lazy } from 'react'
import { DashboardLayout } from '@/layouts/DashboardLayout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { ProjectsPage } from '@/features/projects/pages/ProjectsPage'

const ProjectWorkspacePage = lazy(() =>
  import('@/features/projects/pages/ProjectWorkspacePage').then((m) => ({
    default: m.ProjectWorkspacePage,
  })),
)
const UploadsPage = lazy(() =>
  import('@/features/uploads/pages/UploadsPage').then((m) => ({ default: m.UploadsPage })),
)
const AnalysisDashboardPage = lazy(() =>
  import('@/features/analysis/pages/AnalysisDashboardPage').then((m) => ({
    default: m.AnalysisDashboardPage,
  })),
)
const AnalysisExplorerPage = lazy(() =>
  import('@/features/analysis/pages/AnalysisExplorerPage').then((m) => ({
    default: m.AnalysisExplorerPage,
  })),
)
const AIWorkspacePage = lazy(() =>
  import('@/features/ai/pages/AIWorkspacePage').then((m) => ({ default: m.AIWorkspacePage })),
)
const ReportsListPage = lazy(() =>
  import('@/features/reports/pages/ReportsListPage').then((m) => ({ default: m.ReportsListPage })),
)
const ReportViewerPage = lazy(() =>
  import('@/features/reports/pages/ReportViewerPage').then((m) => ({ default: m.ReportViewerPage })),
)
const ComparisonPage = lazy(() =>
  import('@/features/comparison/pages/ComparisonPage').then((m) => ({ default: m.ComparisonPage })),
)
const ComparisonDetailPage = lazy(() =>
  import('@/features/comparison/pages/ComparisonDetailPage').then((m) => ({
    default: m.ComparisonDetailPage,
  })),
)

export const projectsRoutes = {
  element: <ProtectedRoute />,
  children: [
    {
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
    { path: 'projects/:projectId/comparison', element: <ComparisonPage /> },
    { path: 'projects/:projectId/comparison/:comparisonId', element: <ComparisonDetailPage /> },
      ],
    },
  ],
}
