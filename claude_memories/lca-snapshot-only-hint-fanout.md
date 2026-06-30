---
name: lca-snapshot-only-hint-fanout
description: "any lca query joining lcia/lcia_description/lcia_database/lcia_database_source needs the ONLY hint — snapshot children share the live PK and fan out, invisible to dev/local tests"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2bcaab4c-f54e-4421-99b8-45620febd941
---

In the platform's `lca` schema, `lca_snapshot.{lcia, lcia_description, lcia_database, lcia_database_source, upr_exchange_name}` are PostgreSQL INHERITANCE children of their live `lca.*` parents, and a snapshot child carries the **SAME `id` (PK)** as the live row it froze (PG does not enforce PK uniqueness across an inheritance hierarchy). So any query that joins one of these tables **by id without** `.with_hint(Model, "ONLY", dialect_name="postgresql")` (or raw `FROM ONLY`) matches the live row **plus** every snapshot child → row fan-out: `.one_or_none()` raises `MultipleResultsFound`, and `array_agg`/aggregates gain phantom values. `emission_factor_service.py` uses `ONLY` pervasively (~43 times) for exactly this; the views are defined `FROM ONLY ...` too.

**Why:** snapshots preserve the live id by design (that's how a datapoint's history is keyed), so the child collides with the parent on `id`.

**How to apply:** when you add ANY new query/join touching those tables, add the `ONLY` hint on every joined parent. **LANDMINE:** the `lca_snapshot.*` tables are EMPTY on both dev RDS and the local container today, so neither the test suite (fixtures never seed snapshots) nor a live-DB sanity check will catch a missing `ONLY` — you must reason from `pg_inherits`, not from data. This bit D2b's `_narrowed_arrays_lateral` + `_visible_reference_product_ids` (a 2-agent critique flagged it; fixed in `8fdbbed92` with a regression test that seeds a snapshot child sharing a live id). Related: [[lca-null-owner-org-id-semantics]].
