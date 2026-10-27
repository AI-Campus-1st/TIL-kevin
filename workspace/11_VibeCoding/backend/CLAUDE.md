---
# Repository Instructions

## Service

Python FastAPI service exposing REST APIs for authentication, domain logic, AI orchestration, and data persistence.

## Stack

- Python 3.12
- FastAPI + Uvicorn
- Pydantic v2 + pydantic-settings
- Supabase PostgreSQL + `supabase-py`
- LangChain + provider-specific integrations
- pytest + FastAPI TestClient / httpx
- Ruff + mypy
- Alembic, if established in the repository

## Environment Management

- Use `uv` to manage the Python environment, dependencies, and lockfile.
- Declare dependencies in `pyproject.toml` and keep `uv.lock` synchronized.
- Use `uv sync` to install dependencies and `uv run` to execute commands.

## Structure

- `app/api/`: API routes and HTTP request/response mapping
- `app/schemas/`: Pydantic request and response schemas
- `app/services/`: Application use cases and orchestration
- `app/repositories/`: Persistence operations
- `app/models/`: Database and persistence models
- `app/domain/`: Domain entities, business rules, and deterministic calculations
- `app/integrations/`: AI providers and external service adapters
- `app/core/`: Configuration, authentication, security, and shared infrastructure
- `tests/`: Unit, integration, and API tests

Follow the existing repository structure. Introduce new modules only when justified by domain complexity or separation of responsibility.

## Architecture

- Keep API routes thin. Delegate application workflows to services.
- Keep domain logic independent of FastAPI, Supabase, LangChain, and provider-specific SDKs.
- Keep database queries inside repositories and business rules inside domain or application services.
- Use explicit interfaces at infrastructure boundaries when they improve testability or implementation interchangeability.
- Apply Repository, Service Layer, Dependency Injection, and Adapter patterns where appropriate. Use Strategy or Factory patterns only when genuine variation or complex construction requires them.
- Use FastAPI dependencies at the API boundary. Avoid coupling domain logic to framework-specific dependency mechanisms.
- Keep persistence models, API schemas, and domain representations separate when their responsibilities differ.
- Convert internal and domain exceptions into the established API error format. Never expose stack traces, SQL errors, or provider internals.

## API & Security

- Define typed request and response contracts using Pydantic v2 and FastAPI OpenAPI.
- Validate external input on the server, including business constraints not covered by schema validation.
- Verify Supabase JWT signatures, issuer, expiration, and required claims before trusting user identity.
- Derive user identity from the validated authentication context. Never trust request-supplied user IDs as proof of ownership.
- Enforce resource-level authorization and Supabase Row Level Security (RLS).
- Do not use the Supabase `service_role` key for ordinary user requests.
- Keep LLM API keys and server credentials in environment variables or approved secret management systems.
- Restrict external URL fetching to permitted protocols and destinations. Block localhost and private networks, and enforce timeouts and response-size limits.

## Database

- Encapsulate persistence operations in repositories.
- Follow the repository's established Supabase and migration conventions. Do not introduce a competing migration mechanism without approval.
- Never edit applied migration files.
- Include downgrade behavior and data backfill plans where applicable.
- Use transactions for multi-step operations requiring atomicity.
- Preserve user-level data isolation and existing records.

## AI Integration

- Keep prompts, LLM calls, and LangChain orchestration out of API route handlers.
- Encapsulate AI workflows in application services. Access provider-specific SDKs through adapters that normalize provider responses into a shared internal format.
- Use provider-specific SDKs through dedicated adapters:
  - OpenAI: `openai`
  - Google Gemini: `google-genai`
- Define structured AI outputs with Pydantic schemas. Validate both schema structure and domain constraints before accepting or persisting results.
- Treat AI output as untrusted input; schema validity does not guarantee semantic correctness.
- Use deterministic Python logic for ingredient quantities, serving adjustments, unit compatibility, date calculations, and shopping-list aggregation.
- Centralize provider configuration, model selection, timeouts, retry limits, and token budgets.
- Make AI services independently testable through injectable dependencies or provider interfaces.
- Avoid logging sensitive user data, prompts, or responses unnecessarily.

## Testing & Validation

- Use unit tests for domain rules and services, integration tests for persistence, and API tests for validation, authentication, authorization, and error handling.
- Reuse existing fixtures and FastAPI dependency overrides.
- Mock external HTTP requests and AI providers in unit tests. Do not require live provider credentials for routine tests.
- Cover success, validation failure, authorization failure, provider errors, timeouts, and malformed AI responses where applicable.
- Keep tests deterministic and isolate shared state.
- Run relevant tests, `ruff check .`, `ruff format --check .`, and `mypy app`.
- Validate migrations when database schemas change.

## Commands

- Install dependencies: use the repository's configured package manager, preferably `uv` when configured
- Start API: `uvicorn app.main:app --reload`
- Run tests: `pytest`
- Run focused tests: `pytest path/to/test_file.py -k "test_name"`
- Lint: `ruff check .`
- Format check: `ruff format --check .`
- Type check: `mypy app`
- Validate migrations: `alembic check`

Use the actual scripts and dependency configuration defined by the repository.
---