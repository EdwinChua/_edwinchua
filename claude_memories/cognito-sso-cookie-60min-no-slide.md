---
name: cognito-sso-cookie-60min-no-slide
description: "Cognito managed-login SSO cookie is a FIXED 60 min from interactive login and does not slide on silent authorize, so prompt=none has a 60-minute shelf life"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8c6f8e04-62f2-4660-8d6a-81d9b5abb39d
  modified: 2026-08-19T09:10:49.725Z
---

Measured empirically 2026-08-19 against the ADVISE **dev** pool `ap-southeast-1_vXj2lFhBz`, client `advise-platform` (`4fhjj6ea5r8bave59na3velrvt`), with a disposable probe user:

- The managed-login SSO cookie (`cognito`, on `advise-dev-vxj2lfhbz.auth.ap-southeast-1.amazoncognito.com`) is set with **Max-Age exactly 3600s from the interactive login**.
- A silent `/oauth2/authorize?prompt=none` **succeeds** while it is alive (returns a fresh `code`, no login) but **does NOT slide the expiry** — measured `delta_from_first = 0` across three consecutive silent authorizes. TTL just counts down.
- AWS docs claiming these cookies "don't expire automatically" are wrong for managed login.

**Why:** it puts a hard 60-minute shelf life on `prompt=none` as a session-liveness probe. Past that hour every check returns `login_required`, which is **indistinguishable from "the user logged out"** — so a revalidation-only design either forces an interactive login every hour or detects nothing after the first hour. It is also why the eTEA silent-SSO bridge only gives click-free cross-over within an hour of interactive sign-in.

**How to apply:** never treat `prompt=none` → `login_required` as proof of logout. Any cross-app logout propagation needs a durable signal that outlives the SSO cookie (a shared logout epoch, or server-side per-`sub` invalidation), with `prompt=none` only as a corroborator inside the hour. See [[etea-portal-cross-app-logout-facts]] for the companion revocation findings.

Prod client `s3q5mibf5ngudpdihg2nc97pi` has identical token-validity settings; the cookie lifetime itself is unverified on prod.
