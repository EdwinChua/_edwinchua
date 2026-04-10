---
tags: [lca, work, investigation, bugs]
---
> **Status:** Open — root cause confirmed, fix direction TBD

## Problem Statement

The frontend displays final emission numbers that are not representative of the full product system. Some indicators show 0 where they should have values — total impact per indicator is incomplete.

---

## Root Cause (Confirmed)

The LCA calculator builds **one matrix** with ALL indicator UUIDs (union of Emission + CF sources). Each exchange only contributes to indicators covered by its tagged EF/CF dataset.

Exchanges that are:

- **untagged** (`upr_impact_assessment_settings` is NULL), or
- **tagged to a **`**ref_id**`** whose dataset doesn't cover a given indicator**

...contribute **silent 0s** to that indicator's column in the matrix.

Final total per indicator = sum of contributions from exchanges that actually have coverage. Missing coverage = underreported result.

---

## How the Calculator Builds the Indicator Matrix

### Step 1 — Global indicator list (`get_indicators`)

Unions ALL indicator UUIDs from both sources, deduplicated:

```sql
-- Emission: lcia_data joined by lcia_description_id
SELECT ld.impact_indicator_id FROM lca.lcia_data ld
JOIN exchange_settings es ON ld.lcia_description_id = es.ref_id
WHERE es.factor_type = 'Emission'

UNION ALL

-- Characterization: cf_data joined by cf_id
SELECT cf.impact_indicator_id FROM lca.cf_data cf
JOIN exchange_settings es ON cf.cf_id = es.ref_id
WHERE es.factor_type = 'Characterization'
```

Result: flat ordered list of UUIDs — no names, no category, no method.

### Step 2 — Per-IO indicator quantities (`get_input_outputs`)

Each exchange gets its indicators array (id + quantity) via a CASE statement:

- `factortype = 'Emission'` → queries `lcia_data` WHERE `lcia_description_id = ref_id`
- `factortype = 'Characterization'` → queries `cf_data` WHERE `cf_id = ref_id`

### Step 3 — Matrix build & calculation

UUID list from Step 1 sets column order. Per-IO values from Step 2 fill the emission factor matrix. Single matrix inversion, one result per indicator UUID.

### Step 4 — Persistence (`run_calculation_refresh_lcia_data`)

Results upserted into `lcia_data` — one row per `(lcia_description_id, impact_indicator_id, lcia_database_id)`. Name/category/method resolved at display time via joins.

---

## `upr_impact_assessment_settings` Structure

```json
[{"id": "default", "settings": {"ref_id": "<uuid>", "factortype": "Emission"}}]
```

- `factortype: "Emission"` → `ref_id` is a `lcia_description_id` in `lcia_data`
- `factortype: "Characterization"` → `ref_id` is a `cf_id` in `cf_data`

---

## Investigation Steps & Findings

### ✅ Step 1 — All exchanges have `upr_impact_assessment_settings` populated

```sql
SELECT us.name AS stage_name, up.name AS process_name,
       ue.id AS exchange_id, uen.name AS exchange_name,
       ue.upr_impact_assessment_settings
FROM lca.upr_stage us
JOIN lca.upr_process up ON up.upr_stage_id = us.id
JOIN lca.upr_exchange ue ON ue.upr_process_id = up.id
JOIN lca.upr_exchange_name uen ON uen.id = ue.upr_exchange_name_id
WHERE us.lcia_description_id = '87c9c059-1a27-42b8-affa-5297204734eb';
```

**Finding:** All exchanges are tagged — tagging is not the problem.

### ✅ Step 2 — EF coverage NULL for target indicator

```sql
SELECT uen.name AS exchange_name,
       (settings->>'factortype') AS factortype,
       (settings->>'ref_id') AS ref_id,
       COALESCE(ld.amount, cf.amount) AS ef_value,
       CASE
           WHEN ld.amount IS NOT NULL THEN 'from lcia_data'
           WHEN cf.amount IS NOT NULL THEN 'from cf_data'
           ELSE 'missing'
       END AS source
FROM lca.upr_stage us
JOIN lca.upr_process up ON up.upr_stage_id = us.id
JOIN lca.upr_exchange ue ON ue.upr_process_id = up.id
JOIN lca.upr_exchange_name uen ON uen.id = ue.upr_exchange_name_id
CROSS JOIN LATERAL jsonb_array_elements(ue.upr_impact_assessment_settings) AS elem
CROSS JOIN LATERAL jsonb_extract_path(elem, 'settings') AS settings
LEFT JOIN lca.lcia_data ld
    ON ld.lcia_description_id = (settings->>'ref_id')::uuid
    AND ld.impact_indicator_id = '3c29b49e-9e0d-488c-ae3a-368ebe6ecf25'
    AND (settings->>'factortype') = 'Emission'
LEFT JOIN lca.cf_data cf
    ON cf.cf_id = (settings->>'ref_id')::uuid
    AND cf.impact_indicator_id = '3c29b49e-9e0d-488c-ae3a-368ebe6ecf25'
    AND (settings->>'factortype') = 'Characterization'
WHERE us.lcia_description_id = '87c9c059-1a27-42b8-affa-5297204734eb'
  AND (settings->>'ref_id') != ''
ORDER BY ef_value NULLS FIRST;
```

