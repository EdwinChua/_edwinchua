---
name: cognito-dev-pool-topology
description: advise-dev-users Cognito pool (copy of advise-prod-users); single advise-platform client per pool; local-dev login wiring for admin portal + LCA platform
metadata: 
  node_type: memory
  type: project
  originSessionId: ba6d4fe5-89ca-4206-86d5-f0adf2384f5a
---

`advise-dev-users` (`ap-southeast-1_vXj2lFhBz`) is a copy of `advise-prod-users` (`ap-southeast-1_5JLeryayS`) — both in AWS account 701518539545, region ap-southeast-1. Each pool has a single app client named `advise-platform` (different IDs: dev = `4fhjj6ea5r8bave59na3velrvt`, prod = `s3q5mibf5ngudpdihg2nc97pi`).

Local dev for BOTH the admin portal (`advise_lca_platform_with_admin`, FE :4300) and the LCA platform (`advise_lca_platform`, FE :3000) authenticates against the dev pool's `advise-platform` client. Its callbacks: `https://dev.etea.leaf.advise.technology/api/auth/callback/cognito` + `http://localhost:4300/...` + `http://localhost:3000/...`. The dev pool domain `advise-dev-vxj2lfhbz` is on **Managed Login v2** with green/ADVISE branding plus a "DEV ENVIRONMENT" marker (style `b7fc01fa`); prod's `advise-platform` has the same green branding without the marker.

Four local env files point at the dev pool + this client: admin `apps/webUI/.env.development` + `apps/server/.env`, LCA `frontend/lca-platform-app/.env.development` + repo-root `.env`. (Previously these used the old green-compass `gc-dev-v2` pool `ap-southeast-1_0yAGDGzmd`.)

**Why:** user moved local dev off gc-dev-v2 onto the advise dev pool and wants dev/prod client structure to mirror (one `advise-platform` per pool; only pool/callbacks/dev-marker differ).

**How to apply:** AWS resource IDs/branding can change — verify with `aws cognito-idp list-user-pool-clients --user-pool-id ap-southeast-1_vXj2lFhBz` before relying. The production pool (`advise-prod-users`) was never modified. The LCA backend enforces Cognito ID-token verification (SHARING_ENABLED + PERMISSIONS_ENABLED on), so FE pool/client must match BE `COGNITO_*`, and login users must exist (email_verified) in the pool AND in local portal `admin` / `leaf-dev` DBs.
