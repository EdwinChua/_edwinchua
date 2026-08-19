---
name: etea-portal-cross-app-logout-facts
description: "Measured Cognito facts behind the eTEA/portal cross-app logout bug — /logout does not revoke refresh tokens, revocation is per-lineage, auth_time differs per app"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8c6f8e04-62f2-4660-8d6a-81d9b5abb39d
  modified: 2026-08-19T09:11:12.066Z
---

Measured 2026-08-19 on the ADVISE **dev** pool `ap-southeast-1_vXj2lFhBz` with a disposable probe user, driving the real hosted-UI code flow. eTEA and the Identity Portal share ONE app client per env (dev `4fhjj6ea5r8bave59na3velrvt`, prod `s3q5mibf5ngudpdihg2nc97pi`; ID/access 60 min, refresh 5 days).

- **Hosted-UI `/logout` does NOT revoke refresh tokens.** It clears the `cognito` SSO cookie (a following `prompt=none` returns `login_required`) but both apps' refresh tokens kept minting fresh id-tokens afterwards. So a sibling logout leaves a ghost session for the full **5-day** refresh-token life, not ≤60 min.
- **`/oauth2/revoke` is per-refresh-token-lineage.** Revoking app A's refresh token → A returns `invalid_grant`, app B's token still works. Two apps do separate code exchanges, so revoking on logout can never reach the sibling.
- **`auth_time` DIFFERS between the two apps' exchanges from the same SSO session** (measured 1787130315 vs 1787130378) — it is per code exchange, not per SSO session. `origin_jti` differs too. Neither can be used as a cross-app session identifier or freshness basis.
- Silent cross-app SSO genuinely works: a second `/oauth2/authorize` on the same SSO cookie returns a code with no login — and yields an independent second refresh token.
- Revoke call shape: `POST /oauth2/revoke` with HTTP Basic client auth and body `token=<rt>` only. Adding `client_id` to the body alongside Basic auth returns `invalid_request`.

**Why:** these four facts kill the intuitive fixes. Revoking on logout, chaining logout, or binding on `auth_time`/`origin_jti` all fail for reasons that are invisible until measured.

**How to apply:** design cross-app logout around a durable signal (shared logout epoch on `.advise.technology`, or server-side per-`sub` invalidation), not around token revocation. Pair with [[cognito-sso-cookie-60min-no-slide]], which bounds `prompt=none` to a 60-minute shelf life. Hosted UI is Managed Login v2: default first factor is **email OTP**, with password reachable at `/verifyPassword` (`alternativeAuthFlows: USER_PASSWORD_AUTH`).
