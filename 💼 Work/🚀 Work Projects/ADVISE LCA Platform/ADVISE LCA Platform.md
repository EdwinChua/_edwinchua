---
base: "[[🚀 Work Projects.base]]"
Priority: High
Last Edited: 2026-03-30T16:35:00
Status: Active
Goal: Build an LCA platform using DEXPI 2.0 Process Model as the data structure for modelling and computing life cycle assessments.
Created: 2026-03-30T16:33:00
Tags: [lca, work, project]
---
> **Status:** Active | **Scope:** DEXPI 2.0 Process Model only (no Plant model / P&IDs)

## Overview

LCA platform built on the DEXPI 2.0 Process Model (released Oct 2025) as the core data structure. Only the Process model is in scope — the Plant model (P&IDs, piping, instrumentation) is entirely excluded.

Source spec: [https://gitlab.com/dexpi/Specification](https://gitlab.com/dexpi/Specification)

---

## What We Use from DEXPI 2.0

| Concept | Used? | Notes |
| --- | --- | --- |
| `ProcessModel` | ✅ | Top-level container |
| `ProcessStep` | ✅ | Every unit process / activity |
| `Port` | ✅ | `MaterialPort` only |
| `ProcessConnection` / `Stream` | ✅ | With LCA `exchanges` extension |
| `QualifiedValue` | Partial | Simplified form |
| `Composition` | ❌ | Renamed to `stages` to avoid collision |
| `MaterialState`, `MaterialTemplate` | ❌ | Not used |
| `Core.Diagram` / graphical layer | ❌ | Not used |
| `HierarchyLevel` (BFD/PFD) | ❌ | Omitted — nesting used instead |

---

## Key Deviations from Spec

### 1. `ProcessStep.type` always `"ProcessStep"`

DEXPI requires concrete subtypes (e.g. `Pumping`, `Distilling`). We don't enforce this — LCA processes (agriculture, transport, waste) don't map cleanly to DEXPI's industrial taxonomy. **Known non-conformance, suppressed in validator.**

### 2. `HierarchyLevel` omitted

LCA hierarchy is expressed through `SubProcessSteps` nesting rather than the BFD/PFD two-level distinction. Field is `0..1` optional — fully compliant to omit.

### 3. `compositions` → `stages`

DEXPI uses `Compositions` for chemical composition arrays. We use `stages` as a top-level grouping concept for `ProcessStep` objects. **Always use **`**stages**`** in new data.** Viewer supports legacy `compositions` key for backward compat.

```json
{
  "stages": [
    { "id": "uuid", "name": "stage 1", "process_step_ids": ["uuid"] }
  ]
}
```

### 4. `Stream.exchanges` — LCA Extension (Option A)

Primary LCA-specific extension. Instead of DEXPI's typed `MassFlow`/`MoleFlow` properties, streams carry a heterogeneous `exchanges` array:

```json
"exchanges": [
  { "name": "Apples", "value": 3900.0, "unit": "kg" },
  { "name": "Transport, lorry", "value": 500.0, "unit": "tkm" },
  { "name": "Electricity", "value": 12.0, "unit": "kWh" }
]
```

- `name` = ecoinvent exchange name
- `unit` = free-form string (no enumeration constraint)
- When `exchanges` present, do **not** use legacy `mass_flow`

### 5. `QualifiedValue` simplified

We use `{ "value": 86.0, "unit": "kg" }`. Omitted: `scope`, `provenance`, `range`, `case`. Units are plain strings, not DEXPI typed enum refs.

### 6. Other non-conformances (all suppressed in validator)

- `Stream` missing `Identifier` — streams identified by UUID instead
- `source`/`target` carry denormalised `process_id` + `process_name` for convenience

---

## Non-Standard Fields

**On **`**ProcessStep**`**:** `comment`, `is_external`, `sampling_period`, `stage_id`, `stage_name`, `lcia_description_id`

**On **`**Port**`**:** `io_type` (`INPUT`/`OUTPUT`/`INTERMEDIATE`/`FINAL PRODUCT`), `exchange_name`, `category`

---

## JSON Schema (Top-level)

```json
{
  "lca_metadata": {
    "lcia_name": "...",
    "upr_exchange_name": "...",
    "description": "...",
    "lcia_type": "Product",
    "geography": "Singapore",
    "start_date": "2026-01-01",
    "end_date": "2027-01-01",
    "functional_unit_unit": "kg"
  },
  "model_uri": "https://data.dexpi.org/models/2.0.0/Process.xml",
  "stages": [],
  "process_steps": [],
  "process_connections": []
}
```

---

## Validator — Active Checks

| Check | Level |
| --- | --- |
| `compositions` key used for grouping | Error |
| Diagram positions in conceptual objects | Error |
| Duplicate port IDs | Error |
| Distance unit on `mass_flow` (if no `exchanges`) | Error |
| Distance unit on port `qualified_value` | Warning |
| UUID IDs (if targeting XML) | Info |

**Suppressed:** `ProcessStep.type` abstract, `Stream` missing identifier, `QualifiedValue` missing `scope`/`provenance`

---

## Topology Viewer

Standalone HTML file (`dexpi_topology_viewer.html`) renders any conformant JSON as an interactive block flow diagram.

- Steps grouped into colour-coded stage bands
- Ports as coloured dots (blue = In, teal = Out)
- Streams as bezier curves with arrow markers
- Flagged streams (unit mismatch) in amber dashed style
- Click any step/stream to inspect in Detail panel
- Validate tab shows all active issues
- If `exchanges` present → shows exchange names/values; falls back to `mass_flow` for legacy data

---

[[LCA]] | [[📖 LCA Basics — Matrix Method Reference]] | [[⚙️ LCA Engine — Context & Known Issues]] | [[🐛 Known Bugs — Priority Fixes]] | [[🔍 Zero Emission Investigation]]