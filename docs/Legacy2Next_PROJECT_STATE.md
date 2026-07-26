# PROJECT_STATE.md

# Legacy2Next - Project State

> This document tracks the current implementation status of the project.
>
> Update this file after every completed development session.
>
> This document reflects the current state of the repository.
>
> Product requirements are defined in `MASTER_PLAN.md`.
>
> Engineering rules are defined in `AI_CONTEXT.md`.

---

# Project Information

Project Name: Legacy2Next

Version: 0.4.0

Current Phase: Development

Current Sprint: Sprint 4 - Static Analysis

Overall Progress: 55%

Status: In Progress

Last Updated: 2026-07-26

---

# Current Goal

Milestone 5 — AI Integration (M5.1 Analysis Retrieval complete).

---

# Current Task

- AI Project Summary and module implementation (M5.2)

---

# Current Focus

Analysis retrieval API is implemented (407 tests). Moving to AI Integration for project summary generation.

---

# Completed

- Repository structure created (full backend directory tree, .gitignore, project configs)
- Backend initialized (FastAPI app factory, core layer with config/database/security/exceptions, SQLAlchemy models for User/Project/Analysis/Report, 8 module stubs with routes/services/schemas/repository separation, Alembic setup, test scaffolding, pyproject.toml with uv, Dockerfile, workers/ and integrations/ placeholders)
- PostgreSQL configured with connection pooling (`pool_size=5`, `max_overflow=10`, `pool_pre_ping=True`, `echo` driven by `DATABASE_ECHO`)
- Initial Alembic migration generated (`b1a1677bc7ef_initial_migration.py` — creates `users`, `projects`, `analyses`, `reports`)
- Docker Compose setup: `db` (PostgreSQL 16 Alpine) + `backend` (FastAPI) with health checks, named volumes, and default bridge networking
- Authentication system: register, login (JWT), password hashing (bcrypt via passlib), get_current_user dependency, protected `/auth/me` endpoint
- Architecture documentation: `docs/ARCHITECTURE.md` with implemented/planned separation, Mermaid diagrams, layer architecture, request lifecycle, authentication flow, database schema, Docker Compose architecture, error handling, module organisation, and architecture evolution roadmap
- Engineering decision log: `docs/DECISIONS.md` with 18 decisions covering technology stack, application architecture, database/migrations, authentication/security, Docker/infrastructure, and deferred features; each decision documents context, rationale, consequences, alternatives, and revisit conditions
- API contract: `docs/API_CONTRACT.md` documenting all 4 implemented endpoints (GET /health, POST /auth/register, POST /auth/login, GET /auth/me) with full request/response schemas, validation rules, error codes, behaviour origins (framework vs application), examples, and future endpoint placeholders
- Projects module: 5 CRUD endpoints (POST/GET/GET-by-id/PATCH/DELETE /projects), all auth-required, ownership-scoped via `_get_owned_project` helper, `ValidationException` added to exception hierarchy for PATCH-with-no-fields validation, repository uses ORM-object interfaces, projects router registered in `app/main.py`
- Uploads module (M3): complete multi-file upload system — Upload SQLAlchemy model (uploads table, FK to projects, SHA-256 hash, 5 indexes), config settings (UPLOAD_ROOT, MAX_FILE_SIZE_MB, MAX_FILES_PER_REQUEST, MAX_REQUEST_SIZE_MB, ALLOWED_EXTENSIONS, MAX_PROJECT_STORAGE_GB), StorageProvider abstraction (ABC + LocalStorageProvider with UUID hex filenames), Pydantic schemas (UploadResponse, UploadListResponse), repository layer (5 functions), QuotaService for per-project storage enforcement, service layer with batch commit/rollback and file-first delete strategy, 4 endpoints (POST/GET /projects/{id}/uploads, GET/DELETE /uploads/{id}), extended AppException hierarchy (FileValidationException, QuotaExceededException, StorageException), DI factories in core/dependencies.py, Alembic migration e6da2e749540, old upload/ stub removed, targeted engineering review applied (removed sha256_hash from response, added logging for rollback cleanup)
- Documentation updated for M3: API_CONTRACT.md with 4 upload endpoint sections (13 total endpoints), ARCHITECTURE.md with Upload model/storage layer/updated module org, PROJECT_STATE.md with M3 completion
- M4.1 Infrastructure: Analysis model updated (upload_id FK, error_detail, completed_at), 6 new models (Technology, AnalysisTechnology, AnalysisFile, Dependency, Metric), Alembic migration (3f88aa8a120f) with explicit FK naming, repository skeleton with 20 methods, `update_analysis()` removed per immutability requirement, minor `set_metric` fix applied
- M4.2 Discovery Engine: `types.py` (FileNode, DirectoryNode, FileGraph with hybrid representation, DiscoveryContext, DiscoveryStats), `ignore_rules.py` (IgnoreRules with 4 match strategies, 12 default dirs, 2 files, 2 globs), `discovery.py` (DiscoveryEngine with os.walk traversal, deterministic sorting, error resilience), 21 tests
- M4.3B Detector Framework + LanguageDetector: `base.py` (BaseDetector ABC with detect, read_text, logger, detector_name), `types.py` extended (DetectorResult, AnalysisResults, DetectedTechnology, DetectedDependency, DetectedFile, DetectedMetric), `utils.py` (extension→language mapping covering 90+ extensions), `language_detector.py` (LanguageDetector — extension-based language classification, aggregate counts, DetectedFile enrichment), 48 new tests (69 total in test_analysis), all pass
- M4.3B FrameworkDetector: `framework_detector.py` (EvidenceRule hierarchy: JsonDependencyRule, XmlDependencyRule, TomlDependencyRule, LineDependencyRule, FileExistsRule; FrameworkDefinition with 32 definitions across 4 categories; FrameworkDetector with two-phase design, confidence merging, deduplication), `test_framework_detector.py` (45 tests covering all rule types, framework detection, edge cases), all 114 tests in test_analysis pass
- M4.5B DependencyDetector: `dependency_detector.py` (closed ManifestParser hierarchy with 9 parsers: PackageJsonParser, RequirementsParser, PyProjectParser, PomParser, GradleParser, CargoParser, ComposerParser, GemfileParser, CsProjParser; _RawDependency intermediate model; _PARSER_REGISTRY data-driven dict; _merge_deduplicate with version conflict warning; canonical category mapping; graceful degradation), `DetectedDependency` updated (source_files tuple, category field), `test_dependency_detector.py` (93 tests across 12 test classes covering all parsers, registry, dedup, integration), all 207 tests in test_analysis pass
- M4.6B MetricsCollector: `metrics_collector.py` (single `MetricsCollector` class with private helpers, pure aggregation from `AnalysisResults` only, zero I/O, deterministic output), `metric_keys.py` (`MetricKey(StrEnum)` with 7 stable constants, dynamic `dependencies.<ecosystem>` keys), `DetectedMetric.value` widened from `int` to `int | str` to support string metrics like `primary_language`, `test_metrics_collector.py` (51 tests across 14 test classes covering empty results, file counts, language counting, primary language with alphabetical tie-breaking, framework counting, dependency counting, ecosystem grouping, manifest counting, determinism, result integrity, integration, MetricKey enum), all 258 tests in test_analysis pass
- M4.7B AnalysisPipeline: `pipeline.py` (pure orchestration: DiscoveryEngine → detectors → MetricsCollector, constructor injection, failure isolation, sequential execution, deterministic output), `types.py` extended (DetectorWarning, DetectorResult.warnings), 27 tests, 285 total
- M4.8B AnalysisWriter: `writer.py` (AnalysisWriter class writing files, technologies, dependencies, metrics, warnings, status), `repository.py` (6 batch helpers, no commit), `analysis_warning.py` model, `test_writer.py` (26 tests covering all write operations, error aggregation, determinism, transactional boundary), 311 total
- M4.9B API Integration: `service.py` (run_analysis with transaction ownership, upload validation, pipeline construction, lifecycle management), `schemas.py` (AnalysisResponse), `routes.py` (POST /analysis/{upload_id}), `test_api_integration.py` (27 tests covering success, ownership, error states, status transitions, rollback), 338 total
- M5.1B Analysis Retrieval: `query_service.py` (AnalysisQueryService with 8 retrieval methods), `schemas.py` (8 DTOs + PaginatedResponse), `routes.py` (8 GET endpoints), `repository.py` (9 paginated/filtered read methods), `test_query_api.py` (69 tests covering summary, files, technologies, dependencies, metrics, warnings, project/upload listing, pagination, filtering, sorting, ownership, DTO mapping, determinism, no-writes), 407 total

