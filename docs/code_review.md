# Code Review: ciclo-estudos

**Date:** 2026-10-08
**Scope:** whole repository at commit `3c6c4c9` (`src/`, `tests/`, `migrations/`, `scripts/`, config files)

## Summary

The codebase is small, clean and well layered: routers → services → repositories, wired in `dependencies.py`. Services raise domain exceptions, routers map them to HTTP errors, and the progress maths is kept in `domain.py`. Lint and format checks are clean, all 31 tests pass, and line coverage is 97%.

I found **two confirmed bugs** that should be fixed first: a closed cycle records the wrong `finished_at` time, and deleting a subject that has study sessions crashes with a 500. Most other findings are about robustness and data integrity: uniqueness and "one open cycle" are checked only in Python, and the database does not enforce them. There are also some smaller hygiene items.

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| 1 | High | `advance()` stores `finished_at` in local time, but the API labels it UTC | Confirmed |
| 2 | High | Deleting a subject that has study sessions returns 500 | Confirmed |
| 3 | Medium | All data is global, so any registered user can edit or delete everything | By design, risky |
| 4 | Medium | Uniqueness and the single open cycle are not enforced in the DB, so races cause 500s | Plausible |
| 5 | Medium | CORS origin `https://127.0.0.1:5173` is probably a typo for `http` | Plausible |
| 6 | Medium | Login email match is case-sensitive | Confirmed |
| 7 | Low | `GET /cycles/current` writes to the DB | Confirmed |
| 8 | Low | `Settings()` is instantiated in four places, with no shared dependency | — |
| 9 | Low | `get_current_user` skips the repository layer | — |
| 10 | Low | Hard-coded `limit=1000` in cycle progress | — |
| 11 | Low | SQLite pragmas run on any database backend | — |
| 12 | Low | Migration hygiene issues | — |
| 13 | Low | Test gaps | — |
| 14 | Low | Repository hygiene (gitignore, README, typos, metadata) | — |

---

## High

### 1. Cycle `finished_at` is stored in local time and served as UTC

`src/ciclo_estudos/services/cycles.py:53`

```python
current.finished_at = datetime.now()
```

`started_at` and `studied_at` come from SQLite `CURRENT_TIMESTAMP`, which is **UTC**. `finished_at` comes from Python's naive `datetime.now()`, which is **server local time**. `UTCModel` then labels both as UTC (`Z`).

**Reproduced** with `TZ=America/Sao_Paulo`:

```
started_at  2026-10-08T12:13:38Z
finished_at 2026-10-08T09:13:38.096055Z   ← 3 h *before* the cycle started
```

The frontend will show wrong cycle durations, and any "cycles finished between X and Y" query will be off by the UTC offset.

**Action:**
- Use `datetime.now(UTC).replace(tzinfo=None)` to stay consistent with the naive-UTC convention, or set it on the DB side with `func.now()`, e.g. `current.finished_at = func.now()` followed by the refresh that `save()` already does.
- Add a test that runs `advance()` and asserts `finished_at >= started_at`. The test suite should also run under a non-UTC `TZ` so this kind of bug is caught.
- Longer term, consider `DateTime(timezone=True)` columns, or keep one helper (`utcnow()`) that is the only allowed source of "now".

### 2. Deleting a subject that has study sessions causes a 500

`src/ciclo_estudos/services/subjects.py:38-39`, `src/ciclo_estudos/repositories/subjects.py:40-42`

`PRAGMA foreign_keys=ON` (database.py) is correct. But `study_sessions.subject_id` has no `ondelete` rule, and nothing catches the `IntegrityError`. **Reproduced:** create a session for a subject, then `DELETE /subjects/{id}`, and you get an unhandled `sqlalchemy.exc.IntegrityError` (500).

**Action:** decide what the domain should do, then implement it:
- **Block** (recommended, since it keeps history): add a check `if self.study_sessions.exists_for_subject(id): raise SubjectInUseError` and map it to `409 Conflict` in the router.
- **Cascade**: `ForeignKey('subjects.id', ondelete='CASCADE')` plus a migration. This silently erases study history.
- **Soft delete**: add an `archived_at` column and filter archived subjects out of `list()` and progress.

