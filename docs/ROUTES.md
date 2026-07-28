# Frontend Routes

**Project:** Legacy2Next
**Last Updated:** 2026-07-28

---

# Route Table

| Path | Page Component | Auth | Description |
|------|---------------|------|-------------|
| `/` | Redirect to `/projects` | Yes | Root redirect |
| `/projects` | `ProjectsPage` | Yes | List all projects with CRUD dialog |
| `/projects/:projectId` | `ProjectWorkspacePage` | Yes | Project detail with metadata, stats, quick actions, activity |
| `/projects/:projectId/uploads` | `UploadsPage` | Yes | Upload files with dropzone, view uploads list, processing status |
| `/projects/:projectId/analysis/:analysisId/dashboard` | `AnalysisDashboardPage` | Yes | Analysis overview dashboard with summary, metrics, charts, warnings |
| `/projects/:projectId/analysis/:analysisId/explorer` | `AnalysisExplorerPage` | Yes | Browse analysis data: files, technologies, dependencies, warnings, metrics |
| `/projects/:projectId/analysis/:analysisId/ai` | `AIWorkspacePage` | Yes | AI-powered insights: summary, architecture, technical debt, modernization, file/module explanations |
| `/projects/:projectId/reports` | `ReportsListPage` | Yes | Paginated report list with filters, generate/delete |
| `/projects/:projectId/reports/:reportId` | `ReportViewerPage` (lazy) | Yes | Full report viewer with Markdown/JSON rendering |
| `/projects/:projectId/comparison` | `ComparisonPage` | Yes | Compare two analyses with selectors, dashboard, and history |
| `/projects/:projectId/comparison/:comparisonId` | `ComparisonDetailPage` (lazy) | Yes | Full comparison detail with all diff sections |

---

# Route Structure

```
<RootLayout>                    # Sidebar + Header + Outlet
  /
  └── /projects                 # ProjectsPage
  └── /projects/:projectId      # ProjectWorkspacePage
  └── /projects/:projectId/uploads   # UploadsPage
  └── /projects/:projectId/analysis/:analysisId/dashboard  # AnalysisDashboardPage
  └── /projects/:projectId/analysis/:analysisId/explorer   # AnalysisExplorerPage
  └── /projects/:projectId/analysis/:analysisId/ai         # AIWorkspacePage
  └── /projects/:projectId/reports             # ReportsListPage
  └── /projects/:projectId/reports/:reportId   # ReportViewerPage (lazy)
  └── /projects/:projectId/comparison          # ComparisonPage
  └── /projects/:projectId/comparison/:comparisonId  # ComparisonDetailPage (lazy)
```

---

# Navigation

- **RootLayout** renders a sidebar with links to `/projects`
- **QuickActions** component (on workspace page) has an "Upload Codebase" button navigating to `/projects/:projectId/uploads`
- **UploadCard** navigates to `/projects/:projectId/analysis/:analysisId/dashboard` when analysis is completed
- All routes are protected by authentication (handled by the auth provider wrapping the router)

---

# State Handling

Every page component implements 4 states:

1. **Loading** — Skeleton/spinner shown while data fetches
2. **Empty** — Empty state with call-to-action (e.g., "Create your first project")
3. **Error** — Error message with retry button
4. **Data** — Normal rendered content