---

# In Progress

Milestone 5 — AI Integration (M5.1 Analysis Retrieval complete)

---

# Blockers

None.

---

# Next Tasks

1. AI Integration — Project Summary (M5.2)

---

# Milestone Progress

## Milestone 1 — Project Foundation

Status: In Progress (5/6)

Tasks

- [x] Repository Structure
- [x] Backend Setup
- [ ] Frontend Setup
- [x] PostgreSQL Setup
- [x] Docker Setup
- [x] Authentication

---

## Milestone 2 — Projects Module

Status: Complete

Tasks

- [x] Project CRUD (5 endpoints: create, list, get, update, delete)

---

## Milestone 3 — Uploads Module

Status: Complete

Tasks

- [x] Upload SQLAlchemy model (uploads table, FK, SHA-256, 5 indexes)
- [x] Upload configuration (UPLOAD_ROOT, MAX_FILE_SIZE_MB, MAX_FILES_PER_REQUEST, ALLOWED_EXTENSIONS, MAX_PROJECT_STORAGE_GB)
- [x] Storage abstraction layer (StorageProvider ABC + LocalStorageProvider)
- [x] Upload schemas (UploadResponse, UploadListResponse)
- [x] Upload repository (5 CRUD functions + project total storage query)
- [x] Quota service (per-project storage limit enforcement)
- [x] Upload service (batch upload with rollback, file-first delete, ownership enforcement)
- [x] Upload routes (4 endpoints: POST/GET project uploads, GET/DELETE single upload)
- [x] Core dependencies (get_storage_provider, get_quota_service factories)
- [x] Extended exception hierarchy (FileValidationException, QuotaExceededException, StorageException)
- [x] Alembic migration (creates uploads table)
- [x] Removed old upload/ stub
- [x] Targeted engineering review (removed sha256_hash from response, added logging)

---

## Milestone 4 — Static Analysis

Status: Complete (338 tests passing)

### M4.1 — Infrastructure

- [x] Analysis model updated (upload_id FK, error_detail, completed_at)
- [x] 6 new models (Technology, AnalysisTechnology, AnalysisFile, Dependency, Metric)
- [x] Alembic migration with explicit FK naming
- [x] Repository skeleton (20 methods)
- [x] update_analysis() removed (immutability enforcement)

### M4.2 — Discovery Engine

- [x] types.py (FileNode, DirectoryNode, FileGraph, DiscoveryContext, DiscoveryStats)
- [x] ignore_rules.py (IgnoreRules with 4 match strategies, 17 default patterns)
- [x] discovery.py (DiscoveryEngine, deterministic os.walk traversal, error resilience)
- [x] 21 tests passing

### M4.3 — Detector Framework & LanguageDetector

- [x] base.py (BaseDetector ABC with detect, read_text, logger, detector_name)
- [x] types.py extended (DetectorResult, AnalysisResults, DetectedTechnology, DetectedDependency, DetectedFile, DetectedMetric)
- [x] utils.py (extension→language mapping covering 90+ extensions)
- [x] language_detector.py (LanguageDetector — extension classification, aggregation, DetectedFile enrichment)
- [x] 48 tests passing

### M4.4 — FrameworkDetector

- [x] framework_detector.py (EvidenceRule hierarchy, 32 FrameworkDefinitions, two-phase design)
- [x] 45 tests passing

### M4.5 — DependencyDetector

- [x] dependency_detector.py (9 parsers, closed hierarchy, canonical categories, dedup)
- [x] DetectedDependency updated (source_files tuple, category field)
- [x] 93 tests passing (207 total in test_analysis)

### M4.6 — MetricsCollector

- [x] metrics_collector.py (pure aggregation from AnalysisResults, zero I/O, deterministic)
- [x] metric_keys.py (MetricKey StrEnum with 7 stable constants)
- [x] DetectedMetric.value widened from int to int | str
- [x] 51 tests passing (258 total in test_analysis)

### M4.7 — AnalysisPipeline

- [x] pipeline.py (AnalysisPipeline — orchestration only, no detection/aggregation/persistence)
- [x] types.py: DetectorWarning dataclass added
- [x] types.py: DetectorResult.warnings field added
- [x] Constructor injection: engine, detectors, metrics_collector
- [x] Sequential execution, failure isolation, deterministic output
- [x] 27 tests passing (285 total in test_analysis)

### M4.8 — AnalysisWriter

- [x] writer.py (AnalysisWriter — files, technologies, dependencies, metrics, warnings, status)
- [x] repository.py (6 batch helpers, no commit)
- [x] analysis_warning.py model
- [x] PersistenceResult dataclass
- [x] Metric invariant: exactly one of value (int) or value_str populated
- [x] 26 tests passing (311 total in test_analysis)

### M4.9 — API Integration

- [x] service.py (run_analysis — transaction owner, pipeline construction, lifecycle management)
- [x] schemas.py (AnalysisResponse with analysis_id, status, error_detail)
- [x] routes.py (POST /analysis/{upload_id}, 201)
- [x] main.py (analysis router registered)
- [x] Status lifecycle: RUNNING → COMPLETED | COMPLETED_WITH_ERRORS | FAILED
- [x] 27 tests passing (338 total in test_analysis)

---

### M5.1 — Analysis Retrieval

- [x] query_service.py (AnalysisQueryService — 8 retrieval methods)
- [x] schemas.py (8 DTOs + PaginatedResponse[T])
- [x] routes.py (8 GET endpoints in existing router)
- [x] repository.py (9 paginated/filtered read methods)
- [x] Ownership validation on all endpoints
- [x] Pagination (offset/limit), filtering, sorting
- [x] DTOs isolate API from ORM
- [x] 69 tests passing (407 total in test_analysis)

---

## Milestone 5 — AI Integration

Status: In Progress (M5.1 complete)

Tasks

- [x] M5.1 Analysis Retrieval API
- [ ] AI Project Summary
- [ ] AI File Explanation
- [ ] AI Documentation
- [ ] AI Recommendations

---

## Milestone 6 — Dashboard

Status: Not Started

Tasks

- [ ] Dashboard
- [ ] Reports
- [ ] Documentation Viewer

---

## Milestone 7 — Finalization

Status: Not Started

Tasks

- [ ] Testing
- [ ] Bug Fixes
- [ ] Documentation
- [ ] Deployment

---

# Repository Structure

docs/
├── API_CONTRACT.md
├── ARCHITECTURE.md
├── DECISIONS.md
├── Legacy2Next_MASTER_PLAN.md
├── Legacy2Next_AI_CONTEXT.md
├── Legacy2Next_PROJECT_STATE.md
└── initial_prompt.md

backend/
├── app/
│   ├── core/          (config, database, security, exceptions, dependencies)
│   ├── storage/       (base ABC, LocalStorageProvider)
│   ├── models/        (User, Project, Upload, Analysis, Report)
│   ├── modules/       (auth, projects, uploads, analysis, ai, documentation, modernization, reports)
│   │   ├── auth/      (fully implemented)
│   │   ├── projects/  (fully implemented)
│   │   ├── uploads/   (fully implemented — routes, service, schemas, repository, quota)
│   │   └── */         (scaffolded — routes, service, schemas, repository)
│   ├── workers/       (placeholder)
│   ├── integrations/  (placeholder)
│   └── utils/         (placeholder)
├── alembic/           (migration environment; 2 migration versions)
├── tests/             (conftest + test dirs per module, all empty)
├── uploads/           (file storage per project, mounted as Docker named volume)
├── pyproject.toml
├── Dockerfile
└── .env.example

