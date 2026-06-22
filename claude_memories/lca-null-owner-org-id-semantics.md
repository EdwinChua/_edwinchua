---
name: lca-null-owner-org-id-semantics
description: Dev NULL owner_org_id rows are NOT a backfill backlog — on lcia_database_source NULL means GLOBAL (visible to all orgs) by design; on bulk_datasources NULL means superAdmin-only. SHARING_ENABLED is not blocked by them.
metadata: 
  node_type: memory
  type: project
  originSessionId: 656a8dd1-af88-4c5a-a64f-765b6387ae5a
---

Investigated the dev LCA DB (`leaf-dev`, Aurora PG 17) NULL `owner_org_id` rows on
2026-06-22. Conclusion: **do NOT backfill them** — NULL is meaningful, and its meaning
differs per table:

- **`lca.lcia_database_source`** sets `_scope_global_when_unowned = True` → NULL owner =
  **GLOBAL** (the curated REFERENCE library: readable by every org, writable only by
  app_super_admin). `scope_to_org()` in `backend/api/app/auth/scoping.py` adds the
  `owner_org_id IS NULL` disjunct for these. Migration `0005_uuid_portal_ids`
  **deliberately** nulled the old (orphaned integer) owners. So ecoinvent, A*STAR
  ISCE2/SIMTech, and "Dev Data Source" being NULL is correct — stamping ecoinvent to one
  tenant org would WRONGLY hide the global DB from every other org.
- **`lca.bulk_datasources`** does NOT set the flag → NULL owner = **superAdmin-only
  legacy**. Its 2 NULL rows are test data ("SIMTech Bulk Final Test", "Energy Market
  Authority Test"); when SHARING flips on they're just hidden from normal orgs (harmless).

The dev org is **`019ed186-0f21-7af9-afcd-3507c6ff9b52`** (a portal UUIDv7) — it owns the
lcia "Dev Test"/"Test" rows and is the only non-NULL owner in the whole DB.

**Decision (user, 2026-06-22):** leave the bulk NULLs as-is; revisit when **paid
(ENTITLED axis) and public datasets** are implemented. **`SHARING_ENABLED` was flipped
2026-06-19 and is LIVE on dev** (user-confirmed 2026-06-22) — this triage confirms the
live state is correct: no leak, no backfill. (Flag flips are manifest-only changes that
need a forced deploy to land, [[copilot-manifest-change-needs-path-filter]]; enforcement
also needs the portal wiring, [[platform-portal-enforcement-egress-chain]].)
