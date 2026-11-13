# SE3002 Assignment 2 — Student Course Registration Testing

Black-box and white-box testing project for the supplied **Student Course Registration System**.

- **Repository:** https://github.com/Maaz976/Python-Registration-Testing
- **System under test:** `registration.py`
- **Requirements / oracle:** `REQUIREMENTS.md` and `Student_Registration_SRS.docx`
- **Final result:** **80 passed, 0 failed · 100% statement and branch coverage**

## Project structure

```text
.
├── registration.py
├── requirements.txt
├── README.md
├── REQUIREMENTS.md
├── pytest.ini
├── tests/
│   ├── test_blackbox.py
│   └── test_whitebox.py
├── docs/
│   ├── blackbox_test_design.xlsx
│   ├── decision_table.xlsx
│   ├── cfg.png
│   ├── testing_report.pdf
│   ├── White-Box-Testing.docx
│   ├── testing_optimization_and_coverage.md
│   └── evidence/
└── .github/workflows/tests.yml
```

## Setup and test execution

```bash
python -m pip install -r requirements.txt

# Full suite
python -m pytest -v

# Technique-specific suites
python -m pytest tests/test_blackbox.py -v
python -m pytest tests/test_whitebox.py -v

# Statement and branch coverage
python -m pytest tests/ --cov=registration --cov-branch --cov-report=term-missing
```

## Deliverables

| Part | Deliverable | Location |
|---|---|---|
| A1–A2 | ECP (20 cases) and BVA (25 cases) design workbooks | `docs/blackbox_test_design.xlsx` |
| A3 | Decision table and 10 executable decision-table cases | `docs/decision_table.xlsx` |
| A4 | Black-box pytest suite | `tests/test_blackbox.py` |
| A5 | Duplicate analysis and optimisation | `docs/testing_optimization_and_coverage.md` |
| B1 | CFG, V(G) = 10, 10 basis paths | `docs/cfg.png`, `docs/White-Box-Testing.docx` |
| B2 | Statement/branch coverage before and after | `docs/testing_optimization_and_coverage.md` |
| B3 | Condition coverage and MC/DC analysis | `docs/White-Box-Testing.docx` |
| B4 | White-box and regression pytest suite | `tests/test_whitebox.py` |
| D | Final testing report | `docs/testing_report.pdf` |

## Results

| Stage | Tests | Result |
|---|---:|---|
| Initial black-box baseline | 64 | 49 passed, 15 legitimate defect failures |
| Black-box + white-box (pre-fix) | 75 | 58 passed, 17 failures |
| Post-fix regression | 80 | **80 passed, 0 failed** |

Coverage moved from **94.74% statement / 88.46% branch** initially to **100% / 100%** after the defect fixes and regression additions.

## Defects and pull requests

| Issue | Defect | Status |
|---|---|---|
| [#1](https://github.com/Maaz976/Python-Registration-Testing/issues/1) | Exactly 18 credits rejected (FR-01) | Fixed on `defect-fixes`, open pending review |
| [#2](https://github.com/Maaz976/Python-Registration-Testing/issues/2) | Positive dues do not block registration (FR-04) | Fixed on `defect-fixes`, open pending review |
| [#3](https://github.com/Maaz976/Python-Registration-Testing/issues/3) | Partial prerequisites accepted (FR-03, FR-06) | Fixed on `defect-fixes`, open pending review |
| [#4](https://github.com/Maaz976/Python-Registration-Testing/issues/4) | Full course registers instead of waitlisting (FR-08, FR-12) | Fixed on `defect-fixes`, open pending review |
| [#5](https://github.com/Maaz976/Python-Registration-Testing/issues/5) | Withdrawal does not decrement enrollment (FR-13) | Fixed on `defect-fixes`, open pending review |

- **PR #6:** https://github.com/Maaz976/Python-Registration-Testing/pull/6 — repository structure, pytest discovery, and real black-box baseline evidence.
- **PR #7:** https://github.com/Maaz976/Python-Registration-Testing/pull/7 — five defect fixes, regression cases, coverage evidence, and final report.

Both PRs are intentionally **open and unmerged** for review.

## Evidence

Pre-fix failures are preserved in `docs/evidence/`. The final post-fix regression output is in `docs/evidence/final-regression-coverage.txt`, and the GitHub Actions workflow uploads pytest/coverage artifacts on every push and pull request.

## Contributions

- **Muhammad Maaz (`Maaz976`)** — repository setup, black-box design workbook, initial evidence, CFG, white-box documentation, traceability matrix, defect issues.
- **Muhammad Muzammil Ayan (`MuhammadmuzammilAyan1`)** — black-box tests, white-box tests, coverage analysis, GitHub Actions workflow, optimisation review.
- **Pir Ahmed Shah (`PirAhmedShah`)** — baseline reproduction, structure cleanup, five defect fixes, regression cases, final 100% coverage evidence, PRs #6/#7, final testing report.