docker-compose.yml     (orchestrates db + backend)

frontend/              (not yet initialized)

prompts/               (not yet populated)

assets/                (not yet populated)

---

# Current Tech Stack

Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic

Frontend

- React
- TypeScript
- Vite
- TailwindCSS

Database

- PostgreSQL

Authentication

- JWT
- bcrypt

Deployment

- Docker

---

# Important Decisions

- Architecture documented in `docs/ARCHITECTURE.md` with Implemented vs Planned separation — planned features are explicitly labelled and not described as if they already exist; Mermaid diagrams visualise layer architecture, authentication flow, and Docker Compose topology.
- Backend organized by feature modules under `app/modules/` (each module has routes, service, schemas, repository) rather than flat `routers/` + `services/` layers — improves modularity and independent testability.
- SQLAlchemy models centralized in `app/models/` to avoid circular foreign-key imports across modules.
- Repository layer separated from services (empty placeholders) to enforce data-access abstraction from the start.
- `pyproject.toml` used with uv-compatible PEP 621 format instead of `requirements.txt`.
- `workers/` and `integrations/` directories added for future background tasks and external service adaptors.
- Later-milestone schema and model fields stripped to keep M1 focused on foundation only.
- `docker-compose.yml` at repository root orchestrates `db` (PostgreSQL 16 Alpine) + `backend` (FastAPI) with health check dependency and named volumes.
- Dockerfile uses `pip install .`; `pyproject.toml` required `[tool.setuptools.packages.find]` to resolve flat-layout build error.
- Authentication uses JWT (HS256, 30-min expiry, `sub`/`iat`/`exp` claims), bcrypt via `passlib` (pinned `bcrypt<4.1.0` for compatibility), and stateless client-side logout.
- Registration returns user profile without issuing a JWT; tokens are only issued via `/auth/login`.
- `get_current_user` dependency lives in `app/core/dependencies.py` for reuse across all modules.
- Engineering decision log formalised in `docs/DECISIONS.md` — each decision documents context, rationale, consequences, alternatives considered, and future revisit conditions; deferred features are grouped to avoid decision inflation.
- Projects module uses 404 Not Found (not 403) to hide unowned resources — prevents information leakage about other users' project IDs.
- Projects repository accepts/returns ORM objects (`Project`) rather than dicts — ownership checks in the service layer rely on `project.user_id`.
- `ValidationException` (HTTP 400) added for PATCH-with-no-fields — uses 400 rather than 422 to distinguish application-level validation from Pydantic schema validation.

---

# Known Issues

None.

---

# Technical Debt

None.

---

# Session Log

## Session 1

Completed

- Project planning
- MASTER_PLAN.md
- AI_CONTEXT.md
- PROJECT_STATE.md

Next

- Repository initialization

---

## Session 2 — 2026-07-26

Completed

- Repository structure: created full backend directory tree, .gitignore, pyproject.toml (uv), .env.example, .dockerignore
- Backend setup: FastAPI app factory with health endpoint, core layer (config, database, security, exceptions), SQLAlchemy models (User, Project, Analysis, Report), Alembic environment (env.py, ini, mako), test scaffolding (conftest + test directories)
- Module stubs: 8 feature modules (auth, projects, upload, analysis, ai, documentation, modernization, reports) each with routes.py, service.py, schemas.py, repository.py
- Extensibility placeholders: workers/, integrations/, analysis/detectors/, documentation/generators/, utils/
- Docker: Dockerfile with python:3.12-slim

Design Decisions

- Shared models/ to avoid circular FK imports
- Repository layer separated from services
- Later-milestone schemas and model columns stripped to keep M1 focused
- pyproject.toml replaces requirements.txt (uv-compatible)

Next

- Frontend initialization
- PostgreSQL setup and initial migration
- Docker Compose
- Authentication implementation

---

## Session 3 — 2026-07-26

Completed

- PostgreSQL configuration: `DATABASE_ECHO` setting added to `Settings`
- Connection pooling: `pool_size=5`, `max_overflow=10`, `pool_pre_ping=True`, `echo` driven by config
- Initial Alembic migration generated (`b1a1677bc7ef_initial_migration.py`) — creates `users`, `projects`, `analyses`, `reports` tables with FKs and indexes

Design Decisions

- Connection pool params chosen as conservative defaults (5/10) suitable for single-developer MVP
- `echo` gated behind `DATABASE_ECHO` (not `DEBUG`) so SQL logging can be controlled independently
- Autogenerated migration left unapplied for review before first `alembic upgrade head`

Next

- Frontend initialization
- Docker Compose
- Authentication implementation

---

## Session 4 — 2026-07-26

Completed

- Docker Compose setup: `docker-compose.yml` with `db` (PostgreSQL 16 Alpine) and `backend` (FastAPI) services
- Named volumes for PostgreSQL data (`pgdata`) and uploads (`uploads`)
- PostgreSQL health check with `pg_isready`; backend waits for healthy DB via `depends_on`
- `DATABASE_URL` override in compose environment (`postgresql://postgres:postgres@db:5432/legacy2next`) — local dev uses `localhost`
- Default bridge networking (services resolve by name)
- Docker build fix: `[tool.setuptools.packages.find]` added to `pyproject.toml` to resolve flat-layout discovery error (`app` + `alembic` detected as multiple top-level packages)
- Verified: `docker compose up --build` starts both services, health endpoint returns `{"status":"ok"}`
- Verified: `alembic upgrade head` creates all 4 tables successfully

Design Decisions

- No automatic migration on startup — migrations are explicit developer actions
- No `env_file` in compose — backend Settings defaults are sufficient; only `DATABASE_URL` is overridden via `environment`
- PostgreSQL port not exposed to host — backend connects via internal network; avoids port conflicts with local PostgreSQL
- No custom networks — Compose default bridge network sufficient for 2-service setup

Next

- Frontend initialization

---

## Session 5 — 2026-07-26

Completed

- Authentication implementation: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- Registration returns user profile (201) — no automatic login
- Login returns JWT with `sub`, `iat`, `exp` claims (30-min expiry)
- Password hashing with `passlib[bcrypt]` (bcrypt backend pinned to `<4.1.0` for compatibility)
- `decode_access_token` added to `app/core/security.py`
- `get_current_user` dependency in `app/core/dependencies.py` using `OAuth2PasswordBearer`
- Auth router included in `app/main.py`
- Schemas updated with `EmailStr`, `Field` validation, `ConfigDict(from_attributes=True)`
- `ConflictException` (409) added to `app/core/exceptions.py`
- `email-validator>=2.0.0` added to `pyproject.toml`
- Pinned `bcrypt>=4.0.0,<4.1.0` in `pyproject.toml` to resolve `passlib` compatibility issue (`bcrypt>=4.1.0` changed internal API)
- Fixed `datetime.utcnow()` → `datetime.now(tz=timezone.utc)` in `security.py`
- Verified: register, duplicate register (409), login, wrong password (401), `/auth/me` with valid token, `/auth/me` with invalid token (401)

Design Decisions

- Registration does not issue a JWT — authentication occurs only through login
- Stateless JWT, no refresh tokens, no token blacklist (client-side discard on logout)
- `OAuth2PasswordBearer` used for token extraction from `Authorization: Bearer` header; login endpoint accepts JSON (not form data) — `tokenUrl` is metadata only for OpenAPI schema
- `email-validator` added over manual regex validation — standard, well-maintained, handles edge cases
- `bcrypt<4.1.0` pinned because `passlib`'s internal `_bcrypt.hashpw` call is incompatible with bcrypt 4.1.0+

