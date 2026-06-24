---
name: citext-email-migration-predeploy-check
description: "Portal users.email is now citext (case-insensitive perms); migration 0004 is committed on feat/admin-portal-integration + applied to local, but NOT on dev RDS — run a case-dup pre-check before it deploys or migrate-on-boot crash-loops the backend"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8fbdec7a-9043-477b-9d65-1872fd99f2c5
---

The ADVISE Identity Portal (`advise_lca_platform_with_admin/apps/server`) made `users.email` **citext** so the permission lookup (`x-user-email` → user) and the `users_email_unique` constraint are **case-insensitive** (was varchar + plain `eq()`, so `John.Doe@x` ≠ `john.doe@x` → a legit user got "Invalid user email"). Fix = citext column + migration **`drizzle/0004_sad_magik.sql`** (`CREATE EXTENSION citext`; drop/re-add `users_email_unique` around `ALTER COLUMN email TYPE citext`) + lowercase-on-insert everywhere (createUser, invite, bootstrap, seedCore) + lowercased the userExistance LRU key. Committed `62582b50` on **`feat/admin-portal-integration`**; applied + verified on the **local** DB (citext type, case-insensitive lookup AND unique both confirmed). **Not yet on the dev RDS.**

**Before 0004 reaches the dev RDS** (it deploys only when merged to `dev` — CI SSM-deploy + migrate-on-boot fire on `dev` only): run a **case-duplicate pre-check**. The re-added UNIQUE is now case-insensitive, so `ADD CONSTRAINT` FAILS on pre-existing case-dupes → the migration throws → `entrypoint.ts` `process.exit(1)` + `restart: always` → the backend **crash-loops** (portal down).
```sql
SELECT lower(email) AS email_ci, count(*) AS n, array_agg(email) AS variants
FROM admin.users GROUP BY lower(email) HAVING count(*) > 1;
```
0 rows → safe to deploy. ≥1 row → dedup first (repoint FKs to `users.id`, drop/rename losers), re-check, then merge. citext itself is fine on RDS (master user = rds_superuser can `CREATE EXTENSION`; the node-postgres migrator wraps the migration file in one transaction so a failure rolls back atomically). Dev data already looks lowercase (e.g. `koo_chia_wei@a-star.edu.sg`), so dupes are unlikely — the check is cheap insurance. Running it needs box/SSM access to the private RDS (the RDS-connectivity task is pinned). See [[portal-dev-ec2-docker-runtime]].

**pglite gotcha (tests):** pglite's citext `=` is case-insensitive but its btree opclass does NOT dedupe case-variants, so DB-level case-insensitive UNIQUE can't be asserted on pglite (only real PG). The test pglite instance must load the citext contrib — `src/db/index.ts` imports it via the `@electric-sql/pglite/contrib/citext` **exports subpath** with a `// @ts-ignore` (tsc's classic moduleResolution can't see exports subpaths, and the raw `dist/` path is blocked by the exports map at runtime — only the subpath works for bun).
