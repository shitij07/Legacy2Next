# Engineering Decisions

**Project:** Legacy2Next
**Purpose:** Record important engineering and architectural decisions.
**Status:** Living document
**Last Updated:** 2026-07-26

---

# Decision Index

| ID | Decision |
|----|----------|
| D001 | FastAPI |
| D002 | SQLAlchemy ORM |
| D003 | PostgreSQL |
| D004 | PEP 621 pyproject.toml |
| D005 | Repository Pattern |
| D006 | Service Layer |
| D007 | Centralised Models |
| D008 | Consistent Module Structure |
| D009 | Alembic Migrations |
| D010 | Explicit Database Migrations |
| D011 | JWT Authentication |
| D012 | Stateless Authentication |
| D013 | bcrypt via passlib |
| D014 | bcrypt Version Pin |
| D015 | Registration Does Not Issue JWT |
| D016 | Docker Compose for Development |
| D017 | Explicit Package Discovery in pyproject.toml |
| D018 | Deferred Authentication Features |

---

## D001 — FastAPI

### Context

The backend REST API needs a Python web framework. The project requires async support for future non-blocking analysis tasks, automatic API documentation for developer experience, and built-in request validation.

### Decision

Use FastAPI as the web framework.

### Rationale

FastAPI provides native async support, automatic OpenAPI documentation generation, built-in dependency injection via `Depends()`, and Pydantic integration for request/response validation. These capabilities match the project's need for a developer-friendly API backend without requiring additional libraries. The framework is documented in `pyproject.toml` as `fastapi>=0.111.0` and used in `app/main.py`.

### Consequences

#### Benefits

- Auto-generated OpenAPI docs at `/docs` and `/redoc`
- Request validation via Pydantic without additional code
- Dependency injection via `Depends()` manages DB sessions and auth
- Async support available when analysis modules are implemented

#### Trade-offs

- Smaller ecosystem than Django (fewer built-in admin/ORM features)
- Less prescriptive than Django — requires explicit architectural decisions

### Alternatives Considered

- **Django**: Batteries-included but synchronous by default, heavier, no native async views until recent versions. Not aligned with the project's modular architecture.
- **Flask**: Minimal and flexible but lacks built-in validation, dependency injection, and auto-generated OpenAPI docs. Would require adding these capabilities manually.

### Future Revisit

Not needed under current requirements. FastAPI remains appropriate for the project's scale and architecture.

---

## D002 — SQLAlchemy ORM

### Context

The application needs persistent storage for users, projects, analyses, and reports. The ORM must support complex queries, work with Alembic for schema migrations, and integrate with FastAPI.

### Decision

Use SQLAlchemy as the ORM.

### Rationale

SQLAlchemy is the most mature Python ORM with extensive query capabilities, database-agnostic abstraction, strong community integration patterns with FastAPI, and native Alembic migration support. It is declared in `pyproject.toml` as `sqlalchemy>=2.0.0` and used throughout `app/core/database.py` and `app/models/`.

### Consequences

#### Benefits

- Mature, well-documented, and widely adopted
- Database-agnostic (can switch from PostgreSQL if needed)
- Strong typing with Mypy support
- Extensive query capabilities for future analysis data

#### Trade-offs

- Heavier than raw SQL for simple queries
- Requires learning SQLAlchemy's ORM and query APIs

### Alternatives Considered

- **Raw SQL with psycopg2**: No ORM benefits, harder to maintain, no migration tool integration, error-prone for complex queries.
- **Django ORM**: Tightly coupled to Django framework, not compatible with the selected FastAPI architecture.

### Future Revisit

Not needed under current requirements.

---

## D003 — PostgreSQL

### Context

The relational database must support ACID transactions for user and project data, JSON columns for flexible analysis results, full-text search for code search, and future pgvector compatibility for AI-powered features.

### Decision

Use PostgreSQL as the database.

### Rationale

PostgreSQL is ACID-compliant, supports JSON columns natively, has built-in full-text search, and is compatible with pgvector for future AI embedding storage. The database runs in Docker via `postgres:16-alpine` (`docker-compose.yml`), and the connection is configured through `psycopg2-binary>=2.9.0` in `pyproject.toml`.

### Consequences

#### Benefits