Next

- Frontend initialization

---

## Session 6 — 2026-07-26

Completed

- Created `docs/ARCHITECTURE.md` documenting implemented architecture (project overview, folder structure, layer architecture, request lifecycle, DI, auth flow, database schema, Docker Compose, error handling, module organisation) with clearly separated Implemented vs Planned sections and Mermaid diagrams
- Updated `docs/Legacy2Next_PROJECT_STATE.md` to reflect ARCHITECTURE.md completion

Design Decisions

- Architecture document uses Implemented/Planned section split so every statement is verifiable from the current codebase
- Mermaid diagrams used only where they improve understanding (layer architecture, auth sequence, Docker Compose topology)
- Cross-references MASTER_PLAN.md, AI_CONTEXT.md, PROJECT_STATE.md instead of duplicating information
- Scaffolded modules clearly labelled as stubs; auth module as the only fully implemented module
- Empty placeholder directories (workers/, integrations/, detectors/, generators/) explicitly noted

Next

- Frontend initialization

---

## Session 7 — 2026-07-26

Completed

- Created `docs/DECISIONS.md` with 18 engineering decisions: FastAPI, SQLAlchemy ORM, PostgreSQL, PEP 621 pyproject.toml, Repository Pattern, Service Layer, Centralised Models, Consistent Module Structure, Alembic Migrations, Explicit Database Migrations, JWT Authentication, Stateless Authentication, bcrypt via passlib, bcrypt Version Pin, Registration Does Not Issue JWT, Docker Compose for Development, Explicit Package Discovery, and Deferred Authentication Features (Refresh Tokens, RBAC, Email Verification, Password Reset)
- Updated `docs/Legacy2Next_PROJECT_STATE.md` to reflect DECISIONS.md completion

Design Decisions

- Implementation-level choices (e.g., email-validator) excluded from DECISIONS.md — kept in DEVELOPMENT_GUIDE.md scope
- Comparison-style decision names avoided — alternatives discussed only inside the Alternatives Considered section
- Deferred features grouped into a single decision with subsections to avoid decision count inflation

Next

- Frontend initialization

---

## Session 8 — 2026-07-26

Completed

- Created `docs/API_CONTRACT.md` documenting all 4 implemented endpoints (GET /health, POST /auth/register, POST /auth/login, GET /auth/me) with request/response schemas, validation rules, error codes, behaviour origins (framework-generated vs application-defined), examples, and future endpoint placeholders
- Updated `docs/Legacy2Next_PROJECT_STATE.md` to reflect API_CONTRACT.md completion

Design Decisions

- Framework-generated endpoints (/docs, /redoc, /openapi.json) explicitly separated from project-owned endpoints in a dedicated "Framework Endpoints" section
- Behaviour Origins section distinguishes auto-generated 422 validation errors from application-defined AppException errors
- Response Format section documents three categories: success schemas, AppException structured errors, and framework 422 format
- Source of Truth preamble clarifies this document vs the live OpenAPI spec

Next

- Frontend initialization

---

## Session 9 — 2026-07-26

Completed

- Implemented Projects module with 5 CRUD endpoints: `POST /projects` (201), `GET /projects` (200), `GET /projects/{project_id}` (200), `PATCH /projects/{project_id}` (200), `DELETE /projects/{project_id}` (204)
- All endpoints require authentication via `get_current_user` dependency
- All operations scoped to the authenticated user (`current_user.id`) — users cannot access other users' projects
- Ownership enforcement via private `_get_owned_project` helper in `projects/service.py`
- `NotFoundException("Project")` raised (404) for missing or unowned resources — no information leakage about other users' project IDs
- `ValidationException` added to `app/core/exceptions.py` (HTTP 400, code `VALIDATION_ERROR`) for PATCH requests with no updatable fields
- Repository layer uses ORM-object interfaces (`Project` model instance), not dicts
- `projects_router` registered in `app/main.py`
- Updated `docs/API_CONTRACT.md`: added Projects endpoint documentation (5 endpoints), updated coverage count to 9, updated error response tables, removed Projects from Future Endpoints
- Updated `docs/ARCHITECTURE.md`: Projects marked implemented, phase updated to M2, module organisation section added, architecture evolution diagram updated
- Updated `docs/Legacy2Next_PROJECT_STATE.md`: Session 9 recorded, milestone progress updated, completed items extended

Files Modified

- `backend/app/core/exceptions.py` — Added `ValidationException` (HTTP 400, code `VALIDATION_ERROR`)
- `backend/app/modules/projects/schemas.py` — Created `ProjectCreate`, `ProjectUpdate`, `ProjectResponse`, `ProjectListResponse`
- `backend/app/modules/projects/repository.py` — Implemented `get_project_by_id`, `list_projects_by_owner`, `create_project`, `update_project`, `delete_project`
- `backend/app/modules/projects/service.py` — Implemented `_get_owned_project`, `create_project`, `get_project`, `list_projects`, `update_project`, `delete_project`
- `backend/app/modules/projects/routes.py` — Implemented 5 CRUD endpoints
- `backend/app/main.py` — Registered `projects_router`
- `docs/API_CONTRACT.md` — Added 5 Projects endpoints, updated metadata and error tables
- `docs/ARCHITECTURE.md` — Marked Projects implemented, updated phase, module org, evolution diagram
- `docs/Legacy2Next_PROJECT_STATE.md` — Added Session 9, milestone updates

Endpoints Implemented

- `POST /projects` — Create project (201)
- `GET /projects` — List owned projects (200)
- `GET /projects/{project_id}` — Get project by ID (200)
- `PATCH /projects/{project_id}` — Update project fields (200)
- `DELETE /projects/{project_id}` — Delete project (204)

Architecture Changes

- Projects module follows the established 4-file layout (routes/service/schemas/repository)
- All four layers fully implemented (matching auth module pattern)
- Private helper `_get_owned_project` in service layer centralises ownership enforcement
- No schema changes or database migrations required — uses existing `projects` table from initial migration

Validation Changes

- `ValidationException` (HTTP 400, `VALIDATION_ERROR`) added for PATCH with no fields
- `NotFoundException` (HTTP 404, `PROJECT_NOT_FOUND`) returned for missing or unowned projects
- All existing validation patterns preserved

Testing Performed

- Python AST parse verified on all modified files
- No runtime testing performed (no test suite executed)

Design Decisions

- 404 Not Found hides unowned resources rather than 403 Forbidden — prevents information leakage about other users' project IDs
- Repository accepts/returns ORM objects (`Project`) rather than dicts — consistent with service layer ownership checks on model attributes
- `ValidationException` uses 400 rather than 422 — distinguishes application-level validation from Pydantic schema validation
- No new migration required — the `projects` table was already created with all needed columns in the initial migration

Next

- Upload module implementation (ZIP upload, file extraction, project storage)

---

## Session 10 — 2026-07-26

Completed

