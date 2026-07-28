# Changelog

## 2026-07-28 — F12 Reports UI Frontend

### Added
- `frontend/src/features/reports/` — Full Reports feature module:
  - `types/index.ts` — ReportFormat, ReportStatus enums, ReportSummary, ReportResponse, ReportListResponse, ReportCreatePayload, ReportListParams interfaces
  - `api/index.ts` — generateReport(), getReports(), getReport(), deleteReport() with strong typing
  - `hooks/index.ts` — useReports (with placeholderData), useReport, useGenerateReport (with query invalidation), useDeleteReport (with optimistic removal)
  - `components/common/ReportStatusBadge.tsx` — Badge for GENERATING/READY/FAILED states
  - `components/common/ReportFormatBadge.tsx` — Badge for Markdown/JSON formats
  - `components/list/ReportsHeader.tsx` — Page header with Generate Report button
  - `components/list/ReportFilters.tsx` — Filter selects for format and status
  - `components/list/ReportTable.tsx` — Accessible table with title, format, status, created date, actions (view/delete)
  - `components/dialogs/GenerateReportDialog.tsx` — Modal with title input, analysis dropdown (fetched live), format select
  - `components/dialogs/DeleteReportDialog.tsx` — Confirmation dialog for delete
  - `components/viewer/MarkdownReport.tsx` — Renders report content via MarkdownRenderer (react-markdown + remark-gfm)
  - `components/viewer/JsonReport.tsx` — Pretty-prints JSON with syntax formatting and copy button
  - `components/viewer/ReportActions.tsx` — Back, Copy (clipboard), Download (blob), Delete buttons
  - `pages/ReportsListPage.tsx` — Paginated table with filters, empty/loading/error states, generate/delete dialogs
  - `pages/ReportViewerPage.tsx` — Full report viewer with lazy loading, format-aware rendering, action buttons
- `frontend/src/routes/projects.routes.tsx` — Added `/projects/:projectId/reports` and `/projects/:projectId/reports/:reportId` (viewer lazy-loaded)
- `frontend/src/features/projects/components/QuickActions.tsx` — Enabled "View Reports" quick action (was disabled)

### Changed
- `frontend/src/services/analysis.ts` — Added getProjectAnalyses() service function
- `frontend/src/hooks/useAnalysis.ts` — Added useProjectAnalyses() hook
- `docs/CHANGELOG.md`, `docs/Legacy2Next_PROJECT_STATE.md`, `docs/ROUTES.md`, `docs/API_INTEGRATION.md` — Updated for F12

## 2026-07-28 — B12 Backend Reports Foundation

### Added
- `backend/app/models/report.py` — Enhanced Report model with ReportFormat (MARKDOWN, JSON) and ReportStatus (GENERATING, READY, FAILED) enums, new fields (analysis_id, user_id, title, format, status, content, file_path, updated_at), SQLAlchemy relationships to Project/Analysis/User
- `backend/app/modules/reports/schemas.py` — ReportCreate, ReportResponse, ReportSummary, ReportListResponse, ReportFormat, ReportStatus
- `backend/app/modules/reports/repository.py` — create_report, get_report, update_report, delete_report, list_reports with pagination/sorting/filtering by project_id/analysis_id/status/format
- `backend/app/modules/reports/service.py` — generate_report (collects analysis data + AI outputs, generates Markdown/JSON), list_reports, get_report, delete_report with ownership validation
- `backend/app/modules/reports/routes.py` — POST /reports (201), GET /reports (paginated), GET /reports/{id}, DELETE /reports/{id} (204)
- `backend/alembic/versions/b2c3d4e5f6a7_add_report_model_fields.py` — Migration adding 8 columns, 3 FKs, 3 indexes to reports table
- `backend/tests/test_reports/test_generation.py` — 10 tests for Markdown and JSON generation
- `backend/tests/test_reports/test_routes.py` — 9 API tests (CRUD, auth, ownership, validation)
- `backend/app/main.py` — Registered reports_router

### Changed
- `backend/app/modules/reports/__init__.py` — Module package initialized
- `docs/CHANGELOG.md`, `docs/Legacy2Next_PROJECT_STATE.md`, `docs/ARCHITECTURE.md` — Updated for B12

## 2026-07-28 — M11 AI Workspace Frontend

