---
name: invite-signup-cognito-idtoken-hardening
description: "Portal invite-signup: hCaptcha removed + /invitation_tokens/use now requires a verified Cognito ID token (x-id-token) and derives the email server-side. Merged to dev (637e30f9), UNPUSHED. Deploy gotcha: requires email_verified=true."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8fbdec7a-9043-477b-9d65-1872fd99f2c5
---

The ADVISE Identity Portal invite-signup flow (`advise_lca_platform_with_admin`) was reworked 2026-06-24, **merged to `dev` as merge `637e30f9`, NOT pushed** (held at the user's request; dev was ahead of origin by 7):

- **hCaptcha removed** entirely (widget + `@hcaptcha/*` deps + `HCAPTCHA_*` env in `.env.development`/`.env.production`/`bootstrap.sh` + the orphaned `auth/utils.ts` `getClientIp`). Why: it broke on deployed dev (a real, domain-restricted sitekey baked from `.env.production` vs the always-pass test key in `.env.development` that `next dev` uses — deployed `next build` reads `.env.production`), the owning hCaptcha account was orphaned (the dev left), and it was redundant (signup already requires Cognito SSO + an unguessable, expiring, max-use invite code).
- **Hardened both tiers** so the new account binds to the SSO-verified identity, never client input: webUI `createUserFromCode(code)` forwards `session.idToken` as `x-id-token`; the backend **`POST /admin/api/invitation_tokens/use`** now requires `x-id-token`, verifies it via `verifyCognitoIdToken` (the issue-#15 verifier in `src/middleware/userValidation/cognito.ts`), and derives the email from the **verified** claim (body is just `{code}`; the trusted `email` body field is removed). Verification is **unconditional** (NOT gated by `ADMIN_IDENTITY_ENFORCED`). The backend needs `COGNITO_REGION/USER_POOL_ID/APP_CLIENT_ID` — added to `infra/podman/bootstrap.sh` `.env.backend` (values match the webUI's `AUTH_COGNITO_*`: pool `ap-southeast-1_vXj2lFhBz`, client `4fhjj6ea5r8bave59na3velrvt`).

**DEPLOY GOTCHA — verify before pushing/deploying:** `verifyCognitoIdToken` requires **`email_verified === true`** (cognito.ts ~L126). If pool `ap-southeast-1_vXj2lFhBz` issues ID tokens with `email_verified=false` for invitees (Cognito-native admin-created users, or **A*STAR-federated** users whose IdP attribute mapping doesn't set it), every such signup **401s** — re-breaking the very flow this fixed. Check a real invitee's id-token (decode the `email_verified` claim) or the pool/IdP attribute mapping first. Fallback if needed: relax `/use` to not require `email_verified` (the email still comes from the verified token, just not Cognito-confirmed). Related: [[cognito-dev-pool-topology]], [[dev-enforcement-idtoken-refresh-gap]], [[portal-dev-ec2-docker-runtime]].
