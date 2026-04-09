---
tags: [lca, work, bugs]
---
> Bugs identified in `test_calc.py` (LCA engine) and `LCA_calculation_service.py`. Bugs 3 & 4 interact with each other and should be tackled together.

## Summary

| # | Bug | File | Severity | Trigger |
| --- | --- | --- | --- | --- |
| 1 | Unit conversion applied to EFs but not flow quantities | `test_calc.py:750-751` | 🔴 High | Any flow with non-1:1 unit conversion |
| 2 | Abatement inputs may be double-negated | `test_calc.py:674-710` | 🔴 High | Any INPUT with `lcia_type = Characterization` |
| 3 | Wrong scaling factor slice for multi-output processes | `test_calc.py:1036-1040` | 🔴 High | Any process with 2+ intermediate outputs |
| 4 | Functional unit position ambiguous for multi-output processes | `test_calc.py:810-820` | 🔴 High | FU process has multiple intermediate outputs |
| 5 | `lambda_handler` error response is truthy | `LCA_calculation_service.py:99-105` | 🟡 Medium | Any internal engine error |
| — | Global state / thread safety | `test_calc.py` (module globals) | 🔴 Critical | Concurrent requests |

---

## Bug 1 — Unit Conversion Applied to EFs but NOT Flow Quantities

**File:** `test_calc.py:750-751` | **Severity:** 🔴 High

```python
conversion_factor = (conversion_numerator / conversion_denominator).reshape((-1, 1))
user_io[:, 2:] = np.multiply(user_io[:, 2:].astype(np.float64), conversion_factor)
```

**Problem:** `col 0` (flow quantity, used to populate `SecondaryMatrix`) is never converted. `cols 2+` (emission factors) are converted. If a flow is declared in kg but its EF is per tonne, the EF gets scaled but the quantity driving the secondary matrix does not — they end up on different scales and results will be wrong for those flows.

**Fix direction:** Apply the same conversion factor to `col 0` as well, or ensure unit normalisation happens before the tensor is split.

---

## Bug 2 — Abatement Inputs May Be Double-Negated

**File:** `test_calc.py:674-710` | **Severity:** 🔴 High

**Problem:** For `INPUT + Characterization` (abatement) flows, two independent negations are applied:

- **Line 684:** indicator values negated: `-indicators["quantity"]`
- **Line 708:** col 0 quantity negated: `quantity = -ios_loop["quantity"]`

The scaling factor for an input (negative in secondary matrix, sign-flipped by `ExpandedMatrix`) ends up positive. Multiplied by the already-negated EF → abatement **appears as a positive impact** instead of a reduction.

**Fix direction:** Audit the sign chain through `ExpandedMatrix` and determine which single negation point is correct. The two negations do not cleanly cancel through the matrix solve.

---

## Bugs 3 & 4 — Multi-Output Process Issues ⚠️ Fix Together

These two bugs interact. Bug 4 places the functional unit demand at the wrong row; Bug 3 then slices the solve result incorrectly. Both must be fixed together with a concrete multi-output test case.

### Bug 3 — Wrong Scaling Factor Slice

**File:** `test_calc.py:1036-1040` | **Severity:** 🔴 High

```python
scalling_factor = np.matmul(inverse_matrix, functional_unit)[primary_matrix_shape[1]:, :]
```

**Problem:** When `pri_rep_counter > 0` (multi-output process):

- `PrimaryMatrix.shape[0]` = `n_intermediates` (rows)
- `PrimaryMatrix.shape[1]` = `n_processes` = `n_intermediates - pri_rep_counter` (cols, fewer)

The `functional_unit` vector has size `n_intermediates + n_ios` (row space of A), but is oversized relative to what the pseudo-inverse expects. This can cause demand to be placed at an incorrect row position.

**Needs:** Validation with a concrete multi-output example to confirm exact failure mode.

### Bug 4 — Functional Unit Position Ambiguous

**File:** `test_calc.py:810-820` | **Severity:** 🔴 High

```python
for intermediate_loop in intermediates:
    if str(intermediate_loop["io_id"]) == str(functional_unit_idex):
        y = 0
        for x in user_intermediate_from[:, 1]:
            if x == intermediate_loop["process_id"]:
                break
            y += 1
functional_unit[y, 0] = raw_functional_unit["functional_unit_quantity"]
```

**Problem:** `y` is found as the **first row** in `user_intermediate_from` where `process_id` matches. For a multi-output process, multiple rows share the same `process_id` — the code always picks the first regardless of which specific output is the declared functional unit. Demand vector is placed at the wrong row.

**Secondary problem:** If no intermediate's `io_id` matches the functional unit (e.g. misconfigured product), `y` is never assigned → `UnboundLocalError` crash.

**Fix direction:** Match on `io_id` directly to find the correct row, rather than matching on `process_id`. Add a guard for the unbound case.

---

## Bug 5 — `lambda_handler` Error Response Is Truthy

**File:** `LCA_calculation_service.py:99-105` | **Severity:** 🟡 Medium

```python
calculation_response = await run_in_threadpool(lambda_handler, event, context)
if not calculation_response:   # ← never catches engine errors
    raise HTTPException(...)
```

**Problem:** On internal error, `lambda_handler` returns `{ "statusCode": 500, "body": "..." }` — a non-empty dict, which is truthy. The guard passes, and the next line `breakdowns = calculation_response["breakdowns"]` throws a `KeyError` instead of a clean HTTP 500.

**Fix direction:** Check `calculation_response.get("statusCode") == 200` or check for the presence of `"breakdowns"` key explicitly.

---

## 🚨 Global State / Thread Safety

**File:** `test_calc.py` (module-level globals) | **Severity:** 🔴 Critical architectural risk

`UserInputDB` writes to module-level globals: `user_io`, `user_intermediate_from`, `user_intermediate_to`, `functional_unit`. All matrix functions read these globals rather than receiving them as arguments.

**Consequences:**

- Functions are **not thread-safe** — concurrent calculation requests will corrupt each other's state
- Globals persist between calls if a request fails mid-way, potentially poisoning the next request
- `run_in_threadpool` runs `lambda_handler` in a thread — concurrent requests sharing globals is the most serious risk under any real load

**Fix direction:** Refactor `UserInputDB` to return a state object (dataclass or namedtuple), and thread that object through all matrix builder functions as an explicit argument rather than relying on module globals.

---

[[ADVISE LCA Platform]] | [[⚙️ LCA Engine — Context & Known Issues]] | [[🔍 Zero Emission Investigation]]