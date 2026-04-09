---

---
> Reference doc for `backend/api/app/services/test_calc.py` — the matrix-based LCA calculation engine.

## Overview

Implements **process-based [[LCA]] matrix algebra** per ISO 14040/14044. Given a product system, solves a linear system of process interdependencies and multiplies through emission/characterization factors to produce total environmental impacts per indicator.

Core equation:

```javascript
g = B × A⁻¹ × f
```

| Symbol | Role |
| --- | --- |
| `A` | Technology matrix (process system) |
| `B` | Emission factors (flows × indicators) |
| `f` | Functional unit demand vector |
| `g` | Total impact per indicator |

---

## Data Inputs (via `event` dict)

| Input | Description |
| --- | --- |
| `ios_data` | All INPUT/OUTPUT flows with emission/CF factor amounts per indicator |
| `intermediates` | Intermediate/byproduct flows with `process_links` |
| `functional_unit` | Declared reference flow: `{ io_id, quantity, unit }` |
| `indicators` | List of distinct impact indicator IDs referenced by the product |

---

## Calculation Steps

### Step 1 — `UserInputDB`: Build Data Tensors

Converts DB rows into NumPy globals used by all subsequent matrix functions.

- `**user_io**` — shape `(n_flows, 2 + n_indicators)`: col 0 = signed flow qty, col 1 = process_id, cols 2+ = EF per indicator. `INPUT + Characterization` → EF values negated. Unit conversion applied to cols 2+ only.
- `**user_intermediate_from**` — shape `(n_intermediates, 3)`: `[qty, from_process_id, io_id]`
- `**user_intermediate_to**` — shape `(n_links, 5)`: `[qty, from_process_id, -consumed_qty, to_process_id, io_id]`
- `**functional_unit**` — shape `(n_intermediates + n_ios, 1)`: all zeros except declared FU quantity

### Step 2 — `PrimaryMatrix`: Technosphere Matrix

Shape `(n_intermediates, n_processes)`. Diagonal = output qty per process; off-diagonal = negative consumption between processes. When a process has co-products (`pri_rep_counter > 0`), rows outnumber columns — matrix is non-square.

### Step 3 — `SecondaryMatrix`: Flow-to-Process Mapping

Shape `(n_ios, n_processes)`. Maps each INPUT/OUTPUT flow to its process column via signed quantity and process_id.

### Step 4 — `ExpandedMatrix`: Sign Correction Block

Shape `(n_intermediates + n_ios, n_ios)`. Diagonal: `+1` if input flow, `-1` if output/emission flow.

### Step 5 — `TechnologyMatrix`: Full System Matrix

```javascript
TechnologyMatrix = hstack(
    vstack(PrimaryMatrix, SecondaryMatrix),
    vstack(zeros, ExpandedMatrix)
)
```

Shape: `(n_intermediates + n_ios, n_processes + n_ios)`

### Step 6 — `InterventionMatrix`: Core Solve

```python
inverse_matrix = np.linalg.inv(technology_matrix)  # or pinv if non-square
scaling_factor = (inverse_matrix @ functional_unit)[primary_matrix_shape[1]:, :]
intervention_matrix = emission_factors * scaling_factor
total_intervention_matrix = emission_factors.T @ scaling_factor
```

### Step 7 — `format_lca_response`: Structure Output

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

## 🐛 Known Bugs

### Bug 1 — Unit Conversion Not Applied to Flow Quantities ⚠️

**File:** `test_calc.py:750-751`

Unit conversion is applied to EF columns (cols 2+) but **not** to col 0 (flow quantity used in SecondaryMatrix). If a flow is declared in kg but its EF is per tonne, the secondary matrix and EF columns are on different scales → wrong results.

**Triggered when:** any flow has a non-1:1 unit conversion.

---

### Bug 2 — Abatement Inputs May Be Double-Negated ⚠️

**File:** `test_calc.py:674-710`

For `INPUT + Characterization` flows: EF values are negated at line 684, AND col 0 quantity is negated at line 708. The two independent negations don't obviously cancel through the matrix solve — abatement may appear as a **positive** impact rather than a reduction.

**Triggered when:** any INPUT flow has `lcia_type = Characterization`.

---

### Bug 3 — Wrong Scaling Factor Slice for Multi-Output Processes ⚠️⚠️

**File:** `test_calc.py:1036-1040`

```python
scalling_factor = np.matmul(inverse_matrix, functional_unit)[primary_matrix_shape[1]:, :]
```

When `pri_rep_counter > 0`, `functional_unit` vector is sized to row-space of A (`n_intermediates + n_ios`) but pseudo-inverse operates in column-space (`n_processes + n_ios`). The demand may be placed at an incorrect row position.

**Triggered when:** any process has 2+ intermediate outputs. **Needs validation with a concrete multi-output example.**

---

### Bug 4 — Functional Unit Position Ambiguous for Multi-Output Processes ⚠️

**File:** `test_calc.py:810-820`

For a process with multiple co-products, multiple rows share the same `process_id` in `user_intermediate_from`. Code always picks the **first** row, which may not correspond to the declared functional unit output.

Additionally: if no intermediate's `io_id` matches the FU (misconfigured product) → `UnboundLocalError` crash.

**Triggered when:** FU process has multiple intermediate outputs.

---

### Bug 5 — `lambda_handler` Error Response Is Truthy

**File:** `LCA_calculation_service.py:99-105`

```python
if not calculation_response:  # never catches engine errors
    raise HTTPException(...)
```

On internal error, engine returns `{ "statusCode": 500, "body": "..." }` — truthy. Guard passes, next line throws `KeyError` on `calculation_response["breakdowns"]` instead of a clean HTTP 500.

---

## ⚠️ Global State Warning (Thread-Safety Risk)

`UserInputDB` writes to **module-level globals**: `user_io`, `user_intermediate_from`, `user_intermediate_to`, `functional_unit`. All matrix functions read these globals rather than receiving them as arguments.

- **Not thread-safe** — concurrent requests will corrupt each other's state
- Globals persist between calls if a request fails mid-way
- `run_in_threadpool` runs `lambda_handler` in a thread — two simultaneous requests share these globals

**Most serious architectural risk for concurrent load.**

---

## Monte Carlo Path (`distance_calc`)

Runs `N = 5000` simulations (hardcoded — `num_sims` parameter is ignored at line 1189). For each flow, samples a lognormal distribution from the pedigree matrix:

- Pedigree scores → uncertainty factors via `pedigree_matrix_conversion` table
- GSD = `exp(sqrt(Σ log(u_i)²))`
- `sigma = log(GSD)`, `mu = log(mean) - sigma²/2`
- Draws N samples from `lognormal(mu, sigma)`

Rebuilds and re-solves the full technology matrix for each sample. If `mean <= 0`, `log(mean)` produces NaN/inf → simulation silently produces bad results.

---

## Related Files

| File | Role |
| --- | --- |
| `services/test_calc.py` | This engine — `lambda_handler`, `distance_calc`, all matrix builders |
| `services/LCA_calculation_service.py` | Orchestration layer — calls engine, persists results |
| `claude-docs/lca-calculation/lca_calculation_service_context.md` | Orchestration layer context doc |