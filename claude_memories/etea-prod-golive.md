---
name: etea-prod-golive
description: etea platform prod went live 2026-07-07 (release 2026.0.3.0) with all 5 enforcement axes ON; portal-prod seeding + catalog sync now VERIFIED done, only client arming still pending; portal prod on v1.3.0
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

**✅ Portal-prod seeding VERIFIED DONE (checked against the prod DB 2026-08-05):** the
`advise_etea` application row exists with `access_catalog_fetched_at = 2026-07-14`, 4
`kind='feature'` catalog rows, and **15 `organization_features` grants** — and every one of
those 15 has a live `status='active'` catalog row (no orphans). So item 1 below is closed.
Note the portal's own per-app columns `permissions_enabled/features_enabled/seats_enabled`
are all **false** on that row — misleading, but they are NOT the enforcement switches (the
authoritative flags are env vars on the PLATFORM side, acct 149536453305), and
`features_enabled` in particular is written but never read by portal code.

**Portal prod is on `v1.3.0`** (released + verified 2026-08-04): features-on-invite on both
invite surfaces, plus a superAdmin gate on `GET /features/org` and `GET /seats/usage`.

**Still pending (portal side — acct 701518539545):**
1. Arm the prod platform client's application_id (Headline-1, token-hash match) BEFORE
   first real users [[platform-portal-enforcement-egress-chain]]. NOT verified — the
   seeding check above did not cover client arming.

**Why:** next sessions must not re-plan the deploy or assume prod is unconfigured.
**How to apply:** treat prod as LIVE + enforced; remaining work is portal-side seeding,
not platform deploys. Platform prod deploys = manual workflow_dispatch from main
(releases are bookkeeping); the PORTAL repo is the opposite — publishing a GitHub
release THERE deploys portal prod.
