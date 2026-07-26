# Changelog

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
- Pipeline is a pure coordinator — no detection, no aggregation, no persistence
- Structured `DetectorWarning` (not raw strings) enables grouping by detector and future severity support
- Warnings preserved per-detector — pipeline never merges or rewrites them
- All 285 tests passing in test_analysis

## 2026-07-26 — M4.8B AnalysisWriter

### Added
- `backend/app/models/analysis_warning.py` — `AnalysisWarning` model (analysis_id FK, detector_name, message)
- `backend/app/modules/analysis/writer.py` — `AnalysisWriter` class + `PersistenceResult` dataclass
- `backend/app/modules/analysis/repository.py` — 6 batch helpers (no commit): `batch_add_files`, `batch_add_technologies`, `batch_add_dependencies`, `batch_add_metrics`, `batch_add_warnings`, `update_analysis_status`
- `backend/tests/test_analysis/test_writer.py` — 26 tests covering files, technologies, dependencies, metrics (int+str), warnings, error aggregation, determinism, transactional boundary

### Changed
- `backend/app/models/metric.py` — `value` nullable BigInteger, `value_str` Text(NULL)
- `backend/app/models/dependency.py` — `source_files` JSON column, `source_files_list` property

### Architecture
- Writer never commits, never rollbacks — caller owns the transaction
- Metric invariant: exactly one of `value` (int) or `value_str` populated
- Dependencies deduped on `(name, ecosystem)`, metrics deduped on `key`
- Status: `COMPLETED` (no errors) vs `COMPLETED_WITH_ERRORS` (detector errors)

## 2026-07-26 — M4.9B API Integration

### Added
- `backend/app/modules/analysis/service.py` — `run_analysis(db, user_id, upload_id) → AnalysisResponse` with full orchestration, transaction ownership, lifecycle management
- `backend/app/modules/analysis/schemas.py` — `AnalysisResponse(analysis_id, status, error_detail)`
- `backend/app/modules/analysis/routes.py` — `POST /analysis/{upload_id}` endpoint (201)
- `backend/tests/test_analysis/test_api_integration.py` — 27 tests covering success, ownership validation, error states, status transitions, transaction boundaries

### Changed
- `backend/app/main.py` — Registered analysis router

### Architecture
- Service is the sole transaction owner — pipeline and writer never commit
- Status lifecycle: `RUNNING → COMPLETED | COMPLETED_WITH_ERRORS | FAILED`
- Best-effort FAILED persistence: rollback main tx, then write FAILED status in new tx
- Route contains no business logic, pipeline no HTTP knowledge, writer no HTTP knowledge
- All 338 tests passing in test_analysis

## 2026-07-26 — M5.1B Analysis Retrieval

### Added
- `backend/app/modules/analysis/query_service.py` — `AnalysisQueryService` with 8 retrieval methods: `get_analysis_summary`, `get_analysis_files`, `get_analysis_technologies`, `get_analysis_dependencies`, `get_analysis_metrics`, `get_analysis_warnings`, `list_project_analyses`, `list_upload_analyses`
- `backend/app/modules/analysis/schemas.py` — 8 new DTOs: `AnalysisSummaryResponse`, `AnalysisFileResponse`, `AnalysisTechnologyResponse`, `AnalysisDependencyResponse`, `AnalysisMetricResponse`, `AnalysisWarningResponse`, `AnalysisListItem`, `PaginatedResponse[T]`
- `backend/app/modules/analysis/repository.py` — 8 new read methods: `list_analysis_files_paginated`, `count_analysis_files`, `list_analysis_technologies_with_tech`, `list_dependencies_paginated`, `count_dependencies`, `list_warnings_paginated`, `count_warnings`, `list_analyses_by_project_paginated`, `list_analyses_by_upload_paginated`
- `backend/tests/test_analysis/test_query_api.py` — 69 tests across 14 test classes

