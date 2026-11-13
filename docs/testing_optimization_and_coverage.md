# Test Suite Optimization and Coverage Review

**Project:** Student Course Registration System  
**Assignment:** SE3002 Software Quality Engineering — Assignment 2  
**Scope:** Part A5 (exact-duplicate optimization) and Part B2 (before/after structural coverage)  
**Implementation status:** `registration.py` was not modified for this review.

## 1. Design inventory and test traceability

The black-box case spreadsheets and their executable pytest mapping contain:

| Technique | Design IDs | Designed cases | Executable location |
|---|---|---:|---|
| Equivalence Class Partitioning | `ECP-01`–`ECP-20` | 20 | `tests/test_blackbox.py` |
| Boundary Value Analysis | `BVA-01`–`BVA-25` | 25 | `tests/test_blackbox.py` |
| Decision Table | `DT-01`–`DT-10` | 10 | `tests/test_blackbox.py` |
| Additional registration/withdrawal state checks | `STATE-01`–`STATE-09` | 9 | `tests/test_blackbox.py` |
| **Total black-box executions** | | **64** | |

The repository now uses the assignment's required `tests/` directory consistently. Historical evidence files retain the paths that were current when those runs were captured.

## 2. A5 — Exact-duplicate analysis

**Duplicate criterion:** Two cases are exact duplicates only when they exercise the **same operation**, with the **same complete pre-state and concrete input values**, and require the **same result/exception and state-change assertions**. Sharing an SRS requirement or expected status is insufficient.

The 20 ECP, 25 BVA, and 10 decision-table cases were compared against this criterion using their workbook representative inputs and the pytest fixtures. No exact cross-technique duplicate scenarios were identified. The meaningful overlaps below remain separate because their actual inputs or additional decision conditions differ.

| Similar cases | Shared testing idea | Why they are **not exact duplicates** |
|---|---|---|
| `ECP-07`, `BVA-24`, `DT-10` | Eligible registration | Different current/course credits, enrollment, capacity, or prerequisite setup. |
| `ECP-08`, `BVA-25`, `DT-01` | Positive dues block registration | ECP uses Rs. 50; BVA uses Rs. 1 near the boundary; decision-table case uses Rs. 1 with additional completed-prerequisite and credit setup. |
| `ECP-15`, `BVA-17`, `BVA-19`, `DT-09` | Full course returns `WAITLISTED` | Different capacity, enrollment, credits, or prerequisite setup; DT-09 also checks priority interactions. |
| `ECP-17`, `BVA-20` | Invalid enrollment exceeds capacity | `7 > 5` versus `31 > 30`; different invalid values. |
| `ECP-13`, `DT-05` | Missing prerequisites | Different prerequisite sets and registration preconditions. |

**Optimization decision:** Exact duplicate count = **0**; cases removed = **0**; all **55** design cases retained with their original IDs. Parametrized pytest groups keep code compact while preserving independently visible test IDs and technique traceability. Do not merge cases solely because both return `REGISTERED`, `WAITLISTED`, `DUES_BLOCK`, or `ValueError`.

## 3. B2 — Coverage baseline and white-box improvement

The following measurements were reproduced on **the same environment** (Linux, Python 3.12.14, pytest 9.2.0, pytest-cov 7.1.0) to permit a fair comparison. Both runs used `--cov=registration --cov-branch` on the unchanged starter implementation.

| Measure | Black-box only (initial) | Black-box + white-box (after additions) | Change |
|---|---:|---:|---:|
| Tests collected | 64 | 75 | +11 |
| Passed / failed | 49 / 15 | 58 / 17 | 9 added passes; 2 added legitimate failures |
| Statements executed | 54 / 57 | 55 / 57 | +1 statement |
| **Statement coverage** | **94.74%** | **96.49%** | **+1.75 points** |
| Branch arcs executed | 23 / 26 | 24 / 26 | +1 branch arc |
| **Branch coverage** | **88.46%** | **92.31%** | **+3.85 points** |
| Combined `pytest-cov` coverage | 77 / 83 = **92.77%** (displayed 93%) | 79 / 83 = **95.18%** (displayed 95%) | **+2.41 points** |