Add a router test for the chosen behaviour.

---

## Medium

### 3. No per-user data ownership

Subjects, cycles and study sessions have no `user_id`. Every authenticated user sees and changes the same data. This is safe today only because `ALLOW_REGISTRATION=false` by default. As soon as registration is opened (`routers/users.py:15`), any new account can delete or rename all subjects and advance the cycle.

**Action:** if the app stays single-user, document that and consider removing public registration completely (the seed script already creates the user). If more users are expected, add `user_id` foreign keys to `subjects` and `cycles` and scope every repository query by `current_user.id`. Make `number` unique per user, not globally.

### 4. Integrity rules are only checked in Python

- `SubjectService.create/update` and `UserService.create` check-then-insert. Two concurrent requests both pass the check, and the second hits the `UNIQUE` constraint, an unhandled `IntegrityError` (500).
- `CycleService.get_or_create_open()` (`services/cycles.py:21`) can create two cycles with the same number if two requests race. It is also invoked implicitly by `GET /cycles/current` and `POST /sessions/`. Nothing in the DB enforces "only one cycle has `finished_at IS NULL`".
- `advance()` does two separate commits (close current, then add next). If the second commit fails, no cycle is open, but `get_or_create_open` would recover the next time it runs.

The risk is low for a single user, since FastAPI runs sync endpoints in a thread pool and a double-click is enough.

**Action:**
- Catch `IntegrityError` in the repositories' `add`/`save`, roll back, and re-raise the matching domain error (`SubjectAlreadyExistsError`, etc.).
- Add a partial unique index: `CREATE UNIQUE INDEX one_open_cycle ON cycles((1)) WHERE finished_at IS NULL` (works in SQLite and Postgres).
- Make `advance()` a single unit of work: flush both changes, then commit once (move `commit()` out of the repositories, or add a non-committing variant).

### 5. Suspicious CORS origin

`src/ciclo_estudos/app.py:17`: `'https://127.0.0.1:5173'`. Vite's dev server serves plain `http` unless TLS is set up, so requests from `http://127.0.0.1:5173` are currently blocked.

**Action:** change it to `http://127.0.0.1:5173`. Better, move the origins into `Settings` (e.g. `CORS_ORIGINS: list[str]`) so production URLs don't need a code change.

### 6. Login is case-sensitive on email

**Reproduced:** `TESTE@TEST.COM` with the right password returns 401. Users who type their email with different capitalisation get locked out.

**Action:** normalise emails (`.strip().lower()`) when creating a user and when logging in, or compare with `func.lower(User.email)`. Normalise `username` too if it should be case-insensitive.

---

## Low

### 7. `GET /cycles/current` writes to the database

`routers/cycles.py:11` calls `get_progress()`, which calls `get_or_create_open()`, so a GET can create cycle 1. That is surprising for a safe HTTP method, and it widens the race in #4. `GET /sessions/` behaves the same way.

**Action:** acceptable as a pragmatic choice, but consider creating the first cycle explicitly (in the seed script or on first `POST /sessions/`). For read paths, return an empty progress when no cycle is open.

### 8. Settings are loaded repeatedly and can't be overridden in tests

`Settings()` is built in `database.py:6`, `security.py:20` (module level), `routers/users.py:15` (on **every request**, which re-reads `.env`), and `migrations/env.py:13`.

**Action:** add `@lru_cache def get_settings() -> Settings` and inject it with `Depends(get_settings)` where request-scoped access is needed. Tests can then use `app.dependency_overrides[get_settings]` instead of patching environment variables.

### 9. `get_current_user` bypasses the layering

`security.py:68` queries `select(User)` directly, while everything else goes through `UserRepository`.

**Action:** use `UserRepository(session).get_by_email(...)`. Also, `except DecodeError` (line 63) is redundant because `DecodeError` is a subclass of `PyJWTError`, which is caught right after. Keep only the `PyJWTError` branch.

