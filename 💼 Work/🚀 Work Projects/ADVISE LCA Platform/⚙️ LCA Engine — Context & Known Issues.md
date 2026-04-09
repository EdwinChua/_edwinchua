---

---
> Reference doc for `backend/api/app/services/test_calc.py` — the matrix-based LCA calculation engine.

## Overview

Implements **process-based LCA matrix algebra** per ISO 14040/14044. Given a product system, solves a linear system of process interdependencies and multiplies through emission/characterization factors to produce total environmental impacts per indicator.

Core equation:

```javascript
g = B × A⁻¹ × f
```

| Symbol | Description |
| --- | --- |
| `A` | Technology matrix (process system) |
| `B` | Emission factors (flows × indicators) |
| `f` | Functional unit demand vector |
| `g` | Total impact per indicator |

---

## Data Inputs

Four inputs fetched from DB and passed via the `event` dict:

| Input | Description |
| --- | --- |
| `ios_data` | All INPUT/OUTPUT flows with emission/CF factor amounts per indicator |
| `intermediates` | Intermediate/byproduct flows with `process_links` |
| `functional_unit` | Declared reference flow: `{ functional_unit, functional_unit_quantity, functional_unit_unit }` |
| `indicators` | List of distinct impact indicator IDs referenced by the product |

---

## Calculation Steps

### Step 1: `UserInputDB` — Build Data Tensors

Converts DB rows into NumPy globals used by all subsequent matrix functions.

- `**user_io**` — shape `(n_flows, 2 + n_indicators)`: col 0 = flow quantity (negative for INPUTs, positive for OUTPUTs); col 1 = `process_id`; cols 2+ = emission/CF factor per indicator. `INPUT + Characterization` → indicator values negated. Unit conversion applied to cols 2+ only.
- `**user_intermediate_from**` — shape `(n_intermediates, 3)`: `[quantity, from_process_id, io_id]`, sorted by `process_id`
- `**user_intermediate_to**` — shape `(n_links, 5)`: `[quantity, from_process_id, -consumed_qty, to_process_id, io_id]`, sorted by `process_id`
- `**functional_unit**` — shape `(n_intermediates + n_ios, 1)`: all zeros except one entry at position `y` (the declared FU intermediate)

### Step 2: `PrimaryMatrix` — Technosphere Matrix

Shape `(n_intermediates, n_processes)`. Diagonal = output quantity per process; off-diagonal = negative consumption between processes. When a process has multiple co-products (`pri_rep_counter > 0`), rows outnumber columns — no longer square.

### Step 3: `SecondaryMatrix` — Flow-to-Process Mapping

Shape `(n_ios, n_processes)`. Maps each INPUT/OUTPUT flow to its process column. At most one non-zero entry per row.

### Step 4: `ExpandedMatrix` — Sign Correction Block

Shape `(n_intermediates + n_ios, n_ios)`. Diagonal: `+1` if input flow, `-1` if output/emission flow.

### Step 5: `TechnologyMatrix` — Full System Matrix

```javascript
TechnologyMatrix = hstack(
    vstack(PrimaryMatrix, SecondaryMatrix),   # process columns
    vstack(zeros, ExpandedMatrix)             # flow columns
)
```

Shape: `(n_intermediates + n_ios, n_processes + n_ios)`

### Step 6: `InterventionMatrix` — Core Solve

```python
inverse_matrix = np.linalg.inv(technology_matrix)  # or pinv if non-square
scaling_factor = (inverse_matrix @ functional_unit)[primary_matrix_shape[1]:, :]
intervention_matrix = emission_factors * scaling_factor
total_intervention_matrix = emission_factors.T @ scaling_factor
```

### Step 7: `format_lca_response` — Structure Output

```python
{
  "<indicator_id>": {
    "total_emissions": float,
    "io_breakdown": { "<io_id>": { name, stage, process, quantity, unit, amount, percent } },
    "process_breakdown": { "<process_id>": { stage, process, total_amount, percent } }
  }
}
```

