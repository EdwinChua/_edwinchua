---
name: ce2m-wp8-deployment-topology
description: ce2m wp8 deployed at 172.20.77.31:8080 behind nginx Basic auth; Menlo proxy blocks browser access; team deploys from monorepo subtree; API base must stay relative /_
metadata: 
  node_type: memory
  type: project
  originSessionId: 3014fb7a-0d8e-4b14-a5f0-c8d8bd292f6c
---

The ce2m wp8 app (repos\ce2m-workspace) is deployed at http://172.20.77.31:8080 behind **host nginx (1.18.0 Ubuntu) with HTTP Basic auth** (realm "WP8 Application"). The Menlo corporate proxy returns 503 for that IP:port, so Chrome/Claude-in-Chrome can't reach it — debug it with `curl --noproxy "*"` instead. Credentials are not in either repo; I must not authenticate (prohibited) — the user has to log in / fetch authed pages himself.

The deploying team builds from the **monorepo** `repos\ce2m-netzero-monorepo\projects\sg-times-model\subtree-sgtimes-automation\wp8` — an older copy of ce2m-workspace's wp8 (backend port 8000, no .env files, Dockerfile without the build ARG). Fixes land in ce2m-workspace and must be propagated to that subtree or they won't reach production.

Fixed 2026-07-15 (commit e5b525b): all frontend API calls go through `lib/api-base.ts` (`NEXT_PUBLIC_API_BASE_URL || "/_"` — relative, since the FastAPI backend serves the static export and mounts APIs under `/_/`). Gotchas that caused the original "deployed app calls localhost" bug: NEXT_PUBLIC_* is inlined at **build** time (runtime env in compose does nothing); a Dockerfile `ENV` default overrides `.env.production`; one-arg `new URL()` throws on a relative base; the committed `Frontend/out/` is itself a deploy artifact (docker-compose.prebuilt.yml + any host nginx serve it directly, so it must be rebuilt and recommitted after base-URL changes, and the fronting nginx needs a `location /_/` proxy to the backend — see `wp8/nginx/default.conf`).

**Why:** these constraints are invisible from any single file and span two repos plus the server.
**How to apply:** when touching wp8 API URLs/deployment, keep the base relative, rebuild+recommit `out/`, remind the user to sync the monorepo subtree; related: [[menlo-proxy-tls-python-ca-bundle]].
