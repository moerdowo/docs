# Test Quality Review — API V2 Reference Documentation

- **Feature**: api-v2-reference-docs
- **Phase**: 16 — test-quality
- **Purpose**: No low-value tests, correct assertions
- **Date**: 2026-06-29
- **Result**: PASS — all 15 checks proven LIVE; one latent vacuous-pass smell fixed

---

## 1. Method

"Tests" for this docs corpus are the two static-validation suites (15 checks,
74 pages / 71 endpoints). The two test-quality risks for assertion-style suites
are (a) **vacuous checks** that show PASS but can never fail, and (b) **wrong
assertions** that pass on genuinely broken input. Both were attacked by
**mutation testing**: inject exactly one defect per check, confirm the suite
turns RED *and* the expected check id appears in a FAIL line, then `git restore`
and confirm the gate returns to GREEN with no leftover mutation.

Harness: `/tmp/mutation_test.py` (15 mutations). Subject file for per-page
mutations: `api-reference-v2/bundling/detail.mdx`; `docs.json` for C1/C8.

## 2. Mutation results — every check's FAIL branch is LIVE

| Check | Injected defect | Verdict |
|-------|-----------------|---------|
| C1 | append garbage to docs.json | LIVE (red + caught) |
| C2 | add orphan `.mdx` not in nav | LIVE |
| C3 | strip frontmatter `title:` | LIVE |
| C4 | add unbalanced `<Note>` | LIVE |
| C5 | add a single stray ` ``` ` | LIVE |
| C6 | corrupt embedded JSON | LIVE |
| C7 | inject `@mayarid/core` into rendered prose | LIVE |
| C8 | mutate tabs[1] (V1) path | LIVE |
| D1 | inject `/hl/v1` base URL | LIVE |
| D2 | remove `openapi: METHOD /path` | LIVE |
| D3 | replace all `Bearer` tokens | LIVE |
| D4 | break RequestExample `/hl/v2` curl | LIVE |
| D5 | add both `message` + `messages` (break XOR) | LIVE |
| D6 | rename `statusCode` ResponseField | LIVE |
| D7 | inject stray `</content>` in prose | LIVE |

**15/15 LIVE. Zero vacuous checks. No redundant/duplicate checks** — C4
(balance of 7 known tags) and D7 (unknown stray tags) are complementary, not
overlapping. Assertions are correct: each mutation that *should* fail the
contract does, and the clean baseline passes.

## 3. Defect found & fixed — latent vacuous all-green on empty corpus

Every PASS gate is a `count == total` comparison and the negative checks (C7
leak-grep, C2) pass on "nothing found." With `total == 0` (empty corpus) the
**entire suite would report all-green while asserting nothing** — a textbook
low-value-test trap. It does not trigger today (corpus is 74/71) but the
phase mandate is to remove that class.

**Fix** (non-weakening; both suites stay GREEN on the real corpus):
- `validate-v2-docs.py`: hard-fail **C0** if no `.mdx` found under
  `api-reference-v2/`.
- `domain-compliance-v2-docs.py`: hard-fail **D0** if no endpoint pages found.

Verified: on an empty sandbox corpus the suites now exit 1 with `C0`/`D0`
FAIL lines (previously they would have exited 0). On the real corpus the gate
remains GREEN and all 15 mutations remain LIVE.

## 4. Low-value scan — none found

- No test asserts a tautology or a constant.
- No test is disabled/skipped.
- No over-broad assertion that passes on broken input (mutation-confirmed).
- The `count == total` gates are meaningful (total is non-zero and now guarded).
- bug-002 (upstream reviews-stats 500) remains correctly out of scope of the
  suites — a docs check should not assert live-API health.

## 5. Outcome

Combined gate after changes: **structural 8/8 + domain 7/7 = GREEN**, single
entrypoint `validate-v2-docs.sh` exit 0. No check logic weakened; one guard
added per suite to close the empty-corpus vacuous-pass smell. Test quality:
**PASS**.