- Created M3 Uploads implementation plan with 10 sections (model, config, storage, schemas, repository, quota, service, routes, dependencies, migration)
- Revised plan per review (10 changes: ALLOWED_EXTENSIONS over ALLOWED_MIME_TYPES, ALLOWED_MIME_TYPES kept as config, timeout removed, upload status made constant, UploadResponse expanded, batch response clarified, quota in routes, FK cascade documented, _get_owned_project duplicated, QuotaService made stateless)
- Implemented Upload SQLAlchemy model (`app/models/upload.py`) — id, project_id FK, original_name, stored_name, file_path, file_size, mime_type, extension, sha256_hash, status, created_at; 5 indexes including composite (project_id, created_at)
- Grouped upload config in Settings: UPLOAD_ROOT, MAX_FILE_SIZE_MB (50), MAX_FILES_PER_REQUEST (100), MAX_REQUEST_SIZE_MB (500), ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, MAX_PROJECT_STORAGE_GB (5)
- Created storage abstraction: `app/storage/base.py` (StorageProvider ABC + FileStorageResult TypedDict), `app/storage/local.py` (LocalStorageProvider with UUID hex filenames, per-project subdirs)
- Created upload schemas: UploadResponse (id, project_id, original_name, file_size, mime_type, extension, sha256_hash, status, created_at), UploadListResponse
- Created upload repository: `create_upload` (flush), `get_upload_by_id`, `list_uploads_by_project` (DESC), `delete_upload` (flush), `get_project_total_storage` (SUM coalesce)
- Created QuotaService: `check_storage_quota` reading MAX_PROJECT_STORAGE_GB from settings
- Created upload service: `upload_files` (validation → hash → quota → storage → batch DB with rollback), `list_uploads`, `get_upload`, `delete_upload` (file-first delete)
- Created upload routes: 4 endpoints (POST/GET /projects/{id}/uploads, GET/DELETE /uploads/{id})
- Extended AppException hierarchy: FileValidationException (400), QuotaExceededException (400), StorageException (500)
- Added DI factories: get_storage_provider(), get_quota_service() in app/core/dependencies.py
- Registered uploads_router in app/main.py
- Generated and applied Alembic migration e6da2e749540 (creates uploads table with all columns, FK, 5 indexes)
- Updated backend/.env and backend/.env.example with new upload settings
- Removed old modules/upload/ stub directory
- Conducted targeted engineering review: checked relationships, FK, response models, memory usage, code quality, security
- Applied 2 fixes: removed sha256_hash from UploadResponse, added logging for rollback cleanup failures
- Updated all 3 documentation files: API_CONTRACT.md (4 upload endpoint sections), ARCHITECTURE.md (storage layer, Upload model, updated module org/evolution/DI), PROJECT_STATE.md (M3 completion, new milestone structure)

Files Created

- `backend/app/models/upload.py` — Upload SQLAlchemy model
- `backend/app/storage/__init__.py` — Package init
- `backend/app/storage/base.py` — StorageProvider ABC + FileStorageResult TypedDict
- `backend/app/storage/local.py` — LocalStorageProvider implementation
- `backend/app/modules/uploads/__init__.py` — Package init
- `backend/app/modules/uploads/schemas.py` — UploadResponse, UploadListResponse
- `backend/app/modules/uploads/repository.py` — 5 CRUD/query functions
- `backend/app/modules/uploads/quota.py` — QuotaService
- `backend/app/modules/uploads/service.py` — Business logic
- `backend/app/modules/uploads/routes.py` — 4 endpoints
- `backend/alembic/versions/e6da2e749540_create_uploads_table.py` — Creates uploads table

Files Modified

- `backend/app/core/config.py` — Grouped upload settings
- `backend/app/core/exceptions.py` — Added FileValidationException, QuotaExceededException, StorageException
- `backend/app/core/dependencies.py` — Added get_storage_provider, get_quota_service
- `backend/app/core/database.py` — (no changes needed)
- `backend/app/models/__init__.py` — Added Upload re-export
- `backend/app/main.py` — Registered uploads_router
- `backend/app/.env` — Updated upload settings
- `backend/.env.example` — Updated upload settings
- `docs/API_CONTRACT.md` — Added 4 upload endpoint sections, updated metadata
- `docs/ARCHITECTURE.md` — Added storage layer, Upload model, updated module org/evolution/DI
- `docs/Legacy2Next_PROJECT_STATE.md` — Session 10, M3 completion, milestone restructuring

Deleted

- `backend/app/modules/upload/` — Old stub replaced by uploads/

Design Decisions

- StorageProvider as ABC enables future cloud storage backends (S3, GCS) without changing service code
- UUID hex filenames prevent path traversal and name collisions
- File-first delete strategy (delete from disk before DB record) prevents orphaned DB records
- Batch commit with rollback: all files in a request succeed or none; partial uploads are cleaned up
- Per-project storage quota via QuotaService (configurable MAX_PROJECT_STORAGE_GB)
- SHA-256 hash computed for dedup/integrity but not exposed in API response (post-review)
- Upload module uses its own `_get_owned_project` helper rather than importing from projects service — keeps each module's ownership enforcement self-contained
- No SQLAlchemy relationships on Upload or Project models — consistent with existing codebase pattern (explicit queries over ORM navigation)
- FK cascade intentionally omitted — matches existing projects.user_id FK pattern (no cascade elsewhere)

Validation Changes

- FileValidationException (HTTP 400) for validation failures with explicit codes (EMPTY_FILE, INVALID_FILENAME, INVALID_FILE_TYPE)
- QuotaExceededException (HTTP 400) for storage limit exceeded
- StorageException (HTTP 500) for storage layer failures
- 404 returned for missing or unowned resources (consistent with Projects pattern)
- No MIME type validation — extension-based validation used as primary defense (MIME is advisory and client-controlled)

Testing Performed

- Python AST parse verified on all new and modified files
- No runtime testing performed (no test suite executed)

Next

- Analysis module implementation (language detection, framework detection, dependency parsing, file metadata extraction)

---

## Session 11 — 2026-07-26

Completed

- Implemented BaseDetector ABC (`app/modules/analysis/base.py`) — abstract detect(context), read_text(relative_path), detector_name property, logger property
- Extended types.py with detector types: DetectorResult (flat, immutable), AnalysisResults (mutable collector with property accessors), DetectedTechnology, DetectedDependency, DetectedFile, DetectedMetric (all frozen dataclasses)
- Created utils.py with extension→language mapping covering 90+ programming languages and file formats using `classify_extension()` and `is_known_extension()` helpers
- Implemented LanguageDetector (`app/modules/analysis/language_detector.py`) — extension-based language classification, count aggregation, percentage evidence, DetectedFile enrichment with language field, error-isolated detect() that catches all exceptions
- Created 48 comprehensive tests in `tests/test_analysis/test_detector_framework.py` covering: DetectorResult immutability and serialization, all Detected* types, AnalysisResults aggregation and error handling, classify_extension case-insensitivity and edge cases, BaseDetector (naming, abstract enforcement, read_text with/without root, error cases), LanguageDetector (empty project, single/mixed/unknown languages, deterministic output, large project, files without extensions, field correctness)
- Updated PROJECT_STATE.md with M4 milestone breakdown, session log, version bump to 0.4.0
- Updated ARCHITECTURE.md with analysis module status

Files Created

- `backend/app/modules/analysis/base.py` — BaseDetector ABC
- `backend/app/modules/analysis/utils.py` — Extension→language mapping utilities
- `backend/app/modules/analysis/language_detector.py` — LanguageDetector implementation
- `backend/tests/test_analysis/test_detector_framework.py` — 48 tests

Files Modified

- `backend/app/modules/analysis/types.py` — Added DetectorResult, AnalysisResults, DetectedTechnology, DetectedDependency, DetectedFile, DetectedMetric
- `docs/Legacy2Next_PROJECT_STATE.md` — Session 11, M4 milestone breakdown, version bump, current goal/task update
- `docs/ARCHITECTURE.md` — Updated analysis module status, folder structure, architecture evolution

Testing Performed

- 69 tests in test_analysis: 48 detector framework tests + 21 discovery tests, all passing

Architecture Decisions

- Fluent BaseDetector design with _context_root attribute — set by pipeline orchestration before read_text() calls; avoids passing root_path on every read_text call
- DetectorResult uses flat tuple-based design (not generics) — consistent with M4.3A refinement; empty tuples are singletons with zero overhead
- AnalysisResults is mutable during collection (list of DetectorResult) but all Detected* types are frozen dataclasses
- LanguageDetector uses two-phase design: public detect() catches all exceptions and returns error DetectorResult; private _detect() contains pure logic — never raises
- Extension mapping uses case-insensitive lookup with pre-computed lowercase dict

Next

- FrameworkDetector implementation (identify frameworks and build tools from config file presence)
- DependencyDetector implementation (parse dependency manifests)

---

## Session 12 — 2026-07-26

Completed

- Implemented FrameworkDetector (`backend/app/modules/analysis/framework_detector.py`) — EvidenceRule ABC hierarchy with 5 implementations: JsonDependencyRule (dot-separated JSON key path), XmlDependencyRule (Maven artifactId matching with namespace handling), TomlDependencyRule (TOML key path), LineDependencyRule (requirements.txt and Gemfile patterns), FileExistsRule (evidence file presence)
- Created 32 FrameworkDefinition entries across 4 categories: 11 frontend/backend frameworks (React, Next.js, Vue, Nuxt, Angular, Svelte, SvelteKit, Express, NestJS, Django, Flask, FastAPI, Spring Boot, ASP.NET Core, Laravel, Ruby on Rails), 7 build tools (Vite, Webpack, Rollup, Parcel, Maven, Gradle, Cargo), 6 package managers (npm, pnpm, yarn, bun, pip, Poetry), 3 runtimes (Node.js, Deno, Bun)
- Implemented FrameworkDetector with two-phase design (public detect() catches exceptions → returns error DetectorResult; private _detect() contains pure logic), confidence merging (high > medium > low), evidence deduplication, and deterministic sorted output
- Added helper functions: _find_file (exact name + wildcard *.csproj matching), _read_text, _conf_level, _namespaces, _tag
- Created 45 comprehensive tests covering: all 5 EvidenceRule types (found/not found/missing file/corrupt content edge cases), FrameworkDetector integration (empty project, single/multiple frameworks, Angular with angular.json, Django with manage.py, Spring Boot with pom.xml, Vite with vite.config.ts, Cargo, Next.js without React implication, duplicate evidence merging, confidence merging, corrupted config, deterministic output, full tech stack, Bun, FastAPI with pyproject.toml, detector_name correctness, all definitions have category and rules)
- Updated PROJECT_STATE.md with M4.3 milestone update, Session 12, current task/focus

Files Created

- `backend/app/modules/analysis/framework_detector.py` — FrameworkDetector + 5 EvidenceRule implementations + 32 FrameworkDefinitions (415 lines)
- `backend/tests/test_analysis/test_framework_detector.py` — 45 tests

Testing Performed

- 114 tests in test_analysis: 48 detector framework tests + 21 discovery tests + 45 framework detector tests, all passing

Architecture Decisions

- EvidenceRule ABC enables pluggable rule evaluation without modifying FrameworkDetector for new frameworks
- JsonDependencyRule uses dot-separated key_path (supports deeply nested keys like "dependencies.@angular/core")
- XmlDependencyRule handles Maven pom.xml (artifactId text) with namespace-aware matching; wildcard (*.csproj) filename support for ASP.NET Core
- Corrupt/unreadable config files return medium-confidence evidence rather than None — distinguishes "file missing" from "file present but unreadable"
- FrameworkDefinition is a flat frozen dataclass with name, category, and rules list — no nesting or inheritance
- Confidence priority: high (2) > medium (1) > low (0); best evidence wins for each framework
- Next.js does NOT imply React — each framework definition is self-contained
- Duplicate evidence details are deduplicated per framework (mutable list dedup in accumulation phase)
- _find_file, _read_text are module-level functions (not BaseDetector methods) — keeps I/O isolated in the framework_detector module
- _namespaces/_tag helpers handle XML namespace prefixes for csproj and similar formats
- 45 tests organized in 7 test classes matching the rule hierarchy

Next

- MetricsCollector implementation (file metrics, lines of code)

---

## Session 13 — 2026-07-26

Completed

- Implemented DependencyDetector (`backend/app/modules/analysis/dependency_detector.py`) — closed ManifestParser ABC hierarchy with 9 parsers: PackageJsonParser (npm `dependencies`/`devDependencies`/`peerDependencies`/`optionalDependencies` with dict version format), RequirementsParser (pinned versions, version ranges, editable git installs, comment/option skipping), PyProjectParser (PEP 621 `[project.dependencies]`, `[project.optional-dependencies]`, Poetry `[tool.poetry.dependencies]`/`[tool.poetry.dev-dependencies]`/`[tool.poetry.group.*.dependencies]`), PomParser (Maven groupId:artifactId, scope mapping, optional flag), GradleParser (implementation/api/testImplementation/compileOnly etc. with parenthesised and unparenthesised notation, best-effort), CargoParser (TOML `[dependencies]`/`[dev-dependencies]`/`[build-dependencies]`, table format, git deps), ComposerParser (PHP `require`/`require-dev`), GemfileParser (Ruby `gem` declarations with single/double quotes), CsProjParser (.NET PackageReference with Include/Version attributes)
- Created _RawDependency internal immutable intermediate model — decouples parsing from public DetectedDependency model
- Created _PARSER_REGISTRY module-level dict — data-driven filename-to-parser mapping, no conditional chains
- Created _resolve_parsers helper — exact name match + *.csproj wildcard fallback
- Created _merge_deduplicate function — dedup by (name, ecosystem, category), version conflict warning, sorted tuple source_files, deterministic output
- Implemented canonical category mapping per parser — runtime, development, build, peer, optional, system — using data-driven _CATEGORY_MAP dicts in each parser
- Updated DetectedDependency in types.py — added category: str = "runtime", changed source_file: str | None to source_files: tuple[str, ...] = ()
- All 207 tests in test_analysis pass (48 detector framework + 21 discovery + 45 framework detector + 93 dependency detector)

Files Created

- `backend/app/modules/analysis/dependency_detector.py` — DependencyDetector + 9 parsers + registry + dedup (450+ lines)
- `backend/tests/test_analysis/test_dependency_detector.py` — 93 tests across 12 test classes

Files Modified

- `backend/app/modules/analysis/types.py` — DetectedDependency: added category, renamed source_file → source_files
- `backend/tests/test_analysis/test_detector_framework.py` — Updated 2 tests for new DetectedDependency fields
- `docs/Legacy2Next_PROJECT_STATE.md` — Session 13, milestone progress, current task/focus

Testing Performed

- 93 new dependency detector tests: _RawDependency (3), PackageJsonParser (11), RequirementsParser (9), PyProjectParser (9), PomParser (6), GradleParser (6), CargoParser (7), ComposerParser (4), GemfileParser (6), CsProjParser (4), ParserRegistry (5), MergeDeduplicate (7), DependencyDetector integration (16)
- Full test_analysis suite: 207 tests, all passing

Architecture Decisions

- Closed parser hierarchy (one class per manifest format) rather than monolithic parser — each parser independently testable, no conditional chains
- _RawDependency intermediate model decouples parsing from the public DetectedDependency model — parsers return plain data, not domain objects
- Per-parser _CATEGORY_MAP dicts for canonical category mapping — data-driven, no conditional mapping logic
- Parsers return (list[_RawDependency], list[str]) — warnings as data, not exceptions; DependencyDetector owns logging and aggregation
- Gradle DSL marked as best-effort with regex-based extraction — partial results accepted, documented limitation
- Duplicates deduplicated by (name, ecosystem, category) — version conflicts emit warnings but preserve first-seen version
- source_files is tuple[str, ...] — immutable, iterable, JSON-serializable, deterministically sorted
- No metadata field, no confidence field, no version normalization — minimal factual model

Next

- MetricsCollector implementation (file metrics, lines of code)

---

## Session 14 — 2026-07-26

Completed

