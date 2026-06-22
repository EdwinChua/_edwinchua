---
name: dev-enforcement-idtoken-refresh-gap
description: "Dev access-control is live but the FE never refreshes the Cognito id-token — NextAuth's 30d session outlives the 1h id-token, so any session >1h forwards an EXPIRED bearer and the backend 401s every call. Rollout S3 (refresh) must land for enforced dev to be usable."
metadata: 
  node_type: memory
  type: project
  originSessionId: 656a8dd1-af88-4c5a-a64f-765b6387ae5a
---

Confirmed 2026-06-22 by live smoke test: `GET https://api.dev.etea.advise.technology/me`
with a real session id-token → **401 `{"error":"invalid-token","reason":"token expired"}`**
even though the NextAuth session was valid (expires 30 days out).

**Root cause** (platform repo, `frontend/lca-platform-app`):
- `auth.ts` `jwt` callback captures `account.id_token` **only at sign-in**; no
  `refresh_token` capture, no rotation → `idToken` is never refreshed within a session.
- NextAuth session lifetime (default ~30d) **>>** Cognito id-token (1h, `exp = iat + 3600`).
- `middleware.ts` silent-SSO bridge (`prompt=none` → `/silent-login`, `SilentLogin.tsx`)
  fires ONLY when `!req.auth` (no NextAuth session). A still-valid 30d session means it
  never re-auths on mere id-token expiry.
- Both server-side egress paths attach the stale `session.idToken` as `Authorization:
  Bearer`: `app/services/backendCall.ts` (+ `web-calls.service.tsx` server actions) and
  `app/api/_lib/proxyBackend.ts` (the `/api/*` routes). Backend verifies `token_use=id` and
  rejects expired → 401.

**Impact:** harmless while inert, but all 4 axis flags are ON (dev, 2026-06-19), so EVERY
dev session older than ~1h gets 401 on all backend calls, with **no auto-recovery**
(middleware doesn't re-auth on a backend 401, only on a missing NextAuth session).
Enforced dev is effectively unusable past the first hour until this is fixed.

**Fix = Rollout S3 (id-token refresh):** in `auth.ts` capture `refresh_token` + `expires_at`
at sign-in; in the `jwt` callback, when near/after expiry, refresh via the Cognito token
endpoint (`grant_type=refresh_token`, client secret `AUTH_COGNITO_SECRET`), update
`idToken`+`expires_at`; on refresh failure mark an error → force re-login. **Stopgap (no
code):** set NextAuth `session.maxAge` < 1h so the existing silent bridge re-mints before
the id-token expires (costs a ~hourly silent redirect). Related: this is the FE half of
[[platform-portal-enforcement-egress-chain]] (which covered the backend-side preconditions).

**STATUS (2026-06-22): FIXED** — implemented as commit `662e78509` on
`feat/admin-portal-integration`: refresh in the NextAuth `jwt` callback via a new
`auth-refresh.ts` (resolves the Cognito token endpoint from OIDC discovery, cached;
`refresh_token` grant with HTTP Basic; no-op in the edge runtime), `next-auth.d.ts` type
augmentation (drops the old `as any`), and a `UserProvider` one-shot re-login on
`session.error === "RefreshAccessTokenError"`. Verified jest 37/37 + tsc + lint; one
adversarial critique, no blockers. **PENDING: deploy to dev (push feat→dev → frontend
deploy) + post-deploy smoke** (a >1h session should now 200, not 401). Separate follow-up
(NOT the refresh itself): also force re-login on a backend 401, not just on refresh failure —
`getMe` masks 401s as a generic load failure today (task_aad6d4a3).
