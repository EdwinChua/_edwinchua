---
name: advise-repos-pr-test-ci
description: PR test CI wired for both advise repos — what runs on pull_request and the no-DB/DB split
metadata: 
  node_type: memory
  type: project
  originSessionId: 29e57a39-702b-45da-9e7f-2a1ecf290331
---

Wired GitHub `pull_request` test gates (→ main/dev) for both repos on 2026-06-25.

**advise_lca_platform_with_admin** (Turborepo): `.github/workflows/ci.yml` runs `npx turbo run check-types` (server+webUI), `lint` (webUI; added a `lint` task to turbo.json), and `test` (apps/server `bun test`, in-memory pglite — 189 pass, no DB/secrets). Needs setup-node@22 + setup-bun.

**advise_lca_platform** (multi-service):
- `backend-test.yml` — Python pytest. Runs the FULL suite but **DB-backed tests auto-skip** when no Postgres is reachable (the `db_session` fixture in `app/tests/conftest.py` AND the self-connecting `http_app` fixture in `test_auth_shares_http.py` now `pytest.skip` on connection failure; `REQUIRE_DB=1` turns skip → hard error). No-DB run = 109 passed / 142 skipped / 0 errors. The ~14 DB/auth tests self-seed (need schema, not seed data); ~10 no-DB tests gate the PR.
- `backend-test-db.yml` — follow-up, **workflow_dispatch only**, needs one validation run before gating. Stands up postgres:16, builds schema via `CREATE SCHEMA lca` + `Base.metadata.create_all` (migrations are additive-on-top-of-create_all, so create_all is the generator; raw-SQL CHECKs/partial-indexes not reproduced — fine for the app-logic auth tests). Promote by swapping `on:` to pull_request.
- `ensure-build.yml` (was frontend build-only) — added `npm run lint` + `npm test` (Jest, 49 pass); build still covers types.

**Gotchas:** never use `pipenv run pytest` in CI — it swallows the exit code → silently-green gate; call `$(pipenv --venv)/bin/python -m pytest` directly ([[pipenv-run-swallows-exit-codes]]). pact_api + csv_exporter tests are NOT wired (placeholder scripts / need a live server — would be new test work). Not yet committed as of 2026-06-25.