### Added
- `frontend/src/lib/types.ts` — Added `AIResponse` type (analysis_id, feature, content, model), `AIFeatureSection` interface
- `frontend/src/services/ai.ts` — 6 API service functions:
  - `generateSummary()`, `generateArchitecture()`, `generateTechnicalDebt()`, `generateModernization()` (POST, no body)
  - `generateFileExplanation()` (POST /file/{fileId}/explain)
  - `generateModuleExplanation()` (POST /module, body: `{ module_path }`)
- `frontend/src/hooks/useAI.ts` — 6 mutation hooks (useGenerateSummary, useGenerateArchitecture, useGenerateTechnicalDebt, useGenerateModernization, useGenerateFileExplanation, useGenerateModuleExplanation) with retry (1), success/error toasts via sonner
- `frontend/src/features/ai/` — New AI Workspace feature module:
  - `pages/AIWorkspacePage.tsx` — Main page with 2-column card grid, project/analysis header, refresh, navigation to dashboard/explorer
  - `components/common/AIResponseCard.tsx` — Reusable card wrapper: generate button, loading skeleton, markdown display, copy/regenerate buttons, error state
  - `components/common/GenerateButton.tsx` — Sparkle icon button with loading state
  - `components/common/CopyButton.tsx` — Clipboard copy with check feedback
  - `components/common/MarkdownViewer.tsx` — Wraps existing MarkdownRenderer
  - `components/common/LoadingSkeleton.tsx` — Content skeleton for AI generation
  - `components/common/ErrorCard.tsx` — Error display with warning icon
  - `components/common/PromptHeader.tsx` — Title + description header
  - `components/common/SectionCard.tsx` — Card wrapper
  - `components/summary/SummarySection.tsx` — Project summary card
  - `components/architecture/ArchitectureSection.tsx` — Architecture analysis card
  - `components/technicalDebt/TechnicalDebtSection.tsx` — Technical debt card
  - `components/modernization/ModernizationSection.tsx` — Modernization recommendations card
  - `components/fileExplanation/FileExplanationSection.tsx` — File selector dialog + explanation card
  - `components/moduleExplanation/ModuleExplanationSection.tsx` — Module path input + explanation card
- `frontend/src/routes/projects.routes.tsx` — Added `/projects/:projectId/analyses/:analysisId/ai` route

### Changed
- `docs/ROUTES.md` — Added AI Workspace route to route table and structure diagram
- `docs/API_INTEGRATION.md` — Added AI endpoints table and data flow for AIWorkspacePage
- `docs/ARCHITECTURE.md` — Updated frontend folder structure with ai/ module, added AI workspace routes, updated version to 0.7.0, next milestones marked as complete

## 2026-07-28 — M10A Analysis Overview Dashboard + M7-M9 Frontend

### Added
- `frontend/` — New React 19 + TypeScript + Vite + TailwindCSS 4 application
- `frontend/src/services/projects.ts` — Projects API client (getProjects, getProject, createProject, updateProject, deleteProject)
- `frontend/src/services/upload.ts` — Uploads API client (getUploads, uploadFile multipart, deleteUpload, UPLOAD_CONSTRAINTS, formatFileSize)
- `frontend/src/services/analysis.ts` — Analysis API client (getUploadAnalyses, getAnalysisSummary, getAnalysisDashboard, getAnalysisMetrics, getAnalysisTechnologies, getAnalysisWarnings)
- `frontend/src/hooks/useProjects.ts` — React Query hooks (useProjects, useCreateProject, useDeleteProject with optimistic updates)
- `frontend/src/hooks/useUploads.ts` — React Query hooks (useUploads, useUploadFile, useDeleteUpload with optimistic updates + toasts, 10s refetch)
- `frontend/src/hooks/useUploadAnalysisStatus.ts` — Polling hook (5s interval, auto-stop on terminal status)
- `frontend/src/hooks/useAnalysis.ts` — React Query hooks for dashboard (useAnalysisDashboard, useAnalysisMetrics, useAnalysisTechnologies, useAnalysisWarnings, useAnalysisDashboardEnabled)
- `frontend/src/features/projects/` — Projects CRUD pages and components (ProjectCard, ProjectList, CreateProjectDialog, ProjectWorkspacePage, ProjectMetadata, ProjectStats, QuickActions, RecentActivity)
- `frontend/src/features/uploads/` — Upload pages and components (UploadDropzone, UploadCard, UploadList, UploadsPage, 5 processing states)
- `frontend/src/features/analysis/` — Analysis dashboard page and components (DashboardSummary, MetricsCards, RiskIndicator, TopFindings, RecommendedNextSteps, FileLanguageChart, TechnologyChart, DependencyEcosystemChart)
- `frontend/src/lib/types.ts` — 14+ TypeScript dashboard types (DashboardResponse, GeneralSection, FilesSection, TechnologiesSection, DependenciesSection, WarningsSection, MetricsSection, RiskLevel, etc.)
- `frontend/src/routes/index.tsx` — React Router 7 config-based routes (/projects, /projects/:projectId, /projects/:projectId/uploads, /projects/:projectId/analysis/:analysisId/dashboard)
- `frontend/src/layouts/` — RootLayout with sidebar navigation and header
- `frontend/src/lib/queryKeys.ts` — React Query key factory
- `docs/ROUTES.md` — Frontend routes documentation
- `docs/API_INTEGRATION.md` — Dashboard backend endpoints consumed

