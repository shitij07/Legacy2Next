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

---

# Route Structure

```
<RootLayout>                    # Sidebar + Header + Outlet
  /
  └── /projects                 # ProjectsPage
  └── /projects/:projectId      # ProjectWorkspacePage
  └── /projects/:projectId/uploads   # UploadsPage
  └── /projects/:projectId/analysis/:analysisId/dashboard  # AnalysisDashboardPage
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
