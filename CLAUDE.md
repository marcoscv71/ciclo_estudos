# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

FastAPI + SQLAlchemy 2 backend for tracking a study cycle ("ciclo de estudos"). Subjects have target hours. Study sessions record minutes against the currently open cycle. A cycle is "advanced" by closing it and opening the next numbered one. The app targets a separate frontend at `localhost:5173` (CORS is configured in `app.py`). It uses Python 3.14, is managed with `uv`, and runs tasks through `poe` (poethepoet).

## Commands

```bash
uv sync                          # install deps (incl. dev group)
uv run poe serve                 # fastapi dev server (src/ciclo_estudos/app.py)
uv run poe lint                  # ruff check
uv run poe format                # ruff check --fix + ruff format
uv run poe test                  # lint, then pytest -s -x -vv, then coverage html
uv run poe test tests/test_cycles.py::test_name   # extra args are forwarded to pytest
uv run pytest tests/test_cycles.py -k name        # run pytest directly (skips lint/coverage html)
uv run alembic upgrade head      # apply migrations
uv run alembic revision --autogenerate -m "msg"   # new migration from models
uv run poe seed                  # interactive: seeds the default subjects + optional initial user
uv run typos                     # spell check (dev dependency)
```

pytest always runs with `--random-order` and coverage (`--cov-context=test`), so tests must not depend on execution order.

## Configuration

`Settings` (`settings.py`, pydantic-settings) reads `.env`. Required keys: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`. `ALLOW_REGISTRATION` defaults to `false`, and while it is false `POST /users/` returns 403. The local DB is SQLite (`database.db`). `database.py` turns on WAL, `foreign_keys` and `busy_timeout` pragmas on every connection. Alembic takes its URL from `Settings`, not from `alembic.ini`, and autogenerates from `models.table_registry.metadata`.

## Architecture

The code is layered under `src/ciclo_estudos/`. Each feature (subjects, users, auth, study_sessions, cycles) has a file in each layer:

- **routers/**: HTTP only. They receive services through the `*ServiceDep` aliases and catch `DomainError` subclasses (`exceptions.py`), which they turn into `HTTPException`s. Protected endpoints take `current_user: CurrentUser`.
- **services/**: business rules. Constructors take repositories (and sometimes other services). Services raise domain exceptions and never raise HTTP errors.
- **repositories/**: SQLAlchemy queries. Each repo wraps one `Session`, and `add`/`save`/`delete` commit right away.
- **dependencies.py**: the composition root that wires `Session → Repository → Service` for FastAPI `Depends`. Add a new feature's factory and `Annotated` alias here.
- **models.py**: ORM models declared with `@mapped_as_dataclass` on a shared `table_registry`, so `init=False` fields such as `id` and timestamps can't be passed to the constructor.
- **domain.py**: plain dataclasses (`CycleProgress`, `SubjectProgress`) that compute progress, percentages and completion. The progress response schemas are built from these via `from_attributes`.
- **schemas.py**: Pydantic I/O models. A response schema that exposes datetimes should subclass `UTCModel`, which tags naive DB datetimes as UTC.
- **security.py**: JWT (PyJWT) and argon2 hashing (pwdlib). The token `sub` is the user's **email**, and `/auth/token` uses the OAuth2 password form with the email in the `username` field.

Cycle semantics: at most one cycle is open (`finished_at IS NULL`). `CycleService.get_or_create_open()` lazily creates cycle 1 or the next one, and both registering a study session and reading progress go through it. Subjects are global: every cycle's progress includes all subjects.

## Testing

`tests/conftest.py` builds a fresh in-memory SQLite engine for each test (StaticPool, same pragmas) and overrides `get_session` on the app. Fixtures: `session`, `client`, `user` (exposes `user.clean_password`), `token`, `subject`, and `mock_db_time` (a context manager that pins `created_at`/`updated_at` on insert). Service-level tests (e.g. `test_subject_service.py`) use hand-written fake repositories, not the DB.

## Conventions

- Ruff: line length 79, single quotes, preview rules enabled, lint sets `I, F, E, W, PL, PT`. `migrations/` is excluded.
- Use `HTTPStatus` for status codes.
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `chore:`).
- User-facing seed data and messages are in Portuguese, and code identifiers are in English.
