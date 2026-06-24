---
name: citext-email-migration-predeploy-check
description: "Portal users.email is citext (case-insensitive perms) — migration 0004 SHIPPED to dev 2026-06-24 (applied cleanly, no case-dups); the same case-dup pre-check is needed before any FUTURE env (prod) gets it or migrate-on-boot crash-loops"
metadata: 
  node_type: memory
  type: project
  originSessionId: 8fbdec7a-9043-477b-9d65-1872fd99f2c5
---

The ADVISE Identity Portal (`advise_lca_platform_with_admin/apps/server`) made `users.email` **citext** so the permission lookup (`x-user-email` → user) and `users_email_unique` are **case-insensitive** (was varchar + plain `eq()`, so `John.Doe@x` ≠ `john.doe@x` → a legit user got "Invalid user email"). Fix = citext column + migration **`drizzle/0004_sad_magik.sql`** (`CREATE EXTENSION citext`; drop/re-add `users_email_unique` around `ALTER COLUMN email TYPE citext`) + lowercase-on-insert everywhere (createUser, invite, bootstrap, seedCore) + lowercased the userExistance LRU key. Committed `62582b50` on `feat/admin-portal-integration`.

**Shipped to dev 2026-06-24:** the user merged all of `feat/admin-portal-integration` into `dev` (not just this fix — also migrations 0002/0003, org-admin authz, usage telemetry, cognito id-token refresh). CI built + SSM-deployed to the box; migrate-on-boot applied 0002→0003→0004 to the dev RDS cleanly (`https://api.dev.identity.advise.technology/health` = 200, frontend = 200). So the skipped case-dup pre-check turned out fine — dev had no case-variant emails.

**Before this migration reaches ANY future env (esp. prod):** run the case-dup pre-check first — the re-added UNIQUE is case-insensitive, so `ADD CONSTRAINT` FAILS on pre-existing case-dupes → migrate-on-boot `exit(1)` + `restart: always` → backend crash-loops.
```sql
SELECT lower(email) AS email_ci, count(*) AS n, array_agg(email) AS variants
FROM admin.users GROUP BY lower(email) HAVING count(*) > 1;
```
0 rows → safe; ≥1 → dedup (repoint FKs to `users.id`, drop/rename losers) then deploy. citext is fine on RDS (master user = rds_superuser; the node-postgres migrator wraps the migration file in one transaction → atomic rollback on failure).

**pglite gotcha (tests):** pglite's citext `=` is case-insensitive but its btree opclass does NOT dedupe case-variants, so DB-level case-insensitive UNIQUE can't be asserted on pglite (only real PG). The test pglite instance loads the citext contrib — `src/db/index.ts` imports it via the `@electric-sql/pglite/contrib/citext` exports subpath with a `// @ts-ignore` (tsc's classic moduleResolution can't see exports subpaths; the raw `dist/` path is blocked by the exports map at runtime — only the subpath works for bun). See [[portal-dev-ec2-docker-runtime]].
