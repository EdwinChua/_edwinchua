---
name: neurasil-vault-mcp-server
description: "neurasil = self-hosted second-brain vault (MCP connector + Notion-like web UI) replacing Notion; personal AWS 548045679450; MCP + REST + SPA all LIVE; key build/deploy facts"
metadata: 
  node_type: memory
  type: project
  originSessionId: e696b565-4e5d-4e86-ba47-b5854963dfea
  modified: 2026-08-05T15:45:37.835Z
---

**neurasil** ("neural silicon") — a self-hosted personal "second brain" (free-form markdown notes + schema-on-demand CSV tables with real SQL) reachable as a remote MCP **custom connector** from claude.ai / Desktop / Cowork. Replaces Notion, whose hosted MCP connector kept failing OAuth. Started 2026-08-05.

**Where things live**
- Repo: private `github.com/EdwinChua/neurasil` (personal identity 3dw1nchu4@gmail.com); local `C:\Users\chuache\Documents\repos\neurasil`.
- Council-amended implementation plan: `C:\Users\chuache\.claude\plans\declarative-prancing-codd.md` (the detailed source of truth for design decisions).
- Notion export being migrated (LATER, out of scope for the build): `C:\Users\chuache\Downloads\temp\Finance` (742 ledger rows, 6 tables, 9 real pages).

**AWS** — dedicated PERSONAL account **548045679450**, CLI profile **`neurasil`** (IAM user `neurasil-deploy`, AdministratorAccess). Root access key was shared in plaintext then **deleted** 2026-08-05 (0 root keys remain) — never use root. Region **ap-southeast-1**. Stack name `neurasil`. CFN artifacts bucket `neurasil-cfn-artifacts-548045679450`; vault bucket `neurasil-vault-548045679450`.