### Changed
- `docs/Legacy2Next_PROJECT_STATE.md` — Updated to v0.6.0, Session 21, all milestones updated, repo structure includes frontend
- `docs/Legacy2Next_MASTER_PLAN.md` — Development milestones table updated with status column, Phase 5 updated to reflect frontend completion
- `docs/ARCHITECTURE.md` — Version bumped to 0.6.0, current milestone updated to M10B
- `frontend/src/features/projects/components/QuickActions.tsx` — Enabled Upload Codebase navigation

### Architecture
- Feature-based frontend folder structure (features/projects, features/uploads, features/analysis) mirrors backend module organization
- TanStack Query for server state with optimistic updates on create/delete
- Sonner for toast notifications on upload/delete success/error
- All pages implement 4 UI states (loading skeleton, empty state with CTA, error state with retry, data state)
- Upload processing uses polling (5s interval) that auto-stops on terminal status
- Dashboard charts use Recharts (sector donut for files, bar for technologies, pie for dependencies)
- Routes use React Router 7 layout routes with RootLayout wrapping all pages

## 2026-07-27 — M6B AI Module

### Added
- `backend/app/integrations/ai/provider.py` — `AIProvider` ABC + `LiteLLMProvider` wrapping `litellm.completion()`:
  - `generate(prompt, system_prompt, temperature, max_tokens) → str`
  - Supports OpenAI, Anthropic, Gemini, Ollama through provider/model config
  - Timeout and error handling via `LiteLLMException`
- `backend/app/modules/ai/schemas.py` — `ModuleExplanationRequest`, `GenerationResponse`
- `backend/app/modules/ai/context_builder.py` — `ContextBuilder` with 6 typed frozen dataclasses:
  - `SummaryContext`, `FileExplanationContext`, `ModuleExplanationContext`, `ArchitectureContext`, `TechnicalDebtContext`, `ModernizationContext`
  - Read-only loading from analysis repository; file contents for `file_explanation`
- `backend/app/modules/ai/prompt_loader.py` — `PromptLoader`:
  - Jinja2 `Environment` + `FileSystemLoader` + compiled template cache
  - Accepts typed dataclass contexts (converts via `dataclasses.asdict`)
- `backend/app/modules/ai/service.py` — `AIService` ABC + `DefaultAIService`:
  - Orchestrates `ContextBuilder` → `PromptLoader` → `AIProvider`
  - Ownership validation via FK chain (Analysis → Upload → Project → user_id)
  - All 6 generation methods return `GenerationResponse`
- `backend/app/modules/ai/routes.py` — 6 POST endpoints:
  - `POST /ai/analysis/{id}/summary` — project overview
  - `POST /ai/analysis/{id}/file/{file_id}/explain` — file explanation
  - `POST /ai/analysis/{id}/module` — module explanation
  - `POST /ai/analysis/{id}/architecture` — architecture description
  - `POST /ai/analysis/{id}/technical-debt` — technical debt analysis
  - `POST /ai/analysis/{id}/modernization` — modernization recommendations
- `backend/app/modules/ai/prompts/*.jinja2` — 6 Jinja2 prompt templates:
  - `summary.jinja2`, `file_explanation.jinja2`, `module_explanation.jinja2`
  - `architecture.jinja2`, `technical_debt.jinja2`, `modernization.jinja2`
