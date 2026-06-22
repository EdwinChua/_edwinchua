---
name: apprunner-dev-live
description: ADVISE Identity Portal dev runs on App Runner + RDS; App Runner usable via CFN/CLI despite the disabled console
metadata: 
  node_type: memory
  type: project
  originSessionId: ba6d4fe5-89ca-4206-86d5-f0adf2384f5a
---

The **ADVISE Identity Portal** dev env (repo `advise_lca_platform_with_admin`) is deployed on **AWS App Runner + RDS PostgreSQL** in account `701518539545`, region `ap-southeast-1`, CFN stack `advise-identity-portal-apprunner-dev` (template `infra/apprunner-dev.yaml`, two-pass — see `infra/README-apprunner.md`). Live at **https://dev.identity.advise.technology** (custom domain on the frontend service; backend at its `*.awsapprunner.com` URL, bearer-token protected).

**Non-obvious:** AWS App Runner stopped accepting new customers 2026-04-30 and the **console create flow is disabled**, BUT this account can still create App Runner services via **CloudFormation/CLI** (the `CreateService` API still works for it) — proven by a successful deploy on 2026-06-17. So App Runner remains usable here; it's maintenance-mode (no new features, no announced EOS). The evaluated successor is **ECS Express Mode** (~2× cost due to a forced shared ALB) — deferred to a deliberate pre-prod migration, not done now.

Gotchas that bit us (all fixed, in git): RDS enforces SSL → `DATABASE_URL` needs `?sslmode=no-verify` (node-postgres doesn't enable SSL by default); the Windows AWS CLI crashes printing the app's emoji logs unless `PYTHONUTF8=1`; SSM `/`-path args need `MSYS_NO_PATHCONV=1` in Git Bash.

Login caveat: super-admins are seeded in the **app DB** for role mapping, but login is via **Cognito** (pool `ap-southeast-1_vXj2lFhBz`, client `4fhjj6ea5r8bave59na3velrvt`) — the email must also exist as a Cognito user. As of deploy, only one of `koo_chia_wei@a-star.edu.sg` / `edwin_chua@a-star.edu.sg` had a Cognito account. See [[cognito-dev-pool-topology]].
