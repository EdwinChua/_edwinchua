---
name: etea-prod-golive
description: etea platform prod went live 2026-07-07 (release 2026.0.3.0) with all 5 enforcement axes ON; portal-prod seeding/catalog-sync/client-arming still pending
metadata: 
  node_type: memory
  type: project
  originSessionId: fb1a271d-d8fd-4fbb-8d6d-a07cdd39bd36
---

etea LCA platform PROD go-live happened 2026-07-07: release 2026.0.3.0, main `1f914678e`,
backend now a public LBWS at api.etea.advise.technology with ALL 5 axis flags ON
(fail-closed), migrations 0001–0006 + D2b views on leaf-prod, ADMIN_PORTAL_TOKEN +
ACCESS_CATALOG_TOKEN in prod SSM (values in `/copilot/etea/prod/secrets/*`, acct
149536453305). Full state + runbook pointers live in the repo's `.claude/primer.md`
(commit `293f694bb`).

**✅ Catalog sync DONE 2026-07-07** (22 caps pulled). Gotcha that broke it twice: the sync
runs inside the portal's FRONTEND container (embedded Elysia API / server action), NOT the
backend container — refreshing portal-prod box env (SSM → sync-env.sh) must target BOTH
`sync-env.sh backend` AND `sync-env.sh frontend` + `docker compose up -d --force-recreate`
each; a stale frontend keeps 401ing with the old ACCESS_CATALOG_TOKEN. Portal-side token
lives at SSM `/apprunner/advise-identity-portal/prod/ACCESS_CATALOG_TOKEN` (now v2, equals
the platform-side value).

**Still pending (all gated, portal side — acct 701518539545):**
1. Seed portal prod: org, roles, seat pool, monte_carlo grants (users 403 until then).
2. Arm the prod platform client's application_id (Headline-1, token-hash match) BEFORE
   first real users [[platform-portal-enforcement-egress-chain]].

**Why:** next sessions must not re-plan the deploy or assume prod is unconfigured.
**How to apply:** treat prod as LIVE + enforced; remaining work is portal-side seeding,
not platform deploys. Platform prod deploys = manual workflow_dispatch from main
(releases are bookkeeping); the PORTAL repo is the opposite — publishing a GitHub
release THERE deploys portal prod.