### Changed
- `backend/app/modules/analysis/routes.py` — Added 8 GET endpoints: `GET /analysis/{id}`, `/analysis/{id}/files`, `/analysis/{id}/technologies`, `/analysis/{id}/dependencies`, `/analysis/{id}/metrics`, `/analysis/{id}/warnings`, `/analysis/project/{id}`, `/analysis/upload/{id}`
- `docs/ARCHITECTURE.md` — Added AnalysisQueryService documentation, updated folder structure, test listing, component table
- `docs/Legacy2Next_PROJECT_STATE.md` — Added Session 18, updated test counts, milestone progress

### Architecture
- AnalysisQueryService is read-only — never writes, commits, rollbacks, or flushes
- Read/write path separation: AnalysisQueryService and AnalysisQueryService share only the repository layer
- Repositories remain persistence-only: paginated queries return ORM models, no joins, no aggregation
- DTOs isolate API from ORM — all 8 responses are Pydantic models, never ORM entities
- Ownership validation on every GET endpoint via `_get_owned_analysis` (walk: Analysis → Upload → Project → user_id)
- Pagination: offset/limit (page/size), 3 default sizes (20 for list, 50 for sub-resources)
- Deterministic defaults: files by relative_path asc, deps by name asc, warnings by created_at desc
- All 407 tests passing in test_analysis

## 2026-07-26 — M5.2B Shared Query Infrastructure

### Added
- `backend/app/modules/analysis/query_options.py` — `QueryOptions`, `Page[T]`, `FileFilter`, `DependencyFilter`, `WarningFilter`, `apply_sort()`

### Changed
- `backend/app/modules/analysis/repository.py` — 5 paginated methods accept `(filter, opts)` and return `Page[ORM]`; added `_apply_file_filters`, `_apply_dependency_filters`, `_apply_warning_filters` with ILIKE search support
- `backend/app/modules/analysis/query_service.py` — Constructs filter+opts objects, validates sort_by, converts `Page` → `PaginatedResponse`; added `search` param to files/deps/warnings
- `backend/app/modules/analysis/routes.py` — Added `search: str | None = Query(None, min_length=2)` to files, dependencies, warnings endpoints
- `backend/tests/test_analysis/test_query_api.py` — 7 new search tests, 76 total

### Architecture
- QueryOptions and filter dataclasses are frozen (immutable)
- apply_sort() is a single shared helper — no per-repository sort repetition
- Search is case-insensitive ILIKE, min 2 chars, matches file_name/relative_path (files), name (deps), message (warnings)
- All 414 tests passing (was 407)

## 2026-07-26 — M5.3B Dashboard Aggregation

### Added
- `backend/app/modules/analysis/dashboard_service.py` — `DashboardService.get_dashboard()` with 6 section builders: general, files, technologies, dependencies, warnings, metrics. Ownership validation, derived values, no writes.
- `backend/app/modules/analysis/dashboard_schemas.py` — 9 nested Pydantic DTOs: `DashboardResponse`, `GeneralSection`, `FilesSection`, `TechnologiesSection`, `DependenciesSection`, `WarningsSection`, `MetricsSection`, plus `LanguageCount`, `ExtensionCount`, `DirectorySize`, `CategoryCount`, `ConfidenceCount`, `EcosystemBreakdown`, `TopPackage`, `DetectorCount`
- `backend/app/modules/analysis/repository.py` — 9 aggregation methods returning raw tuples/ORM entities: `get_language_distribution`, `get_extension_distribution`, `get_largest_directories`, `get_technology_category_distribution`, `get_ecosystem_breakdown`, `get_dependency_type_counts`, `get_top_dependencies`, `get_detector_breakdown`, `count_analysis_directories`
- `backend/app/modules/analysis/routes.py` — `GET /analysis/{analysis_id}/dashboard` endpoint returning `DashboardResponse`
- `backend/tests/test_analysis/test_dashboard_api.py` — 51 tests across 15 test classes covering all sections, empty data, ownership, DTO mapping, determinism, no-writes, serialization

### Architecture
- DashboardService owns orchestration — repositories return raw aggregation data only (COUNT, GROUP BY tuples, ORM entities)
- No DTO construction in repositories — all DTO mapping happens in DashboardService
- No caching — deferred to M5.4
- No Health section — deferred to M6 (AI insights)
- Nested DTO structure — each section independently evolvable
- All 465 tests passing (was 414)
