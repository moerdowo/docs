# Coverage Report — API V2 Reference Documentation

- **Feature**: api-v2-reference-docs
- **Branch**: feat/api-v2-reference-docs
- **Phase**: 15 — coverage
- **Date**: 2026-06-29
- **Result**: ✅ PASS — full traceability, combined gate GREEN (15/15)

---

## 1. What "coverage" means for this feature

This is a **documentation corpus**, not runnable code — there is no line/branch
coverage to instrument (no application runtime, no in-repo test framework). The
applicable coverage metric is therefore **corpus + objective traceability**:

1. **Corpus coverage** — fraction of pages/endpoints exercised by ≥1 check.
2. **Objective coverage** — fraction of P0/P1/P2 risk objectives enforced by ≥1
   executable check.
3. **Gate pass rate** — fraction of checks currently green.

Threshold for this feature: **100% objective coverage** (no P0/P1/P2 objective
unprotected) **and** the combined gate GREEN. Both are met.

---

## 2. Corpus coverage (measured 2026-06-29)

| Unit | In tree | Exercised | Coverage |
|------|---------|-----------|----------|
| `.mdx` pages (`api-reference-v2/**`) | 74 | 74 (C2–C7, D1) | **100%** |
| Endpoint pages (`openapi:` frontmatter) | 71 | 71 (D2–D7) | **100%** |
| Embedded ```json blocks | 80 | 80 (C6) | **100%** |
| `docs.json` nav (tabs[2] + tabs[1] regression) | 1 | 1 (C1, C2, C8) | **100%** |

Counts re-verified against the working tree this phase (`find … -name '*.mdx'`
→ 74; `grep -rl '^openapi:'` → 71) and match what both suites report. No page or
endpoint is outside the reach of a check.

---

## 3. Objective coverage (traceability)

Every P0/P1/P2 objective from test-plan §2 maps to ≥1 executable check. No
objective is unprotected.

| Pri | Objective | Enforced by | Status |
|-----|-----------|-------------|--------|
| P0 | No internal-identifier leak | C7 | ✅ green |
| P0 | No V1 content drift | C8 | ✅ green |
| P0 | Site builds / renders | C1, C4, C5, C6 | ✅ green |
| P1 | Base-URL fidelity (prod+sandbox, no /hl/v1) | D1 | ✅ green |
| P1 | Envelope quirk (`statusCode` + message^messages) | D5 | ✅ green |
| P1 | Nav integrity (1:1, no orphan/missing) | C2 | ✅ green |
| P2 | Endpoint contract complete | D2, D3, D4, D6 | ✅ green |
| P2 | Frontmatter / authoring hygiene | C3, D7 | ✅ green |

**Objective coverage: 8/8 (100%).** The C4↔D7 pairing (known-tag balance vs
unknown stray-tag detection — the gap that hid bug-001) is intact and must be
preserved.

---

## 4. Gate pass rate (re-run this phase)

```
### Structural suite (C1-C8) ###  RESULT: PASS (8/8)
### Domain-compliance suite (D1-D7) ###  RESULT: PASS (7/7)
GATE: PASS (structural 8/8 + domain 7/7)   exit 0
```

**Check pass rate: 15/15 (100%).** Combined entrypoint
(`validate-v2-docs.sh`) exit 0 — confirmed re-run from repo root this phase, no
check logic altered.

---

## 5. Coverage gaps (carried forward, non-gating)

No **objective** is uncovered. The following are coverage-*depth* limits already
recorded in test-plan §6 — none gate the feature:

| ID | Coverage limit | Status |
|----|----------------|--------|
| G2 | No CI re-runs the gate on future edits | Deferred (R2) — non-gating |
| G3 | Value-level semantic fidelity not auto-asserted (shape only) | Accepted — manual prod-capture |
| G4 | No link-integrity / heading-consistency check | Deferred (R3) — non-gating |
| G5 | No real `mint build` (static lint is the proxy) | Accepted — no build tooling in-repo |
| bug-002 | Upstream reviews-stats 500 — pages flagged REPRESENTATIVE | Open, non-gating |

---

## 6. Verdict

- Corpus coverage: **100%** (74/74 pages, 71/71 endpoints, 80/80 json blocks).
- Objective coverage: **100%** (8/8 P0/P1/P2 objectives enforced).
- Gate pass rate: **15/15**, combined entrypoint exit 0.

**Coverage threshold met. Phase 15 PASS.**
