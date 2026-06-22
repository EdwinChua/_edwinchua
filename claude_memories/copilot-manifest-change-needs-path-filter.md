---
name: copilot-manifest-change-needs-path-filter
description: "dev deploy workflows are path-filtered to service code (backend/**, frontend/**); a Copilot manifest/env-only change (e.g. an access-control flag flip) merges but never deploys"
metadata: 
  node_type: memory
  type: project
  originSessionId: e5f02ae0-afc4-421b-9c62-5a1759955f8e
---

ADVISE LCA dev CI (`.github/workflows/*-push-ecr-dev.yaml`) triggers on push to `dev`
**with a `paths:` filter** scoped to the service source (`backend/**`, `frontend/**`).
A change that touches ONLY the Copilot service manifest (`copilot/<svc>/manifest.yml`)
— which is where the runtime env lives, incl. the access-control axis flags
(`PERMISSIONS/SEATS/FEATURES/SHARING_ENABLED`) — merges to `dev` but does **NOT**
trigger a deploy. The running ECS task keeps the old env; the change is silently inert.

**Hit 2026-06-19:** PR #218 flipped the dev flags in `copilot/backend/manifest.yml`,
merged to `dev`, but the backend never redeployed (task def stayed on `:16` from #214).
Enforcement looked "on" in git but was OFF on the live container — a logged-in user with
no seats/rights could do everything. Fixed by `gh workflow run backend-push-ecr-dev.yaml
--ref dev` (→ task def `:17` with the flags; verified `/me` no-token now 401) AND adding
`copilot/backend/**` to that workflow's `paths:` filter (commit 847b0217f on `dev`).

**How to apply:** after ANY Copilot manifest/env change, confirm a deploy actually ran —
check `gh run list --workflow=<svc>-push-ecr-dev.yaml` and the live ECS task def's env
(`aws ecs describe-task-definition`), don't trust the merge. `frontend-push-ecr-dev.yaml`
likely still has the same gap (only `copilot/backend/**` was fixed). Prod workflows are
`workflow_dispatch` (no path filter) so they're unaffected. Related deploy-topology
landmine: [[prod-deploy-from-main-reverts-etea-rename]].
