---
name: prod-deploy-from-main-reverts-etea-rename
description: "prod Copilot deploys build from main, but the etea domain-rename manifests live only on feat/admin-portal-integration — deploying any prod service from main reverts the domain"
metadata: 
  node_type: memory
  type: project
  originSessionId: f73dcfdc-7336-4f20-ad2a-5fe162d61a7f
---

The ADVISE LCA prod Copilot deploy workflows (`frontend-push-ecr-prod.yaml`,
`backend-push-ecr-prod.yaml`) are manual `workflow_dispatch` and **check out
`ref: main`**. The etea domain rename (`*.leaf.advise.technology` →
`*.etea.advise.technology`) was cut over live via env deploy + operator DNS/CF +
the feat-branch manifests, but those rename manifests were **never merged to
`main`** — they live only on `feat/admin-portal-integration`.

**Consequence (hit 2026-06-19):** dispatching the prod frontend deploy (release
2026.0.2.2) from `main` re-rendered the frontend service's ALB host rules +
`AUTH_URL` to the stale pre-rename config (`alias: etea.leaf.advise.technology`),
taking the canonical `etea.advise.technology` **offline (TLS handshake failure)`**
while only `etea.leaf` served. Fixed by 2026.0.2.3: bring the reviewed
`copilot/frontend/manifest.yml` rename onto `main` (prod `alias` lists BOTH the new
canonical host and `etea.leaf` for the 308 redirect; AUTH/IMG/SITE URLs on the new
domain) → push to main → re-dispatch → all three hosts verified 200. A frontend
`svc deploy` alone restored it; no env-level cert re-work was needed.

**Why:** `main` is the prod source of truth, but it lags the live env — the rename
only ever existed on a feature branch. Any prod `svc deploy` / `env deploy` from
`main` reverts to whatever stale config main holds (this is the same class of
"Copilot-unaware operator watch-item" as [[copilot-byo-deletes-env-zone]]).

**How to apply:** before ANY prod deploy from `main`, confirm `main` actually
carries the live config. For the etea estate the full rename is now ON `main` as of
2026-06-19: `copilot/frontend/manifest.yml` (`d4baf5c98`, release 2026.0.2.3) +
`copilot/environments/prod/manifest.yml` (cdn+ALB BYO certs) +
`copilot/img-proxy/manifest.yml` + `copilot/environments/addons/leaf-image.yml`
(`d3284efc4`). So a routine prod **frontend svc deploy** from main is now safe.
STILL operator-gated: a prod `copilot env deploy` with the cdn-BYO certs is the
operation that previously DELETED the env Route53 subzone ([[copilot-byo-deletes-env-zone]]) —
follow the runbook watch-items (recreate A-ALIASes, re-attach the CloudFront 308
redirect Function) before/after running it.