**Finding:** `ef_value` returned NULL for Emission-type exchanges for indicator `3c29b49e...`.

### ✅ Step 3 — `lcia_description` row exists for the `ref_id`

```sql
SELECT * FROM lca.lcia_description WHERE id = 'd0c823c0-4959-4b21-9c8b-f0484a9cdf38';
```

**Finding:** Row exists — `ref_id` is valid.

### ✅ Step 4 — `lcia_data` has no rows for this description + indicator

```sql
SELECT ld.impact_indicator_id, ii.name AS indicator_name, ld.amount
FROM lca.lcia_data ld
JOIN lca.impact_indicator ii ON ii.id = ld.impact_indicator_id
WHERE ld.lcia_description_id = 'd0c823c0-4959-4b21-9c8b-f0484a9cdf38'
  AND ld.impact_indicator_id = '3c29b49e-9e0d-488c-ae3a-368ebe6ecf25';
```

**Finding:** No rows returned. **The EF dataset for that description does not include this indicator. The data gap is in **`**lcia_data**`** itself.**

---

## Key IDs Under Investigation

| Field | Value |
| --- | --- |
| Product / UPR | `lcia_description_id = 87c9c059-1a27-42b8-affa-5297204734eb` |
| Indicator under test | `3c29b49e-9e0d-488c-ae3a-368ebe6ecf25` |
| Previously investigated indicator | `00accaee-d492-4942-a17a-bacddcd45443` |
| EF description `ref_id` | `d0c823c0-4959-4b21-9c8b-f0484a9cdf38` |

Get indicator metadata:

```sql
SELECT ii.name AS indicator_name, ic.name AS impact_category, im.name AS impact_method
FROM lca.impact_indicator ii
JOIN lca.impact_category ic ON ic.id = ii.impact_category_id
JOIN lca.impact_method im ON im.id = ii.impact_method_id
WHERE ii.id = '3c29b49e-9e0d-488c-ae3a-368ebe6ecf25';
```

---

## Reference Queries

### Get all EFs for a flow name

```sql
SELECT uen.name AS ef_flow_name, ii.name AS indicator_name,
       ic.name AS impact_category, im.name AS impact_method, ld.amount
FROM lca.upr_exchange_name uen
JOIN lca.lcia_description ldesc ON ldesc.upr_exchange_name_id = uen.id
JOIN lca.lcia_data ld ON ld.lcia_description_id = ldesc.id
JOIN lca.impact_indicator ii ON ii.id = ld.impact_indicator_id
JOIN lca.impact_category ic ON ic.id = ii.impact_category_id
JOIN lca.impact_method im ON im.id = ii.impact_method_id
WHERE uen.name ILIKE '%your flow name%';
```

### Get EF tagged to a UPR exchange by flow name

```sql
SELECT uen.name AS flow_name, ue.id AS upr_exchange_id,
       (settings->>'factortype') AS factortype,
       (settings->>'ref_id')::uuid AS ref_id,
       uen2.name AS ef_flow_name
FROM lca.upr_exchange ue
JOIN lca.upr_exchange_name uen ON uen.id = ue.upr_exchange_name_id
CROSS JOIN LATERAL jsonb_array_elements(ue.upr_impact_assessment_settings) AS elem
CROSS JOIN LATERAL jsonb_extract_path(elem, 'settings') AS settings
JOIN lca.lcia_description ldesc ON ldesc.id = (settings->>'ref_id')::uuid
JOIN lca.upr_exchange_name uen2 ON uen2.id = ldesc.upr_exchange_name_id
WHERE uen.name ILIKE '%Water for washing%'
  AND (settings->>'ref_id') != '';
```

### Get EF values with datasource, category, method

```sql
SELECT ldb.name AS datasource_name, ld.lcia_description_id,
       ii.name AS indicator_name, ic.name AS impact_category,
       im.name AS impact_method, ld.amount
FROM lca.lcia_data ld
JOIN lca.impact_indicator ii ON ii.id = ld.impact_indicator_id
JOIN lca.impact_category ic ON ic.id = ii.impact_category_id
JOIN lca.impact_method im ON im.id = ii.impact_method_id
JOIN lca.lcia_database ldb ON ldb.id = ld.lcia_database_id
WHERE ii.name ILIKE '%GWP100%';
```

---

## Next Steps (Open)

- [ ] Determine why `lcia_data` is missing indicator `3c29b49e...` for EF-type descriptions
- [ ] Establish whether this is a **data import gap** or an **expected limitation** of the EF dataset (e.g. indicator only exists in CF datasets like IPCC 2021)
- [ ] If import gap: identify which import pipeline is dropping the rows and fix
- [ ] If dataset limitation: decide whether to surface a warning in the UI when indicators have partial coverage across exchanges

---

[[ADVISE LCA Platform]] | [[⚙️ LCA Engine — Context & Known Issues]] | [[🐛 Known Bugs — Priority Fixes]]