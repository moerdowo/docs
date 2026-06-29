# Test Plan — API V2 Reference Documentation

- **Feature**: api-v2-reference-docs
- **Branch**: feat/api-v2-reference-docs
- **Phase**: 13 — test-planning
- **Author**: test-lead
- **Date**: 2026-06-29
- **Status**: APPROVED — strategy validated, both suites currently GREEN

---

## 1. What "testing" means for this feature

This is a **documentation corpus**, not runnable code: 74 Mintlify `.mdx` pages
(71 endpoint pages + 3 overview pages: introduction / statuscode / rate-limit)
plus the `docs.json` navigation tree. There is no application runtime, no unit-
under-test, and no in-repo test framework (`test command: echo 'no test command
configured'`).

Therefore the test strategy is **static validation as test**: deterministic,
machine-checkable invariants that a published API reference must hold. These
invariants fall in two layers, each already implemented as an executable suite
(both authored in earlier phases, both exit-code gated):

| Layer | Suite | Checks | Question it answers |
|-------|-------|--------|---------------------|
| **Structural** | `validate-v2-docs.py` | C1–C8 (8) | Does it parse, render, and wire into nav without leaking internals? |
| **Domain** | `domain-compliance-v2-docs.py` | D1–D7 (7) | Does every endpoint page follow the REST-reference contract (base URL, method, auth, request/response envelope, field docs)? |

**Total: 15 checks** over 74 pages. Both are pure-Python, stdlib-only, no
network, deterministic, runnable from repo root. Together they are the test
suite for this feature.

---

## 2. Test objectives & risk-based priorities

Derived from `plan.md` Risks + Key Decisions. Each objective maps to the
check(s) that enforce it (full matrix in §4).

| Pri | Objective (risk being controlled) | Enforced by |
|-----|-----------------------------------|-------------|
| P0 | **No internal-identifier leak** (handler/fn/var names, internal paths, `@mayarid/*`, GraphQL/Redis/env) reaches a reader | C7 |
| P0 | **No V1 content drift** — V1 tab byte-identical to `main`, only the label renamed | C8 |
| P0 | **Site builds / renders** — valid JSON, balanced JSX, parseable embedded JSON, fence parity | C1, C4, C5, C6 |
| P1 | **Base-URL fidelity** — prod `api.mayar.id/hl/v2` + sandbox `api.mayar.club/hl/v2` on every endpoint; zero `/hl/v1` leak | D1 |
| P1 | **Envelope quirk preserved** — `statusCode` + exactly-one-of `message`/`messages`; `data` optional for status-only writes | D5 |
| P1 | **Nav integrity** — nav↔file 1:1, no orphan/missing pages | C2 |
| P2 | **Endpoint contract complete** — method+path, Bearer auth, curl request example, field docs incl. `statusCode` | D2, D3, D4, D6 |
| P2 | **Frontmatter / authoring hygiene** — title present; no stray closing tags in prose | C3, D7 |

---

## 3. Scope

### In scope (under test)
- All 74 `.mdx` pages under `api-reference-v2/**`.
- `docs.json` navigation (tabs[2] structure; tabs[1] regression vs `main`).
- The two validation suites themselves (they are the deliverable test assets).

### Out of scope (explicitly NOT tested — see §6 for residual risk)
- V1 pages under `api-reference/**` content correctness — only checked for *non-change* (C8).
- The stock `api-reference/openapi.json` Plant-Store sample (cosmetic, unwired).
- The 3 excluded MCP routes (customer-detail / unpaid-transactions / product-members).
- **Semantic fidelity** of response examples vs the live API (value-level accuracy) —
  structurally checked (envelope shape) but not value-verified beyond the manual
  prod-capture done in implementation phases.
- Live **sandbox** responses (prod key 401s on `api.mayar.club`; documented by pattern).

---

## 4. Coverage / traceability matrix

Every check, what it guards, and which plan requirement it traces to.

| Check | Guards | Trace (plan) | Scope |
|-------|--------|--------------|-------|
| C1 | `docs.json` is valid JSON | Phase 1 / `python3 -m json.tool` | docs.json |
| C2 | nav↔file 1:1, 0 orphan / 0 missing | Decision: 1 .mdx per endpoint; Risk: nav 1:1 | 74 pages |
| C3 | frontmatter `title:` present | Phase 2/3 template | 74 pages |
| C4 | JSX balance (7 components) | Risk: render integrity | 74 pages |
| C5 | code-fence parity (even ```) | render integrity | 74 pages |
| C6 | embedded ```json parses (80 blocks) | render + example validity | 74 pages |
| C7 | **leak-grep** — 0 internal identifiers in rendered content | Risk: internal-id leak (P0) | 74 pages |
| C8 | tabs[1]=="API V1 Reference"; groups/pages == `main` | Decision/Risk: no V1 drift (P0) | docs.json vs main |
| D1 | prod+sandbox base URL; no `/hl/v1` leak | Decision: /hl/v2 base; sandbox by pattern | 74 pages |
| D2 | `openapi: METHOD /path` in frontmatter | Decision: openapi frontmatter convention | 71 endpoints |
| D3 | Bearer `Authorization` documented | REST contract | 71 endpoints |
| D4 | `<RequestExample>` curl on /hl/v2 | REST contract | 71 endpoints |
| D5 | envelope `statusCode` + `message`^`messages`; `data` optional | Decision: preserve message/messages quirk (P1) | 71 endpoints |
| D6 | ≥1 ParamField/ResponseField + `statusCode` field (+`data` when present) | field docs completeness | 71 endpoints |
| D7 | no stray/unknown closing tags in prose | bug-001 class (authoring artifacts) | 71 endpoints |

**Coverage assessment:** every P0/P1/P2 objective in §2 is enforced by at least
one executable check. No objective is unprotected. The two suites are
complementary, not overlapping — C4 balances 7 known JSX tags; D7 catches
*unknown* stray tags (the gap that let bug-001 hide). This pairing is
intentional and must be preserved.

---

## 5. Test data & fixtures

- **Subject under test**: the working-tree `api-reference-v2/**` + `docs.json`.
- **Baseline fixture**: `git show main:docs.json` — the C8 regression oracle for
  the V1 tab. Requires the `main` ref to be present (it is, in this worktree).
- **Embedded examples**: 80 ```json blocks captured from live prod GET reads
  (PII-scrubbed) or derived-and-flagged REPRESENTATIVE for writes.
- No external network, DB, or credentials needed at test time — suites are
  fully hermetic (the prod key was only used during *authoring*, not testing).

---

## 6. Gaps, residual risk & known defects

These are deliberately untested or accepted; listed so the execution phase and
reviewers see them explicitly (no silent caps).

| ID | Gap / risk | Status / mitigation |
|----|-----------|---------------------|
| G1 | **Runner wires only the structural suite.** `validate-v2-docs.sh` execs `validate-v2-docs.py` but NOT `domain-compliance-v2-docs.py`. A green `.sh` run does not prove domain compliance. | **CLOSED (Phase 14):** `.sh` now runs both suites and ANDs their exit codes — single combined gate. See test-execution.md §2. |
| G2 | **No CI wiring.** Suites are run manually; nothing prevents a future edit from regressing un-checked. | Recommend a CI hook (R2). Non-gating for this feature. |
| G3 | **Semantic fidelity not auto-verified.** Suites check envelope *shape*, not whether documented values match live API. | Accepted: covered by manual prod-capture + fidelity pass (Phases 3–5). REPRESENTATIVE writes flagged in-page. |
| G4 | **No link-integrity / heading-consistency check.** Internal cross-links and `## heading` uniformity are not asserted (Phase 12 fixed 7 heading inconsistencies by hand). | Deferred enhancement R3 (add heading-consistency check to validator). Non-gating. |
| G5 | **No real Mintlify build executed.** Static lint approximates render; it is not a `mint build`. | Accepted: no build tooling in-repo (plan Out-of-Scope). C4/C5/C6 are the proxy. |
| bug-002 | Upstream API defect (reviews stats endpoints HTTP 500). Not a docs defect. | **Open, non-gating.** Affected pages documented REPRESENTATIVE. Does not fail any check. |

---

## 7. Recommendations (for execution / completion phases)

- **R1 (do in Phase 14):** Make the suite entrypoint run **both** suites so one
  command gates the feature. Either invoke both `.py` files in Phase 14, or
  extend `validate-v2-docs.sh` to chain `domain-compliance-v2-docs.py` after the
  structural run and AND their exit codes. Closes G1.
- **R2 (deferred, non-gating):** Add a CI step that runs the combined gate on PRs
  touching `api-reference-v2/**` or `docs.json`. Closes G2.
- **R3 (deferred, non-gating):** Add a heading-consistency check (`## Authorization`,
  `## Path Parameters`) to the structural validator. Closes G4 / Phase-12 R1.

---

## 8. Execution plan (Phase 14 — test-execution)

**Commands (run from repo root):**
```bash
python3 .jonggrang/.output/features/api-v2-reference-docs-mqyl9hub/validate-v2-docs.py
python3 .jonggrang/.output/features/api-v2-reference-docs-mqyl9hub/domain-compliance-v2-docs.py
```
(or, after R1, a single combined entrypoint.)

**Entry criteria:** all 74 pages authored; `main` ref present for C8 baseline.

**Pass / exit criteria (gate):**
- Structural suite: exit 0, **8/8 PASS**.
- Domain suite: exit 0, **7/7 PASS**.
- No P0/P1 check failing. bug-002 is the only permitted open item (non-gating,
  upstream, flagged REPRESENTATIVE in-page).

**On failure:** a failing check prints `FAIL <id> <file>: <detail>` and a
non-zero exit. Triage as either (a) real docs defect → fix the page, re-run, OR
(b) false positive → adjust the check with a documented rationale (precedent:
the `</p>`-in-JSON and data-less-envelope false positives retired in Phase 11).
Do not weaken a check to pass without recording why.

**Current baseline (measured 2026-06-29):** both suites GREEN — structural 8/8,
domain 7/7, 74 pages / 71 endpoints / 80 json blocks. The feature is in a
passing state entering execution.
