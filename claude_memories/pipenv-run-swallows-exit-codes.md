---
name: pipenv-run-swallows-exit-codes
description: pipenv run can return 0 even when the child fails; in CI call the venv python directly
metadata: 
  node_type: memory
  type: reference
  originSessionId: 29e57a39-702b-45da-9e7f-2a1ecf290331
---

`pipenv run <cmd>` can swallow the child's exit code and return **0 even when the child fails** — observed with pipenv 2025.0.4 on Windows git-bash: `pipenv run python -c "import sys; sys.exit(7)"` → exit 0, and `pipenv run pytest` → exit 0 even with test errors/failures. A CI step using `pipenv run pytest` is therefore a **silently-green gate** that passes on a red suite.

**Why:** the `pipenv run` shim doesn't reliably propagate the subprocess return code (at least this version/platform). Couldn't confirm on Linux, so treat it as unsafe everywhere.

**How to apply:** in CI/scripts that must fail on a non-zero child, bypass `pipenv run` — resolve the venv and call its python directly:
`VENV="$(pipenv --venv)"; "$VENV/bin/python" -m pytest` (Linux) / `"$VENV/Scripts/python.exe"` (Windows). Verified the direct venv python DOES propagate (sys.exit(7)→7; pytest errors→1; clean run→0). Used in `advise_lca_platform/.github/workflows/backend-test.yml` + `backend-test-db.yml`. Related: [[advise-repos-pr-test-ci]].