**Architecture (LOCKED, see [[dsae-aws-knowledge-vault]] style docs in plan):** API Gateway HTTP API → Lambda (Mangum/ASGI) → S3. **NOT** CloudFront+OAC+Function URL — a 20-agent council verified OAC 403s every MCP POST and strips Authorization. Custom domain **mcp.neurasil.com** via raw `AWS::ApiGatewayV2::DomainName` (Condition-gated; SAM's Domain sugar rejects intrinsics). Auth: stateless OAuth 2.1 + PKCE, **GitHub as IdP** allowlisting immutable numeric id **21016768**, HS256 JWTs (no session store, no DynamoDB), secrets in SSM `/neurasil/*`. Deploy via `aws cloudformation package/deploy` (no SAM CLI installed).

**Build gotchas (hard-won):** deps are **FastMCP 3.4.5 / mcp 1.29.0 / duckdb 1.5.5** (not the 2.x assumed at planning). Package with `uv --python-platform x86_64-manylinux_2_28 --python-version 3.13`; **never `sam build`** (clobbers linux wheels); **keep `*.dist-info`** (fastmcp reads its version via importlib.metadata → pruning it 500s every request). Use **`MSYS_NO_PATHCONV=1`** for any git-bash `aws` call with `/neurasil/*` args (MSYS mangles leading-slash paths). Menlo CA fix is local-only — build.ps1 asserts it never enters the artifact.

**Status @ 2026-08-05 — LIVE.** Phases 0–2 complete + 4 critique rounds applied (auth ×2, vault engine ×2, adapter ×2). `mcp.neurasil.com` serves **20 vault tools** over OAuth; connector added in claude.ai and confirmed working end to end. Real secrets in SSM (throwaway signing key rotated out via put-secrets). 72 moto-backed tests green. Core engine `src/neurasil/vault/` (storage CAS, schema, tables, notes, query, index) is MCP-agnostic; adapter `src/neurasil/tools.py`; `SETUP.md` is the reproducible stand-up guide. Deploy = `build.ps1` → `aws cloudformation package/deploy` with `CanonicalBaseUrl/DomainName/CertificateArn`; smoke via `scripts/smoke.py`.
Cert ARN `…/9dd8b4f3-d310-4bec-87f6-bcc269c8334b` (ISSUED). ACM validation CNAME + `mcp`→`d-j9j81d2ds1.execute-api.ap-southeast-1.amazonaws.com` live at registrar (keep forever). Connector client id `neurasil-E8DFZ4e0`; secrets in `/neurasil/*`.
Instruction notes SEEDED (`_meta/instructions.md` served as describe_vault routing preamble; readable `finance/index` note) via `scripts/seed.py` from `seed/*.md`. Cost tripwires in-template: zero-spend budget + `neurasil-invocation-spike` CloudWatch alarm (>1000 inv/5min → SNS email `3dw1nchu4@gmail.com`, needs one-time confirm); artifacts bucket has 30-day expiry. MTD spend ~$0.0002. User has driven the tools live from claude.ai (a `farm` note exists).

**UI — LIVE @ 2026-08-05 (Phases 1–3 done + deployed).** Notion-like React SPA (Vite) + REST API over the same vault core, on Cognito, at **`https://app.neurasil.com`**. Council-approved plan `C:\Users\chuache\.claude\plans\snazzy-honking-curry.md`. Design handoff (HTML prototype) in repo `design/prototype/` (Spline Sans, indigo, 3-pane). Decisions: React SPA Vite; **in-memory Bearer** (not BFF — user overrode chair; compensating CSP+DOMPurify+url-validation, all critique-verified solid); email/password Cognito login; **MCP auth migrated 2026-08-21 — but NOT via the Option A named here.** See the "Identity unified" section below; Option A (Cognito as the MCP authorization server) was rejected by council.
- **Phase 1 DONE** — engine additions (optimistic concurrency `_version`/`PreconditionFailed`, `update_table`/column `label`/`delete_column`/guarded `delete_table`, actor threading, `list_trashed_notes`).
- **Phase 2 DONE + DEPLOYED** — FastAPI REST adapter `src/neurasil/rest/` (cognito.py RS256/JWKS, problem.py RFC9457, app.py incl. `GET /api/notes` list) on a SEPARATE Lambda `neurasil-rest` (stack `neurasil-rest`, `requirements-rest.lock`, no fastmcp). Behind HTTP API `l0byh5w4hh` ($default stage). **Cognito** (ap-southeast-1): pool `ap-southeast-1_CDMiSRjte`, SPA client `3usnaa280lf3fkui0r5h6eggqu` (public/PKCE), resource server `vault` (vault/read, vault/write), Hosted UI `neurasil-auth.auth.ap-southeast-1.amazoncognito.com`, owner OWNER_SUB `092a855c-e091-7067-6323-9e98df6c88d3` (password set). Callback/logout URLs for app.neurasil.com + localhost:5173 registered; code grant + 3 scopes. 92 tests.
- **Phase 3 DONE + DEPLOYED** — SPA `ui/` (Vite/React/TanStack Query; screens Home/TableView/NoteView/NotesFolder/Search/Query/Trash; typed 8-type CellEditor). Hosting stack **`neurasil-web`** (ap-southeast-1): ONE CloudFront dist **E1TYSJLHUI4SHP** (domain `d2dgmlrl5usosb.cloudfront.net`, alias app.neurasil.com, us-east-1 cert `51ffe83f…`), default→private OAC S3 `neurasil-web-548045679450`, `/api/*`→REST origin, SPA-router CloudFront Function (extension-less→/index.html, NOT CustomErrorResponses — those are dist-wide and would clobber REST 4xx), managed SecurityHeadersPolicy (X-Frame-Options SAMEORIGIN etc.). CloudFront alarm in a separate **us-east-1** stack `neurasil-web-alarm` (CF metrics are us-east-1-only). 2-agent critique applied (fixed: bool cells never saved; stale notes-list invalidation; money no-op PATCH; PKCE finally-cleanup; dev CSP relax). **Owner-side done: CNAME + Cognito URLs.** Only remaining: authenticated end-to-end browser click-through (needs owner's password).
- **Phase 4 (MCP→Cognito) DONE 2026-08-21, see below.** **DEFERRED:** Notion→vault data
migration; re-point `dbs-statement-reconciliation` skill.

**Identity unified + attribution — LIVE & VERIFIED 2026-08-21.** Cognito is now the MCP
connector's **identity provider**, NOT its authorization server. A 19-agent council rejected the
old "Option A" (Cognito as AS) on measured grounds: `jwts.verify` pins HS256 against a local key
so an RS256 switch invalidates every live access AND 60-day refresh token at once; Cognito access
tokens carry no `aud` and Cognito has no RFC 8707 resource indicators; and `tools.py` has no
per-tool scope gate, so the end state is an unbound bearer opening all 20 tools including the
deletes. Rationale is written at the top of `src/neurasil/auth/cognito_idp.py`.
- **How it works:** `auth/cognito_idp.py` mirrors `github.py`'s 3-function shape. Hosted UI →
  `/oauth2/token` → verify the **ID token** (RS256/JWKS, `aud`=client id, `token_use=="id"`,
  email required + `email_verified`). Region is derived from the pool id, never `AWS_REGION`.
  neurasil still mints its own HS256 tokens; the `email` claim rides access AND refresh.
- **The switch:** SSM `/neurasil/idp` (`github`|`cognito`; **absent = github**). Not an env var,
  so rollback is one `put-parameter` with NO redeploy — and because an absent param is never
  cached, the flip took effect immediately rather than after the 300s TTL. The chosen leg is
  recorded IN the `gh_state` JWT so a login finishes on the leg it started on (a rollback would
  otherwise strand anyone mid-login).
- **Login client:** `4doss5d4j0a8d2pqf9oupfat0a` (`neurasil-mcp-login`), confidential, scopes
  **`openid email` ONLY** — that is the security boundary: it cannot mint a `vault/*` credential,
  and an ID token has no `scope` claim, so `rest/cognito.py` structurally rejects anything this leg
  produces. Do NOT add it to `CognitoClientIds`. Connector client id/secret UNCHANGED (no
  re-registration; one re-authentication).
- **Attribution:** `actor` was a channel label (`"mcp"`/`"rest"`); it is now the owner's EMAIL in
  `_updated_by` / `updated_by` / `deleted_by`, plus a NEW `created_by` on notes (preserved across
  overwrites). All 13 mutating MCP tools read it from the request context via
  `fastmcp.server.dependencies.get_access_token()` — never as a tool parameter, so `tools/list` is
  byte-identical and no connector re-approval was needed. REST gets it from
  `CognitoOwnerEmail` (new CFN param on `neurasil-rest`), mapped from the single owner sub.
  The ~11 schema-level ops (create_table/add_column/categories/layout/views) accept no actor and
  get a CloudWatch log line instead. Nothing was migrated: pre-cutover rows still say `mcp`.
  VERIFIED in S3: `notes/Sandbox.md` and `tables/connector_test/data.csv` carry
  `3dw1nchu4@gmail.com`; older rows still carry `mcp`.
- **NOT YET RETIRED — do not delete before 2026-10-20** (one refresh-token lifetime): the `github`
  branch in `routes.py`, `auth/github.py`, `/neurasil/github-*`, `/neurasil/allowed-github-id`,
  and the GitHub OAuth app. That is the only irreversible step; code is revertible from git, a
  deleted OAuth app is not.
- **Runbook:** SETUP.md §9. Config script `scripts/put-cognito-secrets.ps1` — SEPARATE from
  `put-secrets.ps1` because that one's first act is rotating the HMAC key, which would destroy the
  very refresh tokens that make the migration safe.

**View expressions (data viz) — Steps 1–2 SHIPPED 2026-08-21.** `ui/src/lib/expr.ts` is a closed
typed AST (15 node types) compiling predicates to SQL; every view type (chart/heatmap/calendar/
scatter) now takes a `filter` ANDed onto its own guards. `{str}` reaches SQL as a **bound
parameter** — `POST /api/query` gained `params` (keyword-only in `Query.run`, so the MCP `query`
tool is untouched). A comparison's RHS may be another column of the same row (`amount > threshold`).
`contains` compiles to duckdb's `contains()`, NOT `LIKE` (measured: a needle of `50%` also matches
"food 50 off"). Value nodes (`neg`/`op`/`if`/`coalesce`) compile and are tested but reachable from
no UI — that is Step 3. Editor: `ui/src/components/FilterEditor.tsx`; battery:
`npm run verify:expr`. Docs/authority: `docs/VIEW_EXPRESSIONS.md`.
- **Deploy/gotchas:** REST = `scripts/build-rest.ps1` → cfn package/deploy (stack `neurasil-rest`). SPA = `npm run build` in `ui/` → `aws s3 sync ui/dist/assets` + `cp index.html --cache-control no-cache` → `cloudfront create-invalidation --paths "/*"`. **Menlo proxy rewrites comma-bearing header whitespace → SigV4 SignatureDoesNotMatch on S3 PUT**: never pass `--cache-control "public,max-age=…,immutable"` on upload (assets are content-hashed, CloudFront default TTL is fine); index.html `no-cache` (no commas) is OK. Web stack in Singapore but ImportValue works only same-region, so the CF alarm is a separate us-east-1 stack. Cost table in SETUP.md: whole estate ~$0/mo single-user.

**Gotchas hit during the 2026-08-21 migration (all machine-level, all repo-documented now):**
`pwsh` is NOT installed — invoke `.ps1` helpers as `powershell -ExecutionPolicy Bypass -File
<FULLY QUALIFIED path>` (a relative path fails unless the shell is already in the repo root).
`aws cloudformation deploy --parameter-overrides RestCookieKeyParam=/neurasil/...` needs
`MSYS_NO_PATHCONV=1` in git-bash or CFN rejects the changeset ("must begin with /").
`curl` against mcp.neurasil.com returns the Menlo proxy's CONNECT response — use the venv python
(urllib picks up the CA-bundle env vars). `scripts/smoke_rest.py` must be pointed at the stack's
`RestApiUrl` output, NOT app.neurasil.com (CloudFront routes only `/api/*` there, so `/health`
falls through to the SPA). And `scripts/smoke.py --expect-idp` needs `--client-id`: `/authorize`
refuses an unknown client BEFORE choosing a leg, so without it the check can see nothing.
