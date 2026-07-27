# Changelog

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