---

## ⚠️ Known Bugs

### Bug 1 — Unit Conversion Applied to EFs but NOT Flow Quantities

**File:** `test_calc.py:750-751` | **Severity:** High

`col 0` (flow quantity, used in `SecondaryMatrix`) is never converted. `cols 2+` (emission factors) are converted. If a flow is declared in kg but its EF is per tonne, EF gets scaled but the quantity driving the secondary matrix does not — results will be wrong for those flows.

**Triggered when:** any flow has a non-1:1 unit conversion setting.

---

### Bug 2 — Abatement Inputs May Be Double-Negated

**File:** `test_calc.py:674-710` | **Severity:** High

For `INPUT + Characterization` flows: indicator values negated at line 684 AND col 0 quantity negated at line 708. The scaling factor for an input ends up positive; multiplied by already-negated EF → abatement **appears as positive impact** rather than a reduction.

**Triggered when:** any INPUT flow has `lcia_type = Characterization`.

---

### Bug 3 — Wrong Scaling Factor Slice for Multi-Output Processes

**File:** `test_calc.py:1036-1040` | **Severity:** High

```python
scalling_factor = np.matmul(inverse_matrix, functional_unit)[primary_matrix_shape[1]:, :]
```

When `pri_rep_counter > 0`, `functional_unit` vector is oversized relative to what the pseudo-inverse expects, which can cause demand to be placed at an incorrect row position.

**Triggered when:** any process has 2+ intermediate outputs. Needs validation with a concrete multi-output example.

---

### Bug 4 — Functional Unit Position Ambiguous for Multi-Output Processes

**File:** `test_calc.py:810-820` | **Severity:** High

`y` is found as the **first row** in `user_intermediate_from` where `process_id` matches. For multi-output processes, there are multiple rows with the same `process_id` — code always picks the first regardless of which output is the declared FU. Also: if no intermediate's `io_id` matches the FU → `UnboundLocalError` crash.

**Triggered when:** functional unit's process has multiple intermediate outputs.

---

### Bug 5 — `lambda_handler` Error Response Is Truthy

**File:** `LCA_calculation_service.py:99-105` | **Severity:** Medium

```python
calculation_response = await run_in_threadpool(lambda_handler, event, context)
if not calculation_response:   # ← never catches engine errors
    raise HTTPException(...)
```

On internal error, `lambda_handler` returns `{ "statusCode": 500, "body": "..." }` — truthy. Guard passes, next line throws `KeyError` on `breakdowns` instead of a clean HTTP 500.

---

## 🚨 Global State Warning (Thread Safety)

`UserInputDB` writes to **module-level globals**: `user_io`, `user_intermediate_from`, `user_intermediate_to`, `functional_unit`. All subsequent matrix functions read these globals.

- Functions are **not thread-safe** — concurrent requests will corrupt each other's state
- Globals persist between calls if a request fails mid-way
- `run_in_threadpool` runs `lambda_handler` in a thread — concurrent requests sharing these globals is the most serious architectural risk

---

## Monte Carlo Path (`distance_calc`)

Runs `N` simulations (default 5000 — `num_sims` parameter is ignored, hardcoded at line 1189). For each flow, samples a lognormal distribution from pedigree matrix scores:

- Pedigree score → uncertainty factor via `pedigree_matrix_conversion` table
- GSD = `exp(sqrt(Σ log(u_i)²))`
- `sigma = log(GSD)`, `mu = log(mean) - sigma²/2`
- Draws N samples, rebuilds and re-solves technology matrix for each

**Note:** if `mean <= 0`, `log(mean)` produces NaN/inf → silent bad results.

---

## Related Files

| File | Role |
| --- | --- |
| `services/test_calc.py` | This engine — `lambda_handler`, `distance_calc`, all matrix builders |
| `services/LCA_calculation_service.py` | Orchestration layer — calls engine, persists results |
| `claude-docs/lca-calculation/lca_calculation_service_context.md` | Orchestration layer context doc |