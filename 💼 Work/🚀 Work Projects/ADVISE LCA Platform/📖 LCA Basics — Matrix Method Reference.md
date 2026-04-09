---

---
> Background reference: what LCA is and how the matrix method works. Source: `lca_calculation_basic_context.md`

## What is LCA?

[[Life Cycle Assessment (LCA)]] is a systematic method for evaluating the environmental impacts of a product, process, or service across its entire life cycle — from raw material extraction through production, use, and end-of-life disposal ("cradle to grave"). Standardised under **ISO 14040** and **ISO 14044**.

---

## The Four Phases (ISO 14040)

1. **Goal and Scope Definition** — purpose, system boundary, functional unit
2. **Life Cycle Inventory (LCI)** — compile all inputs and outputs (energy, materials, emissions)
3. **Life Cycle Impact Assessment (LCIA)** — translate inventory into environmental impact categories
4. **Interpretation** — analyse results, identify hotspots, draw conclusions

---

## The Matrix Method

| Symbol | Name | Description |
| --- | --- | --- |
| **A** | Technology matrix | Processes × flows; net output of each flow per process |
| **f** | Final demand vector | Functional unit as required net outputs |
| **s** | Scaling vector | How much each process must run |
| **B** | Inventory matrix | Elementary flows per unit of each process |
| **g** | Inventory result | Total elementary flows for the functional unit |
| **Q** | Characterisation matrix | Converts elementary flows into impact scores |
| **h** | Impact result | Final environmental impact scores |

**Sign convention for A:** positive = output of process, negative = input to process.

### Calculation Chain

```javascript
f  →  s = A⁻¹ · f  →  g = B · s  →  h = Q · g
```

Full expression: `h = Q · B · A⁻¹ · f`

---

## Worked Example (2 Processes)

**Scenario:** Produce 1 kg of Product A. Process 1 makes A but requires B. Process 2 makes B but requires A.

**Technology matrix A:**

```javascript
         Process 1   Process 2
Product A [  1.0        -0.2  ]
Product B [ -0.5         1.0  ]
```

**Functional unit:** `f = [1, 0]ᵀ` (1 unit of A, zero net B)

**Solve:**

```javascript
det(A) = 0.9
A⁻¹ = (1/0.9) · [[1.0, 0.2], [0.5, 1.0]]
s = [1.11, 0.56]ᵀ
```

**Inventory** (2 kg CO₂/unit for P1, 1 kg CO₂/unit for P2):

```javascript
g_CO₂ = (2 × 1.11) + (1 × 0.56) = 2.78 kg CO₂
```

---

## Common Impact Categories

| Category | Unit | Key Flows |
| --- | --- | --- |
| Global Warming Potential (GWP) | kg CO₂-eq | CO₂, CH₄, N₂O |
| Acidification | kg SO₂-eq | SO₂, NOₓ, NH₃ |
| Eutrophication | kg PO₄-eq | Phosphates, nitrates |
| Ozone Depletion | kg CFC-11-eq | CFCs, HCFCs |
| Photochemical Oxidant Formation | kg NMVOC-eq | VOCs, NOₓ |
| Water Scarcity | m³ world-eq | Water withdrawals |
| Abiotic Resource Depletion | kg Sb-eq | Minerals, fossil fuels |

---

## Key Concepts

**Functional Unit** — The quantified performance reference for all calculations. E.g. "1 kg of packaged drinking water delivered to consumer".

**System Boundary** — Which processes are included:

- Cradle-to-gate — extraction through production
- Cradle-to-grave — full life cycle including end-of-life
- Gate-to-gate — single facility or process only

**Multi-Output Processes** — When a process has co-products, impacts must be allocated via system expansion, physical allocation (mass/volume/energy), or economic allocation.

**Foreground vs Background** — Foreground = processes directly under study's control; Background = upstream/downstream from generic databases (e.g. ecoinvent).

---

## Relevant Tools & Databases

| Tool | Notes |
| --- | --- |
| Brightway2 | Open source Python — exposes matrices directly, most relevant to our stack |
| openLCA | Open source, full-featured, database-agnostic |
| SimaPro | Industry standard commercial tool |
| ecoinvent | Most widely used background LCI database |
| ELCD / GaBi | European process data |