---
name: portal-prod-pinned-v1-2-0-invite-regression
description: "The 2026-08-07 Identity Portal rollback to v1.2.0 was REVERTED on 2026-08-17; both envs are back on v1.3.0, the prod IMAGE_TAG pin is removed, and the \"v1.3.0 broke invites\" verdict is retracted"
metadata: 
  node_type: memory
  type: project
  originSessionId: c0ba31f2-00c9-4a90-92e7-0fca41bcfec5
  modified: 2026-08-17T03:43:30.757Z
---

**RESOLVED / RETRACTED — read this before acting on the old conclusion.**

On 2026-08-07 the Identity Portal was rolled back to v1.2.0 because invite redemption
appeared broken (Cognito account created, no portal user). Rolling dev back seemed to
fix it, so v1.3.0 was blamed.

**That verdict is now considered UNPROVEN.** On 2026-08-17 the real cause of a sibling
bug on the same surface was identified as the Menlo SafeView proxy corrupting Next.js
Server Action responses — see [[menlo-breaks-nextjs-server-actions]]. Invite redemption
also goes through a Server Action (`createUserFromCode`), and the Menlo failure is
intermittent and content-dependent, so the v1.2.0 "fix" may simply have been a lucky
pass. **Re-test invites against the Menlo hypothesis before blaming any release.**

**Current state (2026-08-17): both envs restored to v1.3.0, verified healthy.**
- prod backend `sha256:1b33a0d6…`, frontend `sha256:e7beffd3…` (both = tag `v1.3.0`, built 2026-08-04)
- dev backend `sha256:def5dbcd…` (`b8c68570`), frontend `sha256:640d261a…` (`952bb963`)
- `migrations applied`, 0 restarts, all four endpoints 200
- ✅ **The prod `/opt/portal/.env` `IMAGE_TAG=v1.2.0` pin has been REMOVED** (backup at
  `/tmp/portal-env-pin.bak`). Prod deploys resolve to `:latest` again and will actually ship.

**Durable lessons worth keeping:**
- **dev does NOT support an IMAGE_TAG pin** — `/opt/portal/compose.yaml` on dev hardcodes
  `:latest` with no `${IMAGE_TAG}` templating (prod DOES template it). To pin dev you must
  retag `:latest` in ECR. Dev tags images by commit SHA, never by release tag; the dev
  equivalent of `v1.2.0` was `5bd045e8` (dev-side parent of the merge; identical tree).
- **A prod IMAGE_TAG pin is a landmine**: CI runs bare `docker compose pull backend && up -d`
  and never writes IMAGE_TAG, so a pin makes every release report SUCCESS while still
  running the pinned image.
- **Retagging ECR from Windows**: `aws ecr batch-get-image … --output text > file` CRLF-mangles
  the manifest, so `put-image` mints a NEW digest instead of moving the tag. Pipe through
  `tr -d '\r'` and verify with `sha256sum` before pushing.
- v1.3.0's migration `0007` is additive only (one nullable column), so v1.2.0 and v1.3.0 code
  both run fine against it. Migrations are forward-only.

See [[etea-prod-golive]], [[portal-prod-db-query-recipe]].
