---
name: portal-dev-ec2-docker-runtime
description: "ADVISE Identity Portal dev runs on EC2 + Docker Compose + a dedicated RDS (migrated off App Runner, which is retired); CI deploys via SSM"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8fbdec7a-9043-477b-9d65-1872fd99f2c5
---

The **ADVISE Identity Portal** dev env (`advise_lca_platform_with_admin`, acct `701518539545`, `ap-southeast-1`) was **migrated OFF AWS App Runner** (2026-06-24) onto a **single EC2 box running Docker Compose + a dedicated managed RDS**. Live at **https://dev.identity.advise.technology** (frontend) and **https://api.dev.identity.advise.technology** (backend), both **A-records → the box's Elastic IP**, TLS via Caddy + Let's Encrypt.

**Runtime:** CFN stack `advise-identity-portal-ec2-dev` (template `infra/ec2-podman-dev.yaml`) = own VPC (`10.50`), EC2 `t3.small` AL2023 (public subnet, EIP, IMDSv2), and a **private RDS `advise-identity-portal-dev-box`** in 2 private subnets (reached only from the box SG). On the box: **Docker Compose** (`infra/podman/{compose.yaml,Caddyfile,bootstrap.sh}`) runs `caddy + frontend + backend` (no on-box DB — box is stateless). Shell/ops via **SSM Session Manager** (no SSH). App brought up out-of-band via SSM (`bootstrap.sh` assembles `DATABASE_URL` from the RDS-managed Secrets Manager secret, `sslmode=no-verify`, and `docker compose up`). The backend self-seeds on first boot (`SEED_ON_BOOT=true` + `SEED_FORCE_TOKEN=true` binding the `admin-portal-dev` client to the frontend's `ADMIN_API_TOKEN`); flip `SEED_ON_BOOT=false` after.

**Why off App Runner:** its VPC-connected backend could no longer provision ("App Runner instance stopped due to an internal system error"); even a no-op redeploy of the known-good config rolled back, while a throwaway *public-image* App Runner service provisioned fine → the fault was the VPC connector / Hyperplane-ENI path, not account-wide. (This also caused the "We couldn't load your account" outage — the frontend's `ADMIN_API_TOKEN` matched no client row in the DB; the seed rebind fixed it.)

**App Runner retired:** the old stack `advise-identity-portal-apprunner-dev` was **stripped to ONLY the 2 ECR repos + the `GithubDeployRole`** (shared CI infra — kept because deleting the stack would destroy the ECR repos CI pushes to and the box pulls from). Its App Runner services, VPC connector, old VPC (`10.40`), old RDS (`advise-identity-portal-dev`), and App-Runner IAM/autoscaling were all deleted.

**CI/CD:** GitHub Actions (`.github/workflows/{backend,frontend}-push-ecr-dev.yml`) build + push images to ECR on push to `dev`, **then deploy via SSM** (`docker compose pull/up`, instance resolved by tag `advise-identity-portal-dev-box`) — App Runner's auto-deploy is gone, so `GithubDeployRole` gained `ssm:SendCommand`. ⚠️ The SSM deploy step is committed on **`feat/admin-portal-integration`**, not yet on `dev` — it only activates once merged/cherry-picked to `dev`. That branch also holds the unmerged UI redesign + the display-name/disable-client features + all this infra.

**Gotchas (Windows + corporate Menlo TLS proxy):** AWS creds are SSO-temporary and **don't persist between shells** (re-provide each session); set `AWS_CA_BUNDLE` to the exported Windows CA bundle for the AWS CLI through Menlo; **Menlo mangles AWS CLI CloudWatch POST bodies** (other APIs — App Runner/CFN/SSM/ECR/RDS — are fine; for CloudWatch use `--output json` to avoid emoji `charmap` crashes); set `PYTHONUTF8=1` and/or strip non-ASCII when printing app logs; prefix SSM `/`-path names with `MSYS_NO_PATHCONV=1` in Git Bash. AL2023 ships **Docker, not Podman** (no podman in its repos), so the box uses Docker + a downloaded compose-v2 binary despite the global Podman preference.

Login is via **Cognito** (pool `ap-southeast-1_vXj2lFhBz`, client `4fhjj6ea5r8bave59na3velrvt`) — see [[cognito-dev-pool-topology]]. The platform (`advise_lca_platform`) calls `api.dev.identity…` for enforcement with the same `ADMIN_API_TOKEN` — see [[platform-portal-enforcement-egress-chain]]. Single-instance frontend still wants the pinned key — see [[nextjs-server-action-skew-apprunner]].