- Implemented MetricsCollector (`backend/app/modules/analysis/metrics_collector.py`) — single MetricsCollector class with private helper methods, pure aggregation from AnalysisResults only, zero I/O, deterministic output
- Created MetricKey StrEnum (`backend/app/modules/analysis/metric_keys.py`) — stable constants for 7 fixed metric keys (PROJECT_TOTAL_FILES, PROJECT_TOTAL_FILE_SIZE, LANGUAGE_COUNT, PRIMARY_LANGUAGE, FRAMEWORK_COUNT, DEPENDENCY_COUNT, MANIFEST_COUNT); dynamic ecosystem keys use f-strings
- Widened DetectedMetric.value from int to int | str in types.py — accommodates string-valued metrics like languages.primary
- Implemented 8 metric groups: project.total_files, project.total_file_size, languages.count, languages.primary (with alphabetical tie-breaking), frameworks.count, dependencies.count, dependencies.<ecosystem> (sorted), manifests.count
- Created 51 comprehensive tests across 14 test classes: empty results, single/multiple files, file counts, file sizes, language counting, primary language (with tie-breaking edge cases), framework counting, dependency counting, ecosystem grouping (alphabetical order, missing ecosystem fallback to "unknown"), manifest counting (case-insensitive filenames, .csproj extension), determinism (ordering, values, repeated execution), result integrity (metrics-only, detector name, immutability of AnalysisResults), full project integration, multiple detector results aggregation, MetricKey enum validation
- Updated ARCHITECTURE.md — added MetricsCollector aggregation stage section, updated analysis module status, updated architecture evolution
- Updated Legacy2Next_PROJECT_STATE.md — M4.4 complete, next tasks focused on AnalysisWriter
- Created CHANGELOG.md — documented M4.6B changes

Files Created

- `backend/app/modules/analysis/metrics_collector.py` — MetricsCollector class
- `backend/app/modules/analysis/metric_keys.py` — MetricKey(StrEnum)
- `backend/tests/test_analysis/test_metrics_collector.py` — 51 tests
- `docs/CHANGELOG.md` — Changelog

Files Modified

- `backend/app/modules/analysis/types.py` — DetectedMetric.value: int → int | str
- `docs/ARCHITECTURE.md` — MetricsCollector section, analysis status, evolution
- `docs/Legacy2Next_PROJECT_STATE.md` — Session 14, M4.4 complete, milestones, current state

Testing Performed

- 258 tests in test_analysis: 51 new metrics collector tests + 207 existing tests, all passing

Architecture Decisions

- MetricsCollector is NOT a BaseDetector subclass — it reads AnalysisResults, not DiscoveryContext
- Single class with private helper methods over calculator hierarchy — every metric is 1–3 lines of direct Python
- MetricKey StrEnum for fixed keys prevents typos (autocomplete, NameError on rename); dynamic ecosystem keys remain raw f-strings
- DetectedMetric.value widened to int | str — minimal change, no new fields, no new types
- Manifest detection reuses existing DetectedFile metadata (file_name/extension) — no file system access
- Missing ecosystem falls back to "unknown" to avoid silent data loss
- Case-insensitive manifest filename matching handles case variations (Gemfile, gemfile)
- Alphabetical tie-breaking for primary language ensures deterministic output (simpler than confidence-based ordering)

---

## Session 15 — 2026-07-26

Completed

- Implemented AnalysisPipeline (`backend/app/modules/analysis/pipeline.py`) — pure orchestration layer coordinating DiscoveryEngine, detectors, and MetricsCollector
- Added DetectorWarning frozen dataclass to types.py — structured warnings with detector_name and message fields
- Added warnings field to DetectorResult — `warnings: tuple[DetectorWarning, ...] = ()`, no existing behaviour changed
- Pipeline failure isolation: DiscoveryException propagates, detector exceptions are caught and wrapped as error DetectorResults, remaining detectors continue
- Sequential execution with constructor injection (engine, detectors, metrics_collector) — no service locator, no DI framework
- Created 27 comprehensive tests across 7 test classes: construction, successful execution (order, metric integration, final results), failure handling (discovery exception, error result continuation, raised exception wrapping, multi-failure, all-fail), warning preservation, timestamps, determinism, pipeline boundary (no logic leakage, no mutation, ID passthrough)
- Updated ARCHITECTURE.md — AnalysisPipeline section, folder structure, analysis status, next milestones
- Updated Legacy2Next_PROJECT_STATE.md — M4.7 complete, current goal/focus updated
- Updated CHANGELOG.md — M4.7B entry

Files Created

- `backend/app/modules/analysis/pipeline.py` — AnalysisPipeline class
- `backend/tests/test_analysis/test_pipeline.py` — 27 tests

Files Modified

- `backend/app/modules/analysis/types.py` — Added DetectorWarning, DetectorResult.warnings
- `docs/ARCHITECTURE.md` — Pipeline section, folder structure, status updates
- `docs/Legacy2Next_PROJECT_STATE.md` — Session 15, M4.7 complete, state updates
- `docs/CHANGELOG.md` — M4.7B entry

Testing Performed

- 285 tests in test_analysis: 27 new pipeline tests + 258 existing tests, all passing

Architecture Decisions

- AnalysisPipeline is a pure coordinator — no detection, no aggregation, no persistence
- Constructor injection with explicit types — engine: DiscoveryEngine, detectors: list[BaseDetector], metrics_collector: MetricsCollector
- DetectorWarning is a structured dataclass (not a string) — enables grouping by detector_name, future severity support, no string parsing
- DiscoveryException propagates to caller (no analysis without a valid project)
- All other exceptions caught and wrapped as DetectorResult with error string — never aborts the pipeline
- MetricsCollector receives an intermediate AnalysisResults built from detector results, then its DetectorResult is appended to the same list
- Warnings are preserved per-detector on DetectorResult — pipeline does not merge, rewrite, or inspect them
- Timestamps recorded at start and end of analyze() — no per-detector timing in the pipeline

---

## Session 16 — 2026-07-26

Completed

- Implemented AnalysisWriter (`backend/app/modules/analysis/writer.py`) — `AnalysisWriter` class with 6 write methods (files, technologies, dependencies, metrics, warnings, status), `PersistenceResult` dataclass collecting per-category error counts
- Created AnalysisWarning model (`backend/app/models/analysis_warning.py`) — FK to analyses table, detector_name and message columns
- Created AnalysisRepository (`backend/app/modules/analysis/repository.py`) — 6 batch helper functions: `batch_add_files`, `batch_add_technologies`, `batch_add_dependencies`, `batch_add_metrics`, `batch_add_warnings`, `update_analysis_status` — none commit, caller owns the transaction
- Widened Metric.value from `int` to `BigInteger` with nullable `value` (int) and `value_str` (Text) columns — exactly one populated per record
- Added `source_files` JSON column to Dependency model with `source_files_list` property accessor
- Created 26 tests in `test_writer.py` across 7 test classes: empty results, complete results, metrics (int+str+mixed), warnings (detector errors vs warnings), error aggregation single/multiple, deterministic output, transactional boundary (no commit, no rollback)
- Updated MetricKey references in existing tests for the value/value_str invariant

Files Created

- `backend/app/modules/analysis/writer.py` — AnalysisWriter + PersistenceResult
- `backend/app/models/analysis_warning.py` — AnalysisWarning model
- `backend/app/modules/analysis/repository.py` — 6 batch helpers
- `backend/tests/test_analysis/test_writer.py` — 26 tests

Files Modified

- `backend/app/models/metric.py` — value: BigInteger (nullable), value_str: Text
- `backend/app/models/dependency.py` — source_files: JSON, source_files_list property
- `backend/app/modules/analysis/types.py` — (no changes)
- `docs/CHANGELOG.md` — M4.8B entry
- `docs/ARCHITECTURE.md` — (updated)
- `docs/Legacy2Next_PROJECT_STATE.md` — This session

Testing Performed

- 311 tests in test_analysis: 26 new writer tests + 285 existing tests, all passing

Architecture Decisions

- Writer never commits, never rollbacks — caller owns the transaction boundary
- Metric invariant: exactly one of `value` or `value_str` populated; enforced by application logic
- Dependencies deduped on `(name, ecosystem)`; metrics deduped on `key`
- Status: `COMPLETED` (no errors) vs `COMPLETED_WITH_ERRORS` (detector errors during pipeline)
- `PersistenceResult` collects per-category error counts — non-zero means partial write, but caller decides action

Next

- API Integration for analysis endpoint

---

## Session 17 — 2026-07-26

Completed

- Implemented AnalysisService (`backend/app/modules/analysis/service.py`) — `run_analysis(db, user_id, upload_id) → AnalysisResponse` with full orchestration:
  - Upload ownership and project association validation
  - Analysis record creation (status=RUNNING, flush)
  - Pipeline construction with all 3 detectors (language, framework, dependency)
  - Pipeline execution → writer persistence → commit
  - On pipeline/writer exception: rollback + best-effort FAILED status persistence in a new transaction
  - Lifecycle logging (start, progress, completion, warnings, errors)
- Created AnalysisResponse schema (`backend/app/modules/analysis/schemas.py`) — `analysis_id: int`, `status: str`, `error_detail: str | None`
- Created analysis route (`backend/app/modules/analysis/routes.py`) — `POST /analysis/{upload_id}` with `get_current_user` and `get_db` dependencies, delegates entirely to `analysis_service.run_analysis()`
- Registered analysis router in `app/main.py` — included first, before auth router
- Created 27 integration tests in `test_api_integration.py` across 8 test classes:
  - Successful analysis (status=COMPLETED, analysis_id returned, response fields)
  - Upload not found (404), upload not owned (404), upload has no project (symmetry)
  - COMPLETED_WITH_ERRORS (pipeline with a failing detector — status set correctly, error_detail populated)
  - FAILED status from pipeline exception → rollback → FAILED
  - FAILED status from writer exception → rollback → FAILED
  - Transaction ownership verified (commit on success, rollback on failure, no orphan Analysis records)
  - AnalysisResponse correctness (analysis_id matches DB, status matches, error_detail shape)
  - End-to-end flow (upload → discovery → all detectors → metrics → persist → response)
  - Determinism (identical second run returns same results)
  - Concurrent analyses (two independent uploads analyzed simultaneously)

Files Created

- `backend/app/modules/analysis/service.py` — run_analysis()
- `backend/app/modules/analysis/schemas.py` — AnalysisResponse
- `backend/app/modules/analysis/routes.py` — POST endpoint
- `backend/tests/test_analysis/test_api_integration.py` — 27 tests

Files Modified

- `backend/app/main.py` — Registered analysis_router
- `backend/app/conftest.py` — (added session fixture for integration tests)
- `docs/CHANGELOG.md` — M4.9B entry
- `docs/ARCHITECTURE.md` — (updated)
- `docs/Legacy2Next_PROJECT_STATE.md` — This session

Testing Performed

- 338 tests in test_analysis: 27 new API integration tests + 311 existing tests, all passing

Architecture Decisions

- Service is the sole transaction owner — pipeline and writer never commit or rollback
- Best-effort FAILED persistence in a new transaction after rollback — uses same db session, wrapped in try/except
- Route contains zero business logic — pure delegation to service
- Pipeline uses db session from service (after flush, analysis.id is available) — no separate write-back step
- AnalysisResponse is a flat Pydantic model — no PersistenceResult or AnalysisResults leakage to API
- Future async migration: the `run_analysis` body is a pure function sequence extractable to a background worker

---

## Session 18 — 2026-07-26

Completed

- Created AnalysisQueryService (`backend/app/modules/analysis/query_service.py`) — 8 retrieval methods: `get_analysis_summary`, `get_analysis_files`, `get_analysis_technologies`, `get_analysis_dependencies`, `get_analysis_metrics`, `get_analysis_warnings`, `list_project_analyses`, `list_upload_analyses`
- Extended repository.py with 9 new read methods: `list_analysis_files_paginated`, `count_analysis_files`, `list_analysis_technologies_with_tech` (with joinedload), `list_dependencies_paginated`, `count_dependencies`, `list_warnings_paginated`, `count_warnings`, `list_analyses_by_project_paginated`, `list_analyses_by_upload_paginated`
- Added 8 response DTOs to schemas.py: `AnalysisSummaryResponse`, `AnalysisFileResponse`, `AnalysisTechnologyResponse`, `AnalysisDependencyResponse`, `AnalysisMetricResponse`, `AnalysisWarningResponse`, `AnalysisListItem`, `PaginatedResponse[T]`
- Extended routes.py with 8 GET endpoints: `GET /analysis/{id}` (summary), `/analysis/{id}/files`, `/analysis/{id}/technologies`, `/analysis/{id}/dependencies`, `/analysis/{id}/metrics`, `/analysis/{id}/warnings`, `/analysis/project/{id}`, `/analysis/upload/{id}`
- All routes in existing `routes.py` (no new router) — literal paths (project/upload) registered before path params to avoid routing conflicts
- Created 69 tests in test_query_api.py covering: summary endpoint (9 tests), files (8), technologies (6), dependencies (9), metrics (7), warnings (6), project analyses (7), upload analyses (6), ownership validation (2), DTO mapping (3), deterministic ordering (2), no-writes verification (2), empty analysis (1)

Files Created

- `backend/app/modules/analysis/query_service.py` — AnalysisQueryService
- `backend/tests/test_analysis/test_query_api.py` — 69 tests

Files Modified

- `backend/app/modules/analysis/repository.py` — Added 9 paginated/filtered read methods with sort and count helpers
- `backend/app/modules/analysis/schemas.py` — Added 8 response DTOs + PaginatedResponse
- `backend/app/modules/analysis/routes.py` — Added 8 GET endpoints
- `docs/ARCHITECTURE.md` — AnalysisQueryService section, updated folder structure, component table, test listing, milestone evolution
- `docs/CHANGELOG.md` — M5.1B entry
- `docs/Legacy2Next_PROJECT_STATE.md` — This session

Testing Performed

- 407 tests in test_analysis: 69 new query API tests + 338 existing tests, all passing

Architecture Decisions

- Read/write separation: AnalysisQueryService is completely independent from AnalysisService (no shared imports beyond repository + models)
- Repositories remain CRUD-only: joins and aggregation happen in the service layer
- Ownership validation walks FK chain: Analysis → Upload → Project → user_id
- Pagination uses offset/limit (page/size) — cursor pagination deferred until dataset grows
- Technologies and metrics return flat lists (unbounded, small datasets); files, dependencies, warnings paginated
- Literal path segments (project, upload) registered before path parameters to prevent Starlette routing conflicts
- DTOs isolate API from ORM — all 8 responses are Pydantic models with `from_attributes=True`

Next

- Milestone 5 — AI Integration planning

---

# Definition of Current State

Milestone 4 (Static Analysis) is **complete** with all 9 submodules implemented and tested. Milestone 5.1 (Analysis Retrieval) is also **complete**. Total: 407 tests in test_analysis, zero failures. Milestone 1 has 5 of 6 tasks complete (frontend setup remaining). Milestone 2 (Projects Module) is complete. Milestone 3 (Uploads Module) is complete.

The backend has a complete authentication system (register, login, JWT), Projects CRUD (5 endpoints, ownership-scoped), Uploads module (4 endpoints, file storage, quota, hash dedup), and Analysis module (14 endpoints — 6 POST + 8 GET) with Discovery Engine, Detector Framework (4 detectors), MetricsCollector, AnalysisPipeline, AnalysisWriter, API Integration, and Retrieval API. The application is containerized via Docker Compose with PostgreSQL 16 Alpine, with two Alembic migrations applied (5 base tables + 6 M4 analysis tables). Architecture is formally documented in `docs/ARCHITECTURE.md` with implemented/planned separation. Engineering decisions are in `docs/DECISIONS.md`. The HTTP API is in `docs/API_CONTRACT.md` covering all 13 implemented endpoints.

The next session should begin Milestone 5.2 (AI Integration) planning and implementation.