# API Integration — Frontend to Backend

**Project:** Legacy2Next
**Last Updated:** 2026-07-28

---

# Backend Endpoints Consumed by Frontend

## Projects

| Method | Endpoint | Service Function | Hook | Description |
|--------|----------|-----------------|------|-------------|
| `GET` | `/projects` | `getProjects()` | `useProjects()` | List owned projects |
| `GET` | `/projects/{id}` | `getProject()` | `useProjects()` | Get single project |
| `POST` | `/projects` | `createProject()` | `useCreateProject()` | Create project |
| `PATCH` | `/projects/{id}` | `updateProject()` | `useUpdateProject()` | Update project |
| `DELETE` | `/projects/{id}` | `deleteProject()` | `useDeleteProject()` | Delete project |

## Uploads

| Method | Endpoint | Service Function | Hook | Description |
|--------|----------|-----------------|------|-------------|
| `GET` | `/projects/{id}/uploads` | `getUploads()` | `useUploads()` | List project uploads |
| `POST` | `/projects/{id}/uploads` | `uploadFile()` | `useUploadFile()` | Upload files (multipart) |
| `DELETE` | `/uploads/{id}` | `deleteUpload()` | `useDeleteUpload()` | Delete upload |

## Analysis

| Method | Endpoint | Service Function | Hook | Description |
|--------|----------|-----------------|------|-------------|
| `GET` | `/analysis/{id}` | `getAnalysisSummary()` | `useUploadAnalysisStatuses()` | Get analysis summary |
| `GET` | `/analysis/{id}/dashboard` | `getAnalysisDashboard()` | `useAnalysisDashboard()` | Get full dashboard response |
| `GET` | `/analysis/{id}/metrics` | `getAnalysisMetrics()` | `useAnalysisMetrics()` | Get analysis metrics |
| `GET` | `/analysis/{id}/technologies` | `getAnalysisTechnologies()` | `useAnalysisTechnologies()` | Get detected technologies |
| `GET` | `/analysis/{id}/warnings` | `getAnalysisWarnings()` | `useAnalysisWarnings()` | Get analysis warnings |

## Analysis Details

| Method | Endpoint | Service Function | Hook | Description |
|--------|----------|-----------------|------|-------------|
| `GET` | `/analysis/{id}/files` | `getAnalysisFiles()` | `useAnalysisFiles()` | List files with pagination, search, sort, filters |
| `GET` | `/analysis/{id}/dependencies` | `getAnalysisDependencies()` | `useAnalysisDependencies()` | List dependencies with pagination, search, sort, filters |

## AI

| Method | Endpoint | Service Function | Hook | Description |
|--------|----------|-----------------|------|-------------|
| `POST` | `/ai/analysis/{id}/summary` | `generateSummary()` | `useGenerateSummary()` | AI-generated project overview |
| `POST` | `/ai/analysis/{id}/architecture` | `generateArchitecture()` | `useGenerateArchitecture()` | AI architecture analysis |
| `POST` | `/ai/analysis/{id}/technical-debt` | `generateTechnicalDebt()` | `useGenerateTechnicalDebt()` | AI technical debt assessment |
| `POST` | `/ai/analysis/{id}/modernization` | `generateModernization()` | `useGenerateModernization()` | AI modernization recommendations |
| `POST` | `/ai/analysis/{id}/file/{fileId}/explain` | `generateFileExplanation()` | `useGenerateFileExplanation()` | AI file explanation |
| `POST` | `/ai/analysis/{id}/module` | `generateModuleExplanation()` | `useGenerateModuleExplanation()` | AI module explanation |

All AI endpoints return `{ analysis_id, feature, content, model }`.

## Reports

| Method | Endpoint | Service Function | Hook | Description |
|--------|----------|-----------------|------|-------------|
| `POST` | `/reports` | `generateReport()` | `useGenerateReport()` | Create & generate report (body: `{ project_id, analysis_id, format, title }`) |
| `GET` | `/reports` | `getReports()` | `useReports()` | List reports (query: `project_id`, `analysis_id`, `status`, `format`, `page`, `size`) |
| `GET` | `/reports/{id}` | `getReport()` | `useReport()` | Get report details with content |
| `DELETE` | `/reports/{id}` | `deleteReport()` | `useDeleteReport()` | Delete a report |

