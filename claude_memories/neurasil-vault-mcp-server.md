---
name: neurasil-vault-mcp-server
description: "neurasil = self-hosted second-brain vault MCP server replacing Notion; personal AWS account, deployed skeleton, key build facts"
metadata: 
  node_type: memory
  type: project
  originSessionId: e696b565-4e5d-4e86-ba47-b5854963dfea
  modified: 2026-08-05T14:03:07.060Z
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

**UI BUILD IN PROGRESS (2026-08-05):** Notion-like React SPA (Vite) + REST API over the same vault core, on Cognito. Council-approved plan at `C:\Users\chuache\.claude\plans\snazzy-honking-curry.md`. Design handoff (HTML prototype) saved in repo `design/prototype/` (Spline Sans, indigo accent, 3-pane; validation already mirrors backend). Decisions: React SPA Vite; **in-memory Bearer** (not BFF — user overrode chair; compensating CSP+DOMPurify+url-validation mandatory); email/password Cognito login; **MCP auth NOT migrated in this cycle** (deferred to Phase 4, target = Option A full-unification, reusing the same pool + `rest/cognito.py` verifier).
- **Phase 1 DONE** (engine additions: optimistic concurrency via `_version`/`PreconditionFailed`, `update_table`/column `label`/`delete_column`/guarded `delete_table`, actor threading, `list_trashed_notes`; 2 critiques applied). 84 tests.
- **Phase 2 IN PROGRESS**: FastAPI REST adapter at `src/neurasil/rest/` (cognito.py RS256/JWKS verifier, problem.py RFC9457, app.py routes) — SEPARATE Lambda artifact (`requirements-rest.lock`, no fastmcp; starlette 1.4 vs MCP's 1.3.1). 89 tests. **Cognito provisioned** (region ap-southeast-1): pool `ap-southeast-1_CDMiSRjte`, SPA client `3usnaa280lf3fkui0r5h6eggqu` (public/PKCE, no secret), resource server `vault` (scopes vault/read, vault/write), Hosted UI `neurasil-auth.auth.ap-southeast-1.amazoncognito.com`, owner user `3dw1nchu4@gmail.com` OWNER_SUB `092a855c-e091-7067-6323-9e98df6c88d3` (user sets permanent password via admin-set-user-password). TODO: REST Lambda in SAM + COGNITO_* env, 2-agent critique, deploy behind CloudFront (`app.neurasil.com`, us-east-1 cert pending user CNAME).
- **Phase 3** (SPA) and **Phase 4** (MCP→Cognito) not started. **DEFERRED:** Notion→vault data migration; re-point `dbs-statement-reconciliation` skill.
