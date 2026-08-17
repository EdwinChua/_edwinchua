---
name: menlo-breaks-nextjs-server-actions
description: The corporate Menlo SafeView proxy reclassifies Next.js Server Action responses (text/x-component) as file downloads and replaces them with an HTML interstitial — silently corrupting data for A*STAR users only
metadata: 
  node_type: memory
  type: reference
  originSessionId: c0ba31f2-00c9-4a90-92e7-0fca41bcfec5
  modified: 2026-08-17T03:43:08.407Z
---

The A*STAR **Menlo SafeView** proxy intercepts **Next.js React Server Action**
responses. Server Actions reply with `Content-Type: text/x-component`; Menlo
reclassifies that as a FILE DOWNLOAD and substitutes an HTML interstitial page
(title "File Download", `Name: <route segment>`, "Error Occurred"). The client then
cannot deserialize the response.

**It is INTERMITTENT and content-dependent.** Confirmed on the Identity Portal
2026-08-17: the same call passed with a 4-item payload and was intercepted with a
3-item payload. So "it worked when I tried it" proves nothing.

**Why it is so hard to diagnose:**
- Only affects users behind Menlo (A*STAR staff). External users are fine, so it never
  looks like an outage.
- Code that does `const x = await action(); return data?.field ?? []` turns the
  corrupted response into a silent empty result — no throw, no banner, no browser
  console error. The UI just renders wrong.
- The server action's own `console.error` goes to the **Next server container's
  stdout**, NOT the browser console — so "no console errors" does not rule it out.
- Survives app version reverts and container restarts (it is infrastructure, not code),
  and behaves exactly like a stale cache, so it misdirects onto caching hypotheses.

**The fix, already established in the identity portal repo** (`advise_lca_platform_with_admin`):
route data through plain JSON route handlers instead of Server Actions. Canonical
pattern, whose docstrings state the Menlo rationale explicitly:
`apps/webUI/src/lib/orgAdmin/{data,client,respond}.ts` + `apps/webUI/src/app/api/org-admin/*/route.ts`.
`application/json` passes the proxy; `text/x-component` does not. The **org-admin**
surface was migrated; the **superadmin** surface was not (still exposed as of 2026-08-17).

Note the trade: Server Actions carry built-in CSRF/Origin verification that plain route
handlers do not — mitigate deliberately when migrating.

Open question: soft-navigation RSC payloads are also `text/x-component`, so route
handlers may be only a partial fix. Not yet confirmed.

Related: [[menlo-proxy-tls-python-ca-bundle]], [[ce2m-wp8-deployment-topology]] (Menlo
also blocks that browser path; use `curl --noproxy`).
