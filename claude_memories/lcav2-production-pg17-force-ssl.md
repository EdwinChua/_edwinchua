---
name: lcav2-production-pg17-force-ssl
description: "lcav2-production RDS (LCA v2 acct, hosts Green Compass + LCA DBs) is on PG17 with custom param group lcav2-postgres17 (rds.force_ssl=0); never switch to default.postgres17"
metadata:
  node_type: memory
  type: project
  originSessionId: 6373ae60-2317-49b1-b2a4-e258b444a4ee
  modified: 2026-10-19T09:58:41.811Z
---

`lcav2-production` (account 804210690368, db.t4g.small) was upgraded PostgreSQL 14.22 → 17.11 on 2026-10-19 (≈3 min outage, done during a zero-session moment). It uses custom parameter group **`lcav2-postgres17`** = postgres17 defaults + `rds.force_ssl=0`.

**Why:** PG15+ default parameter groups set `rds.force_ssl=1`. Green Compass backend (Sequelize + node `pg`, no SSL options) and some LCA v2 Lambdas (pg8000) connect without SSL, so the default group would lock them out. Dry run + prod both verified `sslmode=disable` still works; user tested Green Compass dev UI after the upgrade.

**How to apply:**
- Never attach `default.postgres17`/`default.postgres18` to this instance, and copy the `rds.force_ssl=0` override into any future major-version param group, until every client uses SSL (option 2: `dialectOptions.ssl` + RDS CA bundle in green_compass_backend, PGSSLMODE for scripts/Lambdas).
- The instance holds 4 app DBs: `lcav2_prod`, `greencompass_prod`, `greencompass_dev`, `greencompass_tr_dev`. `vacuumdb --all` fails on RDS (rdsadmin DB) — run per database.
- Snapshots kept: `lcav2-production-pre-pg17-20261019-0939` (14.22, rollback point; keep ≥ 2 weeks) and `lcav2-production-post-pg17-20261019-0956`.
- Open follow-ups: pending OS `system-update`; SG still allows 5432 from 0.0.0.0/0 ("temp migration"); the shared dev/prod DB password was exposed in a Claude session transcript on 2026-10-19 — rotate it.

Related: [[etea-feature-split-design]] (different DB — eTEA uses Aurora), [[cognito-dev-pool-topology]].