- `backend/tests/test_ai/` — 72 comprehensive tests:
  - `test_provider.py` (9 tests) — AIProvider ABC, LiteLLMProvider generate/errors/timeout
  - `test_prompt_loader.py` (10 tests) — load, render, cache, custom dir, dataclass, missing template
  - `test_context_builder.py` (7 tests) — all 6 context types + missing data
  - `test_service.py` (14 tests) — AIService ABC, ownership, all 6 features, provider/prompt failures
  - `test_routes.py` (21 tests) — all 6 endpoints, auth, ownership, DTO mapping, 422 validation

### Changed
- `backend/app/core/config.py` — Added 7 AI settings: `AI_ENABLED`, `AI_PROVIDER`, `AI_MODEL`, `AI_API_KEY`, `AI_TEMPERATURE`, `AI_MAX_TOKENS`, `AI_TIMEOUT_SECONDS`
- `backend/app/core/dependencies.py` — Added `get_ai_provider()` and `get_ai_service()` factories
- `backend/app/main.py` — Registered `ai_router`
- `backend/.env.example` — Added AI env vars
- `backend/pyproject.toml` — Added `litellm>=1.40.0`, `Jinja2>=3.1.0`
- `docs/ARCHITECTURE.md` — Added AI Module section (provider abstraction, prompt system, ContextBuilder, PromptLoader, generation flow), updated version to 0.5.0, updated Planned/Evolution
- `docs/Legacy2Next_PROJECT_STATE.md` — Updated to v0.5.0, Session 20, M6 complete, 537 tests, next task redirect to M7

### Architecture
- Provider abstraction: `AIProvider (ABC) ← LiteLLMProvider → litellm.completion()`
- Routes depend on `AIService` ABC — injected via `get_ai_service()` dependency factory
- Service depends on `AIProvider` ABC — provider swap = config change + optional new class
- ContextBuilder reads analysis repository (read-only) — never exposes ORM models
- PromptLoader owns Jinja2 rendering — AIProvider knows nothing about prompts
- All endpoints stateless — no persistence, no caching, no streaming
- Ownership validation via same FK-chain walk as analysis query_service

### Testing
- 537 tests total (465 existing + 72 new AI tests), all passing, zero regressions
- All AI tests mock the provider — no real LLM calls in test suite

## 2026-07-27 — M5.4B Performance & Optimisation

### Added
- `backend/alembic/versions/a1b2c3d4e5f6_add_m54_covering_indexes.py` — 4 covering indexes:
  - `ix_analysis_files_language` on `analysis_files(language)`
  - `ix_analysis_files_is_directory` on `analysis_files(is_directory)`
  - `ix_analysis_warnings_detector` on `analysis_warnings(detector_name)`
  - `ix_dependencies_type` on `dependencies(type)`
- Configurable pagination limits in `app/core/config.py`:
  - `MAX_PAGE_SIZE_SUBRESOURCE` (default 500, max 1000) — files, dependencies, warnings
  - `MAX_PAGE_SIZE_LIST` (default 50, max 200) — project/upload analysis listings
  - `DEFAULT_PAGE_SIZE_SUBRESOURCE` (default 50)
  - `DEFAULT_PAGE_SIZE_LIST` (default 20)
  - `SLOW_SERVICE_THRESHOLD_MS` (default 1000ms)

### Changed
- `backend/app/modules/analysis/dashboard_service.py` — `get_dashboard()` uses `time.perf_counter()` with WARNING/INFO threshold logging
- `backend/app/modules/analysis/query_service.py` — `get_analysis_summary()` uses `time.perf_counter()` with WARNING/INFO threshold logging
- `docs/ARCHITECTURE.md` — Removed caching section, updated DTO/caching references
- `docs/Legacy2Next_PROJECT_STATE.md` — Updated session, removed cache references, corrected test counts

### Removed
- `backend/app/core/cache.py` — Out-of-scope caching layer
- `backend/tests/test_core/` — Cache tests and __init__.py
- `backend/tests/test_analysis/conftest.py` — Out-of-scope cache fixture

### Architecture
- Scope strictly limited to: covering indexes, configurable pagination limits, perf_counter() timing, threshold logging
- No caching — deferred to future milestone
- All existing tests preserved and passing at 465

## 2026-07-26 — M5.3B Dashboard Aggregation

