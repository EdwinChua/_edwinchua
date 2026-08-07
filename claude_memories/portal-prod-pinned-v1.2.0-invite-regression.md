---
name: portal-prod-pinned-v1-2-0-invite-regression
description: Identity Portal dev+prod rolled back to v1.2.0 on 2026-08-07 because v1.3.0 broke invite redemption; prod carries an IMAGE_TAG pin that MUST be removed before the next release
metadata: 
  node_type: memory
  type: project
  originSessionId: a25acda2-9db1-4912-bc73-1bad56efbc48
  modified: 2026-08-07T09:47:22.779Z
---

Identity Portal **v1.3.0 broke invite redemption** — the invitee's Cognito account got
created but no portal user row. Confirmed empirically on 2026-08-07: after rolling dev
back to v1.2.0, invite redemption worked again. Both envs are now on v1.2.0.

Ruled out as the cause (all present since v1.0.0, so v1.2.0 has them too): the
`x-id-token` requirement on `/invitation_tokens/use`, and the fail-closed seat gate.
The v1.3.0-only delta in the redemption path is the **feature-grant block** in
`createUserFromInviteCode` — it runs only when the invite payload carries features.
Root cause still unconfirmed; that block is where to look.

**Rollback levers differ per env — dev does NOT support IMAGE_TAG:**
- **prod** `compose.yaml` templates `${IMAGE_TAG:-latest}` → pinned via
  `/opt/portal/.env` containing `IMAGE_TAG=v1.2.0`. Prod ECR carries real `v1.2.0` tags.
- **dev** `compose.yaml` **hardcodes `:latest`** — an IMAGE_TAG pin is a silent no-op.
  Reverted instead by moving the `:latest` tag in both dev ECR repos to the v1.2.0
  images. Dev tags by commit SHA, not release tag: the dev equivalent of `v1.2.0` is
  `5bd045e8b1cd7c211be311174924aaab808c15c3` (the dev-side parent of the v1.2.0 merge;
  `git diff 5bd045e8 v1.2.0` is empty). Self-healing — the next push to `dev` restores
  forward motion.

⚠️ **The prod pin makes every future release a silently-green no-op.** CI runs bare
`docker compose pull backend && up -d backend` and never writes IMAGE_TAG, so while
`/opt/portal/.env` exists prod keeps running v1.2.0 while the job reports SUCCESS.
**`rm /opt/portal/.env` on the prod box before shipping the next release.**

Schema note: v1.3.0's migration `0007` is additive only (one nullable column,
`applications.access_catalog_endpoint`). Migrations are forward-only and v1.2.0 boots
clean against it — verified on both boxes (`migrations applied (or already up to date)`,
0 restarts). No DB rollback is needed or possible.

Retagging ECR from Windows: `aws ecr batch-get-image ... --output text > file` **CRLF-mangles
the manifest**, so `put-image` mints a NEW digest instead of moving the tag. Pipe through
`tr -d '\r'` and verify with `sha256sum` before pushing.

See [[etea-prod-golive]], [[portal-prod-db-query-recipe]], [[etea-feature-split-design]].