The earlier saved initial run on **Windows / Python 3.14.6** displayed **92% combined coverage** with 53 measured statements. Because Python/coverage instrumentation differs, do **not** directly compare that Windows percentage with the Linux final percentage as if it were the same measurement environment. Retain the original Windows evidence and also use the paired Linux runs above.

### 3.1 Missing lines and branch arcs

| Stage | Missing statements | Missing branch arcs |
|---|---|---|
| Initial black-box run | `51, 59, 71` | `50 → 51`, `58 → 59`, `70 → 71` |
| After white-box tests | `59, 71` | `58 → 59`, `70 → 71` |

- **Line 51:** `DUES_BLOCK` becomes covered through `WB-CC-06` (dues = Rs. 1500), targeting the supplied-code `dues > 1000` branch. The SRS independently requires blocking **any** positive dues (FR-04).
- **Line 59:** `WAITLISTED` remains unreachable. The earlier capacity validation rejects enrollment above capacity, while the later waitlist decision checks `enrolled > capacity` instead of handling the SRS-defined `enrolled == capacity` case (FR-08).
- **Line 71:** The waitlist append in `register_course` remains unreachable for ordinary inputs because `registration_decision` never returns `WAITLISTED` in the supplied implementation (FR-12).

Full 100% branch coverage is not attainable without correcting the confirmed control-flow defect. Do not alter requirement-based tests to hide these gaps.

### 3.2 White-box additions that justify new execution

| ID | Structural target / purpose |
|---|---|
| `WB-CC-01` | D1 True, negative-dues validation and early raise. |
| `WB-CC-02` | All normal predicates False, common MC/DC baseline. |
| `WB-CC-03` | D2a/A True and later operands not evaluated. |
| `WB-CC-04` | D2a False, D2b/B True, D2c not evaluated. |
| `WB-CC-05` | D2a False, D2b False, D2c/C True. |
| `WB-CC-06` | D3 True and line 51: previously uncovered dues-block return. |
| `WB-CC-07` | D4 True: duplicate registration. |
| `WB-CC-08` | D5 True: missing prerequisite. |
| `WB-CC-09` | D6 True: credit limit. |
| `WB-CC-10` | D7 False even at full capacity: exposes FR-08 defect. |
| `WB-CC-11` | D3 False at positive Rs. 1: exposes FR-04 defect. |

The four unique cases `WB-CC-02`–`WB-CC-05` demonstrate all three independent effects for the selected compound validation decision (manual masking MC/DC: 3/3). **`pytest-cov` does not measure MC/DC directly.** Refer to `docs/White-Box-Testing.docx` for the truth tables and pair rationale.

## 4. Evidence and defect integrity

- `docs/evidence/blackbox-initial.txt` — original black-box failure evidence.
- `docs/evidence/blackbox-baseline-linux.txt` — comparable initial Linux coverage run (49 passed, 15 failed).
- `docs/evidence/whitebox-initial.txt` — white-box run (9 passed, 2 failed).
- `docs/evidence/whitebox-combined-coverage.txt` — combined Linux run (58 passed, 17 failed).

The additional two white-box failures are **new failed test IDs for already known defect types**, not automatically two new unique defects. Specifically, `WB-CC-10` demonstrates the full-course availability bug, and `WB-CC-11` demonstrates the any-positive-dues bug. Maintain the relevant GitHub Issues and keep initial failure evidence before making changes on a future `defect-fixes` branch.

## 5. Pull request review checklist

- [ ] The new documentation is committed to `testing-documentation`, not directly to `main`.
- [ ] The PR explains A5 optimization and the **separate** statement/branch percentages.
- [ ] Existing defect Issues are linked in the PR description, without claiming the implementation was fixed.
- [ ] A different team member reviews the PR, leaves substantive feedback, and the author responds.
- [ ] Evidence and expected-failure records remain available after review.

