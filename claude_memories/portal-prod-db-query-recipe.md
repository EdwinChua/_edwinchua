---
name: portal-prod-db-query-recipe
description: "How to run a read-only query against the Identity Portal prod/dev RDS — private DB, no psql on the box, must go via SSM + a postgres container with --env-file and the RDS CA mounted"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8bf52cbf-6f8d-4a8f-93d6-afa6c933c754
  modified: 2026-08-05T04:53:33.502Z
---

Querying the **ADVISE Identity Portal** RDS (acct `701518539545`, `ap-southeast-1`). Both DBs are
`PubliclyAccessible: false`, so they are **unreachable from the laptop** — every query goes through
an SSM command on the env's box. Boxes (tag `advise-identity-portal-{env}-box`):
prod `i-06912c4dc4620374e`, dev `i-013eb028a4354d2ed`.

**There is no `psql` on the box** — use a throwaway container. Working invocation:

```
cd /opt/portal && echo <SQL_B64> | base64 -d > /tmp/q.sql && \
docker run --rm --env-file /opt/portal/.env.backend \
  -v /tmp/q.sql:/q.sql:ro -v /opt/portal/rds-ca.pem:/etc/ssl/rds-ca.pem:ro \
  postgres:16-alpine sh -c 'psql "$DATABASE_URL" -At -f /q.sql'
```

Three gotchas, each of which cost an attempt:
1. **Never `set -a; . ./.env.backend`.** `DATABASE_URL` contains `&` (query params), so `sh` treats
   it as a background operator and the variable ends up empty — psql then silently falls back to a
   local unix socket and reports "is the server running locally?". `docker run --env-file` parses
   `KEY=VALUE` literally and is the correct way in.
2. **Mount the CA.** The URL sets `sslrootcert=/etc/ssl/rds-ca.pem`; without the bind-mount psql
   fails with `root certificate file "/etc/ssl/rds-ca.pem" does not exist`.
3. **base64 the SQL.** Quoting does not survive shell → JSON → SSM → shell otherwise.

Also: pass SQL/params via `--parameters file://<WINDOWS path>` — the AWS CLI is Windows-native and
rejects git-bash `/c/...` paths. Set `PYTHONIOENCODING=utf-8 PYTHONUTF8=1` before reading command
output, or the CLI dies on `charmap` when logs contain emoji (the backend logs `✅`/`🦊`).

**Schema names that are easy to get wrong:** the drizzle pointer is
`drizzle.__drizzle_migrations` (`count(*)` + `max(created_at)` = which migrations have run);
`admin.applications`' name column is **`name`**, not `application_name`.

⚠️ `aws ssm send-command` is remote execution on a prod box and may be **blocked by the permission
classifier** — expect to need explicit user approval, and don't route around a denial.

Deploy/runtime context: [[portal-dev-ec2-docker-runtime]]. Prod release state: [[etea-prod-golive]].
