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

Version: 0.1.0

Current Phase: Development

Current Sprint: Sprint 1 - Project Foundation

Overall Progress: 20%

Status: In Progress

Last Updated: 2026-07-26

---

# Current Goal

Complete Milestone 1 — Project Foundation by finishing frontend setup, database configuration, Docker Compose, authentication implementation, and architecture documentation.

---

# Current Task

- Frontend initialization with React + TypeScript + Vite

---

# Current Focus

The current priority is completing the remaining Milestone 1 task: frontend setup.

---

# Completed

- Repository structure created (full backend directory tree, .gitignore, project configs)
- Backend initialized (FastAPI app factory, core layer with config/database/security/exceptions, SQLAlchemy models for User/Project/Analysis/Report, 8 module stubs with routes/services/schemas/repository separation, Alembic setup, test scaffolding, pyproject.toml with uv, Dockerfile, workers/ and integrations/ placeholders)
- PostgreSQL configured with connection pooling (`pool_size=5`, `max_overflow=10`, `pool_pre_ping=True`, `echo` driven by `DATABASE_ECHO`)
- Initial Alembic migration generated (`b1a1677bc7ef_initial_migration.py` — creates `users`, `projects`, `analyses`, `reports`)
- Docker Compose setup: `db` (PostgreSQL 16 Alpine) + `backend` (FastAPI) with health checks, named volumes, and default bridge networking
- Authentication system: register, login (JWT), password hashing (bcrypt via passlib), get_current_user dependency, protected `/auth/me` endpoint
- Architecture documentation: `docs/ARCHITECTURE.md` with implemented/planned separation, Mermaid diagrams, layer architecture, request lifecycle, authentication flow, database schema, Docker Compose architecture, error handling, module organisation, and architecture evolution roadmap

---

# In Progress

Milestone 1 — Project Foundation (5/6 tasks complete)

---

# Blockers

None.

---

# Next Tasks

1. Initialize React frontend with Vite + TypeScript + TailwindCSS

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

Status: Not Started

Tasks

- [ ] Project CRUD
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
├── ARCHITECTURE.md
├── Legacy2Next_MASTER_PLAN.md
├── Legacy2Next_AI_CONTEXT.md
├── Legacy2Next_PROJECT_STATE.md
└── initial_prompt.md

backend/
├── app/
│   ├── core/          (config, database, security, exceptions, dependencies)
│   ├── models/        (User, Project, Analysis, Report)
│   ├── modules/       (auth, projects, upload, analysis, ai, documentation, modernization, reports)
│   │   └── */         (routes, service, schemas, repository)
│   ├── workers/       (placeholder)
│   ├── integrations/  (placeholder)
│   └── utils/         (placeholder)
├── alembic/           (migration environment)
├── tests/             (conftest + test dirs per module)
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

# Definition of Current State

The project has moved from planning to active development (v0.1.0).

Milestone 1 is in progress with 5 of 6 tasks complete. The backend has a complete authentication system (register, login, JWT, protected endpoint), is containerized via Docker Compose with PostgreSQL 16 Alpine, and has the initial Alembic migration applied. The backend skeleton is fully established with a modular FastAPI structure, SQLAlchemy models, Alembic migrations, and all 8 feature modules scaffolded with routes, services, schemas, and repository separation. Architecture is formally documented in `docs/ARCHITECTURE.md` with implemented/planned separation.

The next session should initialize the frontend — the last remaining Milestone 1 task.