---
name: dsae-aws-knowledge-vault
description: "where the AWS-estate architecture/quirks/cost docs live (the dsae Obsidian vault) and how it's structured"
metadata: 
  node_type: memory
  type: reference
  originSessionId: ba6d4fe5-89ca-4206-86d5-f0adf2384f5a
---

The AWS estate (all ~7 accounts, services, architecture, quirks/workarounds, cost, cleanup
backlog) is documented in an **Obsidian vault at `C:\Users\chuache\Documents\repos\dsae`**
(git repo, branch `main`). When the user asks to document AWS architecture / "aws stuff" /
quirks / reasoning, **update this vault** (and commit when asked).

Structure:
- `aws/Accounts/<profile>.md` — per-account deep-dives (account_id, services, flags). Account
  **701518539545 = profile `sis-susadmin` = ADVISE Identity Portal** (App Runner + RDS).
- `aws/Services/<Service>.md` — per-service pages (App Runner, VPC, RDS, Cognito, CloudFormation,
  ECR, SSM Parameter Store, ELB, …).
- `aws/Architecture.md` — one Mermaid diagram per platform. `Repositories.md` — repo→account map
  (note the `advise_lca_platform*` naming gotcha). `Cleanup Backlog.md`, `Service Inventory.md`,
  `AWS Overview.md`, `Cost Optimization.md`.

Style to match: YAML frontmatter (`title` / `tags: [aws, service|account]` / `updated: YYYY-MM-DD`),
Obsidian `[[wikilinks]]` for accounts (`[[sis-susadmin]]`) and services (`[[App Runner]]`),
`> [!note]` / `⚠️` / `🚩` callouts, Markdown tables, file names use spaces not kebab.

The Identity Portal's App Runner quirks are written up here — see [[apprunner-dev-live]],
[[nextjs-server-action-skew-apprunner]]. The catalog egress-proxy (frontend fetches the eTEA
`/access-catalog` because the VPC-egress backend has no internet) is documented in
`aws/Services/App Runner.md` + `aws/Accounts/sis-susadmin.md`.