### Added
- `backend/app/modules/analysis/dashboard_service.py` — `DashboardService` with 6 section builders:
  - `GeneralSection` (status, file stats, language count, file size, project name)
  - `FilesSection` (top 10 by line count, directory listing)
  - `TechnologiesSection` (all detected techs grouped by type/detector)
  - `DependenciesSection` (total count, ecosystem breakdown, top dependencies)
  - `WarningsSection` (total warnings, breakdown by detector, warning distribution)
  - `MetricsSection` (all metrics with key, label, value, type; graphable insights)
- `backend/app/modules/analysis/dashboard_schemas.py` — 9 nested DTOs for dashboard response
- `backend/app/modules/analysis/repository.py` — 9 new aggregation methods (GROUP BY, COUNT, ORDER BY LIMIT)
- `backend/app/modules/analysis/routes.py` — `GET /analysis/{analysis_id}/dashboard`
- `backend/tests/test_analysis/test_dashboard_api.py` — 51 tests covering all sections, empty data, ownership, DTO mapping, determinism, no-writes, serialization

### Changed
- `docs/ARCHITECTURE.md` — Dashboard section, updated module status, component table, milestone evolution
- `docs/Legacy2Next_PROJECT_STATE.md` — M5.3B complete, 465 total tests

### Architecture
- DashboardService reads AnalysisResults via repository — no pipeline, no detectors, no writes
- All aggregation happens in Python, not SQL — 9 dedicated repository methods return raw tuples/ORM entities
- Ownership validation walks FK chain: Analysis → Upload → Project → user_id
- DTOs isolate dashboard response from ORM — 9 nested Pydantic models with `from_attributes=True`
- Deterministic output with sorted lists, stable labels, no mutable defaults

## 2026-07-26 — M5.2B Shared Query Infrastructure

### Added
- `backend/app/modules/analysis/query_options.py` — `QueryOptions`, `Page[T]`, `FileFilter`, `DependencyFilter`, `WarningFilter`, `apply_sort()`
- `backend/tests/test_analysis/test_query_options.py` — 7 tests (was 0 new — incorporated into query_api tests)

### Changed
- `backend/app/modules/analysis/repository.py` — Refactored all paginated repository methods to accept `(filter, opts)` and return `Page[ORM]`
- `backend/app/modules/analysis/query_service.py` — Constructs filter + opts and delegates to repository
- `backend/app/modules/analysis/routes.py` — Added `search` query param to files, dependencies, warnings endpoints (ILIKE)
- `backend/tests/test_analysis/test_query_api.py` — 76 tests (was 69) — new search/filter/edge-case tests
- `docs/ARCHITECTURE.md` — QueryOptions section, updated component table, milestone evolution
- `docs/Legacy2Next_PROJECT_STATE.md` — M5.2B complete, 414 total tests

### Architecture
- QueryOptions and *Filter dataclasses decouple route params from repository queries
- apply_sort() maps field names to model columns (whitelist-based, no SQL injection)
- Page[T] is the sole pagination container — used by all paginated endpoints
- All existing tests preserved and passing

## 2026-07-26 — M5.1B Analysis Retrieval

### Added
- `backend/app/modules/analysis/query_service.py` — `AnalysisQueryService` with 8 retrieval methods
- `backend/app/modules/analysis/schemas.py` — 8 DTOs + `PaginatedResponse[T]`
- `backend/app/modules/analysis/routes.py` — `GET /analysis/{id}`, `GET /analysis/{id}/files`, `GET /analysis/{id}/technologies`, `GET /analysis/{id}/dependencies`, `GET /analysis/{id}/metrics`, `GET /analysis/{id}/warnings`, `GET /analysis/project/{project_id}`, `GET /analysis/upload/{upload_id}`
- `backend/app/modules/analysis/repository.py` — 9 paginated/filtered read methods
- `backend/tests/test_analysis/test_query_api.py` — 69 tests

### Changed
- `docs/ARCHITECTURE.md` — AnalysisQueryService section, updated folder structure, component table, test listing, milestone evolution
- `docs/Legacy2Next_PROJECT_STATE.md` — M5.1B complete, 407 total tests

### Architecture
- Read/write separation: `AnalysisQueryService` independent from `AnalysisService`
- Ownership validation walks FK chain
- DTOs isolate API from ORM — all 8 responses are Pydantic models with `from_attributes=True`

## 2026-07-26 — M4.9B API Integration

### Added
- `backend/app/modules/analysis/service.py` — `run_analysis()` with full orchestration
- `backend/app/modules/analysis/schemas.py` — `AnalysisResponse`
- `backend/app/modules/analysis/routes.py` — `POST /analysis/{upload_id}`
- `backend/app/main.py` — Registered `analysis_router`
- `backend/tests/test_analysis/test_api_integration.py` — 27 tests

### Architecture
- Service is the sole transaction owner
- Best-effort FAILED persistence after rollback
- Route contains zero business logic

## 2026-07-26 — M4.8B AnalysisWriter

### Added
- `backend/app/modules/analysis/writer.py` — `AnalysisWriter` + `PersistenceResult`
- `backend/app/models/analysis_warning.py` — `AnalysisWarning` model
- `backend/app/modules/analysis/repository.py` — 6 batch helpers
- `backend/tests/test_analysis/test_writer.py` — 26 tests

### Changed
- `backend/app/models/metric.py` — `value` widened to `BigInteger` (nullable) + `value_str` (Text)
- `backend/app/models/dependency.py` — Added `source_files` JSON column with `source_files_list` property

### Architecture
- Writer never commits, never rollbacks — caller owns the transaction boundary
- Metric invariant: exactly one of `value` or `value_str` populated

## 2026-07-26 — M4.7B AnalysisPipeline

### Added
- `backend/app/modules/analysis/pipeline.py` — `AnalysisPipeline` class orchestrating the full analysis workflow:
  - `DiscoveryEngine.discover()` → detectors (Language, Framework, Dependency) → `MetricsCollector`
  - Constructor injection: `engine`, `detectors`, `metrics_collector`
  - Sequential execution, deterministic output, timing recorded
  - Failure isolation: `DiscoveryException` propagates; all other exceptions caught and wrapped as error `DetectorResult`
- `backend/tests/test_analysis/test_pipeline.py` — 27 tests across 7 test classes covering construction, execution order, failure handling, warning preservation, timestamps, determinism, and boundary enforcement

### Changed
- `backend/app/modules/analysis/types.py` — Added `DetectorWarning(detector_name, message)` frozen dataclass; added `warnings: tuple[DetectorWarning, ...]` field to `DetectorResult` (default `()`, zero breakage)
- `docs/ARCHITECTURE.md` — Added AnalysisPipeline orchestration section, updated folder structure and milestone map
- `docs/Legacy2Next_PROJECT_STATE.md` — Updated milestone progress, session log, current state

### Architecture
- AnalysisPipeline is a pure coordinator — no detection, no aggregation, no persistence
- Constructor injection with explicit types
- DetectorWarning is a structured dataclass (not a string)
- Failure isolation: DiscoveryException propagates, all other caught and wrapped
- MetricsCollector receives intermediate AnalysisResults, appends its DetectorResult

## 2026-07-26 — M4.6B MetricsCollector

### Added
- `backend/app/modules/analysis/metrics_collector.py` — `MetricsCollector` class with pure aggregation of project metrics from `AnalysisResults`:
  - `project.total_files`, `project.total_file_size`
  - `languages.count`, `languages.primary`
  - `frameworks.count`
  - `dependencies.count`, `dependencies.<ecosystem>` (dynamic, alphabetically sorted)
  - `manifests.count`
- `backend/app/modules/analysis/metric_keys.py` — `MetricKey(StrEnum)` with stable constants for all fixed metric keys
- `backend/tests/test_analysis/test_metrics_collector.py` — 51 tests across 14 test classes covering all metrics, edge cases, determinism, and result integrity

### Changed
- `backend/app/modules/analysis/types.py` — `DetectedMetric.value` widened from `int` to `int | str` to support string-valued metrics (e.g., `languages.primary`)
- `docs/ARCHITECTURE.md` — Added MetricsCollector aggregation stage documentation, updated analysis module status
- `docs/Legacy2Next_PROJECT_STATE.md` — Updated metrics collector progress, next tasks, test counts

### Architecture
- MetricsCollector reads `AnalysisResults` only — no `DiscoveryContext`, no file I/O, no network, no parsing
- Deterministic output: stable metric ordering, alphabetically sorted ecosystems, identical results for identical input
- O(n) in detector output size — each result visited once
