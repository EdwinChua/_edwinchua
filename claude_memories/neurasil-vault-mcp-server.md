---
name: neurasil-vault-mcp-server
description: "neurasil = self-hosted second-brain vault MCP server replacing Notion; personal AWS account, deployed skeleton, key build facts"
metadata: 
  node_type: memory
  type: project
  originSessionId: e696b565-4e5d-4e86-ba47-b5854963dfea
  modified: 2026-08-05T08:00:02.581Z
---

**neurasil** ("neural silicon") — a self-hosted personal "second brain" (free-form markdown notes + schema-on-demand CSV tables with real SQL) reachable as a remote MCP **custom connector** from claude.ai / Desktop / Cowork. Replaces Notion, whose hosted MCP connector kept failing OAuth. Started 2026-08-05.

**Where things live**
- Repo: private `github.com/EdwinChua/neurasil` (personal identity 3dw1nchu4@gmail.com); local `C:\Users\chuache\Documents\repos\neurasil`.
- Council-amended implementation plan: `C:\Users\chuache\.claude\plans\declarative-prancing-codd.md` (the detailed source of truth for design decisions).
- Notion export being migrated (LATER, out of scope for the build): `C:\Users\chuache\Downloads\temp\Finance` (742 ledger rows, 6 tables, 9 real pages).

**AWS** — dedicated PERSONAL account **548045679450**, CLI profile **`neurasil`** (IAM user `neurasil-deploy`, AdministratorAccess). Root access key was shared in plaintext then **deleted** 2026-08-05 (0 root keys remain) — never use root. Region **ap-southeast-1**. Stack name `neurasil`. CFN artifacts bucket `neurasil-cfn-artifacts-548045679450`; vault bucket `neurasil-vault-548045679450`.

**Architecture (LOCKED, see [[dsae-aws-knowledge-vault]] style docs in plan):** API Gateway HTTP API → Lambda (Mangum/ASGI) → S3. **NOT** CloudFront+OAC+Function URL — a 20-agent council verified OAC 403s every MCP POST and strips Authorization. Custom domain **mcp.neurasil.com** via raw `AWS::ApiGatewayV2::DomainName` (Condition-gated; SAM's Domain sugar rejects intrinsics). Auth: stateless OAuth 2.1 + PKCE, **GitHub as IdP** allowlisting immutable numeric id **21016768**, HS256 JWTs (no session store, no DynamoDB), secrets in SSM `/neurasil/*`. Deploy via `aws cloudformation package/deploy` (no SAM CLI installed).

**Build gotchas (hard-won):** deps are **FastMCP 3.4.5 / mcp 1.29.0 / duckdb 1.5.5** (not the 2.x assumed at planning). Package with `uv --python-platform x86_64-manylinux_2_28 --python-version 3.13`; **never `sam build`** (clobbers linux wheels); **keep `*.dist-info`** (fastmcp reads its version via importlib.metadata → pruning it 500s every request). Use **`MSYS_NO_PATHCONV=1`** for any git-bash `aws` call with `/neurasil/*` args (MSYS mangles leading-slash paths). Menlo CA fix is local-only — build.ps1 asserts it never enters the artifact.

**Status @ 2026-08-05:** Phase 0 walking skeleton DEPLOYED + verified on real Lambda (authenticated `/mcp` initialize+tools/list+echo works — Mangum lifespan risk retired). execute-api URL `https://vx1obv9002.execute-api.ap-southeast-1.amazonaws.com`. Throwaway JWT signing key in SSM (rotate via `scripts/put-secrets.ps1` before go-live). BLOCKED on: ACM cert `PENDING_VALIDATION` (user must add the `_2136ecb78430260d7c4f662052874185.mcp` CNAME at neurasil.com registrar). Then: put-secrets (user runs, GitHub secret), domain deploy, `mcp` CNAME, add connector on 3 surfaces. Then Phase 1 = core vault engine (`src/vault/`).