---

# Data Flow

```
ProjectsPage ──→ GET /projects ──→ Project list with pagination
     │
     └──→ ProjectWorkspacePage ──→ GET /projects/{id}
              │
              ├──→ QuickActions → navigate to uploads
              │
              └──→ RecentActivity → GET /analysis/upload/{upload_id}
                        │
                        └──→ UploadsPage ──→ GET /projects/{id}/uploads
                                 │
                                 ├──→ UploadDropzone → POST /projects/{id}/uploads (multipart)
                                 │
                                 └──→ UploadCard (polling) ──→ GET /analysis/{id}
                                            │
                                            └──→ navigate to dashboard
                                                      │
                                                      ├──→ AnalysisDashboardPage
                                                      │      ├──→ GET /analysis/{id}/dashboard
                                                      │      ├──→ GET /analysis/{id}/metrics
                                                      │      ├──→ GET /analysis/{id}/technologies
                                                      │      └──→ GET /analysis/{id}/warnings
                                                      │
                                                      ├──→ AnalysisExplorerPage
                                                      │      ├──→ GET /analysis/{id}/files
                                                      │      ├──→ GET /analysis/{id}/technologies
                                                      │      ├──→ GET /analysis/{id}/dependencies
                                                      │      ├──→ GET /analysis/{id}/warnings
                                                      │      └──→ GET /analysis/{id}/metrics
                                                      │
                                                      └──→ AIWorkspacePage
                                                             ├──→ POST /ai/analysis/{id}/summary
                                                             ├──→ POST /ai/analysis/{id}/architecture
                                                             ├──→ POST /ai/analysis/{id}/technical-debt
                                                             ├──→ POST /ai/analysis/{id}/modernization
                                                             ├──→ POST /ai/analysis/{id}/file/{fileId}/explain
                                                             └──→ POST /ai/analysis/{id}/module

                                               ReportsPage (future)
                                                       ├──→ POST /reports
                                                       ├──→ GET /reports?project_id=...
                                                       ├──→ GET /reports/{id}
                                                       └──→ DELETE /reports/{id}
```

---

## Comparison

### `POST /comparison` — Create comparison

- **Body:** `{ project_id, analysis_a_id, analysis_b_id }`
- **Response:** `ComparisonResponse` with `comparison_data` (technologies, dependencies, files, warnings, metrics diffs)
- **Service:** `compareAnalyses()` → `features/comparison/api/index.ts`
- **Hook:** `useCreateComparison(projectId)` → `features/comparison/hooks/index.ts`

### `GET /comparison/{comparison_id}` — Get comparison

- **Response:** `ComparisonResponse`
- **Service:** `getComparison()` → `features/comparison/api/index.ts`
- **Hook:** `useComparison(comparisonId)` → `features/comparison/hooks/index.ts`

### `GET /comparison/project/{project_id}` — List comparison history

- **Params:** `page`, `size`
- **Response:** `ComparisonListResponse`
- **Service:** `getComparisonHistory()` → `features/comparison/api/index.ts`
- **Hook:** `useComparisonHistory(params)` → `features/comparison/hooks/index.ts`

### `DELETE /comparison/{comparison_id}` — Delete comparison

- **Response:** `204 No Content`
- **Service:** `deleteComparison()` → `features/comparison/api/index.ts`
- **Hook:** `useDeleteComparison(projectId, params)` → `features/comparison/hooks/index.ts`

---

# Authentication

All endpoints require a Bearer JWT token sent via the `Authorization` header. The frontend stores the token in a Zustand store and attaches it via an Axios/`fetch` interceptor.

---

# Polling Strategy

- **Upload analysis status**: Polls `GET /analysis/{id}` every 5 seconds. Auto-stops when status is terminal (`COMPLETED`, `COMPLETED_WITH_ERRORS`, `FAILED`).
- **Uploads list**: Refetches every 10 seconds via `refetchInterval: 10_000` in `useUploads()` to catch newly completed analyses.
