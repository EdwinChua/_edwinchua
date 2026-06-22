---
name: platform-portal-enforcement-egress-chain
description: "For ADVISE dev access-control to actually enforce, three things beyond the axis flags must be true — the portal API host wired, ADMIN_PORTAL_TOKEN set, and the backend redeployed AFTER setting it"
metadata: 
  node_type: memory
  type: project
  originSessionId: e5f02ae0-afc4-421b-9c62-5a1759955f8e
---

Flipping the axis flags (`PERMISSIONS/SEATS/FEATURES/SHARING_ENABLED`) on the platform
is necessary but NOT sufficient. With flags on, the backend resolves every user's
principal by calling the **identity portal**; if that call fails it **fails closed** →
EVERY user denied → `/home` server-render 500s. Symptom in `/copilot/etea-dev-backend`
logs: `portal unavailable and no in-grace last-good for <email> — failing closed`.

For enforcement to work on dev, ALL of these must hold (each was a separate, days-apart
blocker in the 2026-06-19→22 incident):

1. **Portal API host wired.** Platform calls `ADMIN_PORTAL_BASE_URL =
   https://api.dev.identity.advise.technology/admin/api`. The portal is two App Runner
   services in **account 701518539545** (stack `advise-identity-portal-apprunner-dev`):
   FrontendService (`dev.identity…`) + BackendService (`api.dev.identity…`, Elysia,
   routes under `/admin/api`). Only the frontend domain was originally wired; the backend
   `api.` host was NXDOMAIN. Fix: `apprunner associate-custom-domain` on BackendService +
   add the validation CNAMEs + target CNAME to zone `Z03133243R95RTLGU6EOI`
   (identity.advise.technology). Backend default URL `hcqpfbveyv.ap-southeast-1.awsapprunner.com`
   is public — usable as a fallback `ADMIN_PORTAL_BASE_URL` if DNS is in the way.

2. **`ADMIN_PORTAL_TOKEN` set + valid.** Platform SSM (acct 149536453305)
   `/copilot/etea/dev/secrets/ADMIN_PORTAL_TOKEN` must exist (SecureString, `alias/aws/ssm`)
   and hold a token matching a **portal client** (clientsTable, ≥read). It's read at RUNTIME
   by the TASK role (granted by-ARN in `copilot/backend/addons/access-control-ssm-policy.yml`,
   NOT tag-conditioned — so a plain `aws ssm put-parameter` works; no `copilot secret init`
   needed). Missing/empty token → portal 401 → `PortalError` (distinct from `PortalUnavailable`,
   which is transport/timeout/5xx only — useful to tell DNS/egress vs auth apart).

3. **Redeploy the backend AFTER (1)+(2).** `config.admin_portal_token()` is `lru_cache`d and
   the `httpx` client is a module singleton that **bakes the Bearer header at creation**, so a
   long-running task NEVER picks up a newly-set token or newly-resolving host. Force a fresh
   task (`gh workflow run backend-push-ecr-dev.yaml --ref dev`, the `--force` svc deploy). The
   SSM token is read at runtime, so the task-def revision is irrelevant — just needs a new task.

Diagnostics that were clean (rule out): the dev backend runs in a PUBLIC subnet (public IP +
IGW), SG/NACL allow-all egress, AmazonProvidedDNS, only an S3 gateway VPC endpoint — so public
egress + DNS work (logins verify via Cognito over the same path). Related: the flags themselves
won't deploy on a manifest-only change unless `copilot/backend/**` is in the CI path filter
([[copilot-manifest-change-needs-path-filter]]).
