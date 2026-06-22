---
name: nextjs-server-action-skew-apprunner
description: "Next.js Server Actions break (\"Failed to find Server Action\" → undefined) across multi-instance/rolling deploys unless the signing key is pinned"
metadata: 
  node_type: memory
  type: project
  originSessionId: ba6d4fe5-89ca-4206-86d5-f0adf2384f5a
---

On a multi-instance or rolling Next.js (App Runner / ECS / k8s) deploy, server actions can fail
intermittently with server-side log `Error: Failed to find Server Action "<id>". This request might
be from an older or newer deployment.` The client `await someAction()` then **resolves to `undefined`
(it does NOT throw)** — so `const {x} = (await action()) ?? {}` yields all-undefined, and consumers
silently mis-behave (e.g. empty lists, "unable to get roles", a blank fallback screen).

ROOT CAUSE: Next.js derives each server action's ID using a signing key. If
`NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` is **not pinned**, every `next build` bakes a *random* key →
different action IDs per build. With ≥2 instances live on **different builds** (the rolling-deploy
drain window, or autoscale-up onto a stale image), the browser fetches JS from build A but the action
POST is load-balanced to build B → B doesn't know that ID → fails. A fresh/incognito tab does NOT fix
it (GET and POST can still hit different instances). It surfaces on whichever action's source changed
most recently (its ID shifted between the two live builds) but ALL actions are vulnerable.

FIX (both, belt-and-suspenders, used on the dev Identity Portal 2026-06-18):
1. PIN the key so IDs are identical across builds: generate `python -c "import secrets;
   print(secrets.token_hex(32))"`, store in SSM SecureString, and make it present **at BUILD time**
   (it's baked then) — pass as a Docker `--build-arg` from a GitHub Actions secret, `ARG`+`ENV` it
   before `next build`. Also wire it as a runtime secret (App Runner RuntimeEnvironmentSecrets + IAM).
2. SINGLE-INSTANCE the Next.js service (App Runner Min1/Max1) so two builds are never live at once.
3. RESILIENCE: never let a non-critical server-action failure (e.g. a roles/permissions overlay) null
   the session/user and blank the whole app — degrade gracefully. Add real `error.tsx`/`global-error.tsx`.

GOTCHA: `tsc --noEmit` does NOT catch what `next build` rejects — `next build` runs ESLint and fails on
`@typescript-eslint/no-unused-vars` (e.g. an unused `error` prop in `error.tsx`/`global-error.tsx`).
Run `npx next lint` before pushing. Relates to [[copilot-secret-must-use-secret-init]].
