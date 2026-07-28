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
                                                      └──→ AnalysisDashboardPage
                                                               ├──→ GET /analysis/{id}/dashboard
                                                               ├──→ GET /analysis/{id}/metrics
                                                               ├──→ GET /analysis/{id}/technologies
                                                               └──→ GET /analysis/{id}/warnings
```

---

# Authentication

All endpoints require a Bearer JWT token sent via the `Authorization` header. The frontend stores the token in a Zustand store and attaches it via an Axios/`fetch` interceptor.

---

# Polling Strategy

- **Upload analysis status**: Polls `GET /analysis/{id}` every 5 seconds. Auto-stops when status is terminal (`COMPLETED`, `COMPLETED_WITH_ERRORS`, `FAILED`).
- **Uploads list**: Refetches every 10 seconds via `refetchInterval: 10_000` in `useUploads()` to catch newly completed analyses.