- ACID compliance for transactional integrity
- JSON support for semi-structured analysis results
- Full-text search for future code search features
- pgvector compatible for AI embedding storage
- Strong community and operational maturity

#### Trade-offs

- Heavier than SQLite for local development
- Requires Docker or local PostgreSQL installation

### Alternatives Considered

- **SQLite**: No concurrent write support, limited JSON capabilities, no full-text search suitable for code, incompatible with pgvector.
- **MySQL**: Weaker JSON support, no native pgvector compatibility, different full-text search implementation.

### Future Revisit

If the project scales beyond single-instance PostgreSQL, consider managed cloud PostgreSQL (RDS, Cloud SQL) or connection pooling via PgBouncer.

---

## D004 — PEP 621 pyproject.toml

### Context

The project needs a standards-compliant dependency management format that works with the `uv` package manager and supports optional dependency groups for development tools.

### Decision

Use `pyproject.toml` with PEP 621 format instead of `requirements.txt`.

### Rationale

PEP 621 is the modern Python packaging standard. The single `pyproject.toml` file (`backend/pyproject.toml`) defines dependencies, optional dependency groups (dev tools like pytest, ruff, mypy), and tool configurations (ruff, mypy) in one place. This format is required by `uv` and eliminates the need for multiple `requirements*.txt` files.

### Consequences

#### Benefits

- Single file for dependencies, tool config, and build metadata
- Compatible with `uv` (fast package installer)
- Optional dependency groups separate dev and production dependencies
- No need for multiple requirements files

#### Trade-offs

- Less familiar to developers accustomed to `requirements.txt`
- Some legacy tools may not read `pyproject.toml`

### Alternatives Considered

- **requirements.txt + requirements-dev.txt**: Familiar but no standard tool config integration, not compatible with `uv` for builds.

### Future Revisit

Not needed.

---

## D005 — Repository Pattern

### Context

Database access logic needs to be separated from business logic to keep services testable and maintainable across multiple feature modules.

### Decision

Implement a repository layer in each feature module.

### Rationale

Each feature module contains a `repository.py` file that encapsulates all SQLAlchemy queries for that module's domain. Services call repository functions rather than querying the database directly. This separation is documented in `PROJECT_STATE.md`: "Repository layer separated from services (empty placeholders) to enforce data-access abstraction from the start." The auth module implements this pattern with `get_by_email`, `get_by_id`, and `create` in `app/modules/auth/repository.py`.

### Consequences

#### Benefits

- Business logic remains free of SQLAlchemy query code
- Repositories can be mocked in unit tests
- Consistent data access pattern across all modules
- Database implementation can be changed without affecting services

#### Trade-offs

- Extra abstraction layer increases file count per module
- Simple CRUD operations require 4 files instead of 2

### Alternatives Considered

- **Direct database access in services**: Faster to write initially but couples business logic to ORM queries, making testing harder and reducing flexibility.

### Future Revisit

Consider if the abstraction overhead outweighs benefits for very simple CRUD operations, but maintain pattern consistency.

---

## D006 — Service Layer

### Context

Business logic should be separated from HTTP handling to keep route handlers thin and enable testing business rules independently of the HTTP layer.

### Decision

Implement a service layer in each feature module.

### Rationale

Each feature module contains a `service.py` file that holds business rules and orchestration logic. Route handlers delegate to service functions and only manage HTTP concerns (request parsing, status codes, response serialization). The auth module demonstrates this with `register`, `login`, and `get_current_user` in `app/modules/auth/service.py` called from `app/modules/auth/routes.py`.

### Consequences

#### Benefits

- Route handlers are thin and focused on HTTP concerns
- Business logic is testable without HTTP fixtures
- Service functions can be reused across multiple endpoints
- Clear responsibility boundaries between layers

#### Trade-offs

- Additional layer adds boilerplate for simple endpoints
- Not all modules currently implement meaningful service logic (7 are stubs)

### Alternatives Considered

- **Fat routes with business logic in handlers**: Faster to write initially but harder to test, less reusable, and violates separation of concerns.

### Future Revisit

Not needed; the pattern is already established across all modules.

---

## D007 — Centralised Models

### Context

SQLAlchemy models must be shared across feature modules without causing circular import chains, particularly when models reference foreign keys from other modules.

### Decision

Centralise all SQLAlchemy models under `app/models/` with a single `__init__.py` re-export.

### Rationale

If each module defined its own models, modules that reference foreign keys from other modules would create circular import chains. Centralising all models in `app/models/` with `__init__.py` re-exporting `User`, `Project`, `Analysis`, and `Report` decouples model definitions from feature module business logic. This is documented in `PROJECT_STATE.md`: "SQLAlchemy models centralized in `app/models/` to avoid circular foreign-key imports across modules."

### Consequences

#### Benefits

- No circular import issues between modules
- Single source of truth for the database schema
- Easy to locate all model definitions in one directory

#### Trade-offs

- Models are physically separated from the modules that use them (e.g., `User` is in `models/`, not `modules/auth/`)

### Alternatives Considered

- **Models colocated with modules**: Causes circular imports when modules reference foreign keys from other modules (e.g., Project has FK to User; auth module needs Project).

### Future Revisit

Not needed; this is a foundation decision that avoids a known circular import problem.

---

## D008 — Consistent Module Structure

### Context

Eight feature modules exist in the repository. A standard file layout is needed to ensure predictability, navigability, and maintainability across all modules.

### Decision

Each feature module follows a consistent 4-file layout: `routes.py`, `service.py`, `schemas.py`, `repository.py`.

### Rationale

A predictable file layout reduces cognitive load when navigating the codebase. Every contributor (human or AI) knows exactly where to find HTTP endpoints, business logic, Pydantic models, and database queries for any feature module. This structure is established across all 8 modules under `app/modules/` and documented in `ARCHITECTURE.md`.

### Consequences

#### Benefits

- Predictable navigation across all modules
- Enforced separation of concerns
- Easy onboarding for new contributors
- All 8 modules follow the same convention

#### Trade-offs

- Even trivial modules with one endpoint require 4 files
- The `upload` module is missing `schemas.py`, breaking consistency

### Alternatives Considered

- **Flat structure** (all routes in one `routers/`, all services in one `services/`): Simpler for small projects but becomes unmanageable as the number of feature domains grows.

### Future Revisit

Not needed; the structure is established across all modules. The `upload` module's missing `schemas.py` should be added to restore full consistency.

---

## D009 — Alembic Migrations

### Context

The database schema will evolve as new features are implemented. A version-controlled migration system is needed to track and apply schema changes reliably.

### Decision

Use Alembic with autogenerate support for database migrations.

### Rationale

Alembic is the standard migration tool for SQLAlchemy. Autogenerate detects model changes and produces migration scripts, reducing manual schema-writing errors. The migration environment is configured in `backend/alembic/` with `env.py` importing models from `app.models.*` and overriding `sqlalchemy.url` from `Settings.DATABASE_URL` at runtime. The initial migration (`b1a1677bc7ef_initial_migration.py`) creates all 4 tables with foreign keys and indexes.

### Consequences

#### Benefits

- Autogenerate reduces manual migration writing
- Version-controlled, repeatable upgrades and downgrades
- Standard in the SQLAlchemy ecosystem
- Migration scripts are reviewable before applying

#### Trade-offs

- Autogenerated migrations require review before applying
- Complex schema changes may need manual adjustment of autogenerated scripts

### Alternatives Considered

- **Manual SQL migrations**: No autogenerate support, error-prone, more verbose.
- **No migration system**: Schema must match models at all times, dangerous for any environment beyond development.

### Future Revisit

Not needed.

---

## D010 — Explicit Database Migrations

### Context

Docker Compose orchestrates both services but should not apply database schema changes automatically.

### Decision

Do not run migrations automatically on container startup. Developers apply migrations explicitly with `alembic upgrade head`.

### Rationale

Auto-migration on startup risks applying unintended schema changes, especially during rapid development when models change frequently. Explicit migration control gives the developer the opportunity to review, test, and apply changes deliberately. The Dockerfile (`backend/Dockerfile`) and `docker-compose.yml` contain no migration commands. This is documented in `PROJECT_STATE.md`: "No automatic migration on startup — migrations are explicit developer actions."

### Consequences

#### Benefits

- Developer has full control over when schema changes are applied
- No risk of surprise migrations on container restart
- Migration scripts can be reviewed before applying

#### Trade-offs

- Manual step required after every model change
- Docker Compose setup is not fully automated (requires manual migration step)

### Alternatives Considered

- **Auto-migration in Docker entrypoint**: Convenient but risky — could apply unintended changes, fail silently, or apply migrations in the wrong order.

### Future Revisit

If the project gains multiple developers, consider automating migration in CI/CD pipelines while keeping local development explicit.

---

## D011 — JWT Authentication

### Context

The REST API needs a stateless authentication mechanism that does not require server-side session storage.

### Decision

Use JWT (JSON Web Tokens) with HS256 algorithm for authentication.

### Rationale

JWT is a stateless token format that requires no server-side session storage. The token contains all necessary claims (`sub`, `iat`, `exp`) and is cryptographically verified on each request. HS256 is appropriate for a single-service backend where token signing and verification happen on the same server. Implemented in `app/core/security.py` using `python-jose` with `create_access_token` and `decode_access_token` functions. The library is declared in `pyproject.toml` as `python-jose[cryptography]>=3.3.0`.

### Consequences

#### Benefits

- Stateless — no session storage required
- Standard token format with wide library support
- Compact token size for HTTP headers
- Built-in expiration via `exp` claim

#### Trade-offs

- HS256 is symmetric (same key signs and verifies)
- Token revocation is not possible without a blacklist
- Compromised secret key allows forging arbitrary tokens

### Alternatives Considered

- **Session-based auth**: Requires server-side session storage, harder to scale across multiple instances, more complex than needed for MVP.
- **OAuth2 as framework**: Overkill for a single-developer MVP with no third-party identity providers.
- **API keys**: No user context, harder to expire without server-side state.

### Future Revisit

Consider RS256 (asymmetric) if the backend is split into multiple services. Consider OAuth2 if third-party identity providers are needed.

---

## D012 — Stateless Authentication

### Context

JWT tokens expire after 30 minutes. No refresh token mechanism or token blacklist is implemented.

### Decision

Use stateless JWT with no refresh tokens and no token blacklist. Logout is handled client-side by discarding the token.

### Rationale

For an MVP with a single developer, 30-minute session expiry is sufficient. Refresh tokens add complexity (storage, rotation, endpoint management) without immediate benefit. Token blacklisting requires server-side storage, which defeats the stateless benefit of JWTs. This is documented in `PROJECT_STATE.md`: "Stateless JWT, no refresh tokens, no token blacklist (client-side discard on logout)."

### Consequences

#### Benefits

- Simple implementation with no server-side session state
- No token rotation or refresh logic to maintain
- No blacklist storage or cleanup required

#### Trade-offs

- Users must re-authenticate every 30 minutes
- Tokens cannot be revoked server-side before expiration

### Alternatives Considered

- **Refresh tokens**: Enables longer sessions without re-login, but adds storage, rotation, and endpoint complexity.
- **Token blacklist**: Enables immediate revocation of specific tokens but adds server-side state and defeats the stateless design.

### Future Revisit

See D018 (Deferred Authentication Features).

---

## D013 — bcrypt via passlib

### Context

User passwords must be hashed securely before storage in the database.

### Decision

Use passlib with the bcrypt backend for password hashing.

### Rationale

passlib provides a unified API for multiple hashing schemes and auto-manages algorithm upgrades via `CryptContext`. The bcrypt backend is the industry standard for password hashing — computationally expensive, includes salts automatically, and resists brute-force attacks. Implemented in `app/core/security.py` with `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`. The library is declared in `pyproject.toml` as `passlib[bcrypt]>=1.7.4`.

### Consequences

#### Benefits

- passlib abstracts hashing algorithm selection and future upgrades
- `CryptContext` handles deprecated scheme transitions automatically
- bcrypt is battle-tested and recommended for password storage

#### Trade-offs

- passlib adds an extra dependency layer over direct bcrypt usage
- passlib is less actively maintained than bcrypt itself
- bcrypt version pinning was required for compatibility (see D014)

### Alternatives Considered

- **Direct bcrypt**: Less abstraction, requires manual salt management, no built-in algorithm upgrade path.
- **argon2**: Newer and stronger, but less ecosystem support and not available through passlib's default backends.

### Future Revisit

Consider adding argon2 as a secondary scheme via passlib `CryptContext` if hardware allows and security requirements increase.

---

## D014 — bcrypt Version Pin

### Context

passlib's internal `_bcrypt.hashpw` call is incompatible with bcrypt 4.1.0 and later, causing a `RuntimeError` during password verification.

### Decision

Pin bcrypt to `>=4.0.0, <4.1.0` in `pyproject.toml`.

### Rationale

bcrypt 4.1.0 changed its internal C implementation, breaking passlib's workaround for the original bcrypt API. Pinning to `<4.1.0` ensures compatibility until passlib is updated or replaced. Declared in `pyproject.toml` line 14: `"bcrypt>=4.0.0,<4.1.0"`. Documented in `PROJECT_STATE.md`: "`bcrypt<4.1.0` pinned because `passlib`'s internal `_bcrypt.hashpw` call is incompatible with bcrypt 4.1.0+."

### Consequences

#### Benefits

- Immediate fix for the passlib runtime error
- No code changes required in `security.py`
- Existing tests continue to pass

#### Trade-offs

- Prevents upgrading bcrypt until passlib releases a compatible update
- Requires maintaining a manual version constraint

### Alternatives Considered

- **Switch from passlib to direct bcrypt**: Would remove the abstraction layer entirely, requiring manual algorithm management.
- **Vendor a fixed version of passlib**: Unmaintainable in the long term.

### Future Revisit

Revisit when passlib releases a version compatible with bcrypt 4.1.0+, or when the project replaces passlib with a different hashing library.

---

## D015 — Registration Does Not Issue JWT

### Context

`POST /auth/register` could either return a JWT token (auto-login on registration) or return only the user profile.

### Decision

Registration returns the user profile with HTTP 201 without issuing a JWT. Authentication occurs only through `POST /auth/login`.

### Rationale

Separating registration from authentication follows the principle of explicit actions — creating an account and logging in are distinct operations. The client can validate the registration response before independently logging in. The auth module implements this in `app/modules/auth/routes.py:register` returning `UserResponse` and `app/modules/auth/service.py:register` returning the `User` object directly. Documented in `PROJECT_STATE.md`: "Registration returns user profile without issuing a JWT; tokens are only issued via `/auth/login`."

### Consequences

#### Benefits

- Clear separation of registration and login responsibilities
- Registration endpoint is effectively idempotent (duplicate email returns 409)
- No implicit token creation on account creation

#### Trade-offs

- Client must make two API calls (register, then login) if auto-login after registration is desired

### Alternatives Considered

- **Register and return JWT in a single step**: Conflates account creation with authentication, hides the login step, and makes it unclear whether registration failed due to an account issue or an auth issue.

### Future Revisit

Not needed; this is the established authentication flow.

---

## D016 — Docker Compose for Development

### Context

The development environment needs PostgreSQL and the FastAPI backend orchestrated together with a single command, without requiring developers to install PostgreSQL locally.

### Decision

Use Docker Compose with two services (`db` and `backend`), named volumes, health checks, and default bridge networking.

### Rationale

Docker Compose provides a single-command setup (`docker compose up --build`) for the entire development stack. Named volumes (`pgdata`, `uploads`) persist data across container restarts. PostgreSQL health checks ensure the backend waits for the database before starting. The composition is defined in `docker-compose.yml` at the repository root and documented in `PROJECT_STATE.md` Session 4.

### Consequences

#### Benefits

- Single command starts the full development stack
- No manual PostgreSQL installation required
- Data persists across container restarts via named volumes
- Environment matches CI and production configurations

#### Trade-offs

- Docker adds resource overhead compared to native PostgreSQL
- Networking complexity — backend connects to `db` hostname, not `localhost`
- PostgreSQL port not exposed to host (requires Docker network for direct DB access)

### Alternatives Considered

- **Local PostgreSQL installation**: No Docker overhead but requires manual setup, version management, and risks conflicting with other projects.
- **Managed cloud database**: Costly for development, adds network latency.

### Future Revisit

When the project adds more services (background workers, AI inference), consider Docker Compose profiles or multi-stage orchestration. For production, consider Kubernetes or cloud container services.

---

## D017 — Explicit Package Discovery in pyproject.toml

### Context

Docker build failed with a setuptools flat-layout error because the backend directory contains multiple top-level Python packages (`app/` and `alembic/`).

### Decision

Add `[tool.setuptools.packages.find]` with `include = ["app*"]` to `pyproject.toml`.

### Rationale

setuptools' default flat-layout package discovery detects both `app/` and `alembic/` as top-level packages, causing a build error: "Multiple top-level packages discovered in a flat-layout." Explicitly limiting package discovery to `app*` resolves this without changing the directory structure. The configuration is at `backend/pyproject.toml` lines 34-35 and documented in `PROJECT_STATE.md` Session 4.

### Consequences

#### Benefits

- Docker build succeeds without directory restructuring
- Standard Alembic directory layout is preserved
- `alembic/` is correctly excluded from the installed package

#### Trade-offs

- `alembic` cannot be imported as an installed package (it runs from source during development only)

### Alternatives Considered

- **Move `alembic/` into `app/` or a subdirectory**: Would change the standard Alembic directory layout and break convention.

### Future Revisit

If `alembic` needs to be distributed as part of the installed package (e.g., for runtime migrations in production), revisit the include pattern or restructure the repository.

---

## D018 — Deferred Authentication Features

### Context

The auth module implements only the minimum authentication flow: registration, login, and JWT-based identity verification. Several common authentication features are intentionally excluded from Milestone 1 to keep the foundation focused.

### Decision

Defer the following authentication features:

### Refresh Tokens

#### Why Deferred

30-minute JWT expiry is acceptable for a single-developer MVP. The client can re-authenticate via `POST /auth/login` when the token expires. Implementing refresh tokens would add storage for refresh token families, rotation logic, and a new endpoint — complexity with no immediate benefit.

#### Benefits of Deferring

- No storage or rotation logic to implement or test
- No refresh token endpoint to maintain
- Simpler authentication flow for the client

#### Trade-offs

- Users re-authenticate every 30 minutes
- Sessions cannot survive token expiry
- Not suitable for long-running background tasks

#### Conditions for Revisiting

Implement when multiple concurrent client sessions are needed, long-running background tasks require token validity beyond 30 minutes, or user feedback indicates frequent re-login is disruptive.

---

### RBAC / Authorization

#### Why Deferred

Only the auth module is implemented. There are no resources to protect beyond user identity. Binary authentication (authenticated vs not) is sufficient until module-scoped permissions are needed.

#### Benefits of Deferring

- No role model, permission system, or access control lists to design
- No admin/user distinction to maintain
- Simpler endpoint implementation

#### Trade-offs

- All authenticated users have identical access
- No way to restrict feature access per-role
- Adding RBAC later requires retrofitting permission checks into all endpoints

#### Conditions for Revisiting

Implement when the Projects module (M2) requires per-user data isolation, or when multi-tenant access patterns emerge.

---

### Email Verification

#### Why Deferred

Registration without email confirmation simplifies the MVP. The project has no email delivery infrastructure, no email templates, and no verification token handling. Adding email verification would require an email provider integration, verification token storage and expiry, resend logic, and confirmation endpoints.

#### Benefits of Deferring

- No email provider setup or configuration
- No verification token storage or cleanup
- No email templates to create and maintain
- No resend logic or rate limiting

#### Trade-offs

- Users can register with invalid or mistyped email addresses
- No way to recover accounts via email
- Reduced trust in user identity

#### Conditions for Revisiting

Implement when the project prepares for production deployment with real users beyond the developer, or when password reset (which shares the email infrastructure) is also implemented.

---

### Password Reset

#### Why Deferred

Password reset requires email delivery infrastructure to send reset links securely. Without email verification, password reset has no mechanism to confirm user identity before issuing a reset token.

#### Benefits of Deferring

- No reset token endpoints or expiry logic
- No email delivery for reset links
- No rate limiting for reset requests

#### Trade-offs

- Users must contact the developer to reset passwords
- No self-service password recovery
- Account recovery depends on manual intervention

#### Conditions for Revisiting

Implement when email verification is implemented — both features share the same email delivery infrastructure, verification token patterns, and operational concerns.