### 10. Hidden cap on subjects in progress

`services/cycles.py:41`: `self.subjects.list(limit=1000)`. If there are more subjects, progress is silently wrong.

**Action:** add a `SubjectRepository.all()` with no pagination, or use a single aggregate query that LEFT JOINs subjects to the session sums for the cycle. That also replaces the two queries with one.

### 11. SQLite-only pragmas on the global engine

`database.py:9-15` runs `PRAGMA ...` on every connection whatever `DATABASE_URL` points to. Moving to Postgres would fail at connect time.

**Action:** register the listener only when `engine.dialect.name == 'sqlite'`. Also, `get_session` is a generator but is annotated `-> Session`. Use `-> Iterator[Session]`.

### 12. Migration hygiene

- `9d2da67f433e_add_cycles_and_study_sessions.py` has the same message as `8804832e8807` but actually **drops `subjects.completed_hours`**. The name is misleading.
- Its `downgrade()` re-adds `completed_hours` as `nullable=False` with no `server_default`, which fails on any non-empty `subjects` table.
- Migrations are not tested.

**Action:** fix the downgrade (`server_default='0'`) and the docstring/message. You can't rename an applied revision ID, but the docstring can be corrected. Add a test that runs `alembic upgrade head` then `alembic downgrade base` on a temp SQLite file, or at least a check that `alembic check` reports no drift from the models.

### 13. Test gaps

The suite is good (97% lines, random order, fakes for service tests). Uncovered or missing behaviour:

- Bugs #1 and #2 above: there is no test for `finished_at`, and none for deleting a subject that has sessions.
- `routers/auth.py:24-25` and `services/auth.py:14`: login with a wrong password or unknown email.
- `routers/users.py:21-22`: duplicate user returns 409.
- `routers/subjects.py:60, 78-79`: update and delete of a missing subject return 404.
- `security.py:61, 71`: token without `sub`, and token for a user that was deleted.
- `domain.py:30, 70`: the `target_minutes == 0` branches. These are unreachable through the API because `target_hours` has `gt=0`; either test them directly or remove them.
- The test env relies on a real `.env` being present because of the import-time `Settings()`. Set the test values in `conftest.py` (or with `pytest-env`) so a fresh clone can run tests.

### 14. Repository hygiene

- `.gitignore` covers `database.db`, but not the SQLite WAL side files. `database.db-shm` and `database.db-wal` currently show as untracked. Add `database.db*`.
- `.env.example` has empty values. Add safe examples (`DATABASE_URL=sqlite:///database.db`, `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=30`) and a note to generate `SECRET_KEY` with `python -c "import secrets; print(secrets.token_hex(32))"`.
- `README.md` is empty, and `pyproject.toml` still has `description = "Add your description here"`.
- `uv run typos` fails on Portuguese text (`scripts/seed.py:68` "Disciplinas"). Add a `[tool.typos.default.extend-words]` allow-list or exclude `scripts/`. If spell checking is meant to be enforced, add typos to the `poe test`/lint sequence.

---

## Suggested order of work

1. Fix #1 (`finished_at`) and #2 (subject deletion) with regression tests.
2. Fix the CORS origin (#5) and email normalisation (#6). Both are one-line fixes.
3. Map `IntegrityError` to domain errors and add the one-open-cycle index (#4).
4. Decide on single-user vs multi-user (#3) before adding more features, since it changes every query.
5. Clean up settings injection, the layering in `security.py`, and the hygiene items (#8–#14).

## What's working well

- Clear separation of layers. Services can be tested with simple fakes (`test_subject_service.py`), which is a sign the boundaries are right.
- Domain errors are kept apart from HTTP errors.
- `domain.py` keeps the progress maths pure and easy to test.
- `UTCModel` handles naive datetimes in one place.
- The test setup is solid: a fresh in-memory DB per test, the production pragmas applied in tests, random ordering, and coverage tracked per test.
- Registration is closed by default.
