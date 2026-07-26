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

Version: 0.2.0

Current Phase: Development

Current Sprint: Sprint 2 - Project Management

Overall Progress: 30%

Status: In Progress

Last Updated: 2026-07-26

---

# Current Goal

Complete Milestone 2 — Project Management by implementing the remaining tasks: ZIP upload, file extraction, and project storage.

---

# Current Task

- Upload module implementation (ZIP upload, file extraction, project storage)

---

# Current Focus

The current priority is completing the Upload module — the remaining Milestone 2 task.

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

---

# In Progress

Milestone 2 — Project Management (1/3 tasks complete)

---

# Blockers

None.

---

# Next Tasks

1. Implement Upload module (ZIP upload, file extraction, project storage)

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

## Milestone 2 — Project Management

Status: In Progress (1/3)

Tasks

- [x] Project CRUD
- [ ] ZIP Upload
- [ ] Project Storage

---

## Milestone 3 — Static Analysis

Status: Not Started

Tasks

- [ ] Language Detection
- [ ] Framework Detection
- [ ] Dependency Analysis
- [ ] File Metadata Extraction

---

## Milestone 4 — AI Integration

Status: Not Started

Tasks

- [ ] AI Project Summary
- [ ] AI File Explanation
- [ ] AI Documentation
- [ ] AI Recommendations

---

## Milestone 5 — Dashboard

Status: Not Started

Tasks

- [ ] Dashboard
- [ ] Reports
- [ ] Documentation Viewer

---

## Milestone 6 — Finalization

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
│   ├── models/        (User, Project, Analysis, Report)
│   ├── modules/       (auth, projects, upload, analysis, ai, documentation, modernization, reports)
│   │   ├── auth/      (fully implemented)
│   │   ├── projects/  (fully implemented)
│   │   └── */         (scaffolded — routes, service, schemas, repository)
│   ├── workers/       (placeholder)
│   ├── integrations/  (placeholder)
│   └── utils/         (placeholder)
├── alembic/           (migration environment)
├── tests/             (conftest + test dirs per module, all empty)
├── uploads/           (extracted project storage)
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

# Definition of Current State

The project has moved from planning to active development (v0.2.0).

Milestone 1 is in progress with 5 of 6 tasks complete (frontend setup remaining). Milestone 2 is in progress with 1 of 3 tasks complete (Project CRUD done). The backend has a complete authentication system (register, login, JWT, protected endpoint) and a complete Projects CRUD module (5 endpoints, ownership-scoped). The application is containerized via Docker Compose with PostgreSQL 16 Alpine, and has the initial Alembic migration applied. Architecture is formally documented in `docs/ARCHITECTURE.md` with implemented/planned separation. Engineering decisions are recorded in `docs/DECISIONS.md`. The HTTP API is documented in `docs/API_CONTRACT.md` covering all 9 implemented endpoints with schemas, validation rules, error codes, and behaviour origins.

The next session should implement the Upload module — the remaining Milestone 2 tasks (ZIP upload, file extraction, project storage).