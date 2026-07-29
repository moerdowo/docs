# Completion Report — V2 Get List Coupon doc page

- **Feature**: `v2-coupon-list-doc-ms4496qj`
- **Branch**: `feat/v2-coupon-list-doc` (base `main`)
- **Work type**: SMALL
- **Phase**: 17 — completion
- **Date**: 2026-07-28
- **Result**: **PASS** — all 15 tasks completed, final verification re-run clean.

---

## 1. What shipped

Two content files, additive only — **209 insertions, 0 deletions**:

| File | Change |
|---|---|
| `api-reference-v2/discount/index.mdx` | **new** — 208 lines. `GET /hl/v2/coupons` list page. |
| `docs.json` | **+1 line** — registers `api-reference-v2/discount/index` first in the V2 *Discount & Coupon* nav group. |

Everything else in `git diff main..HEAD` is `.jonggrang/**` workspace artefacts
(plans, reports, the gate fixture, the parity checker).

The page documents the headless surface only: request example, three response
examples (200 / 400 / 500), Production + Sandbox `Endpoint:` CodeGroup,
Authorization, five query parameters (`limit`, `startingAfter`, `status`,
`search`, `productId`), and four response-field structures (root, `data`,
`coupons`, `coupons.products`).

---

## 2. Final verification (re-run in this phase, not carried forward)

| Check | Command | Result |
|---|---|---|
| Blocking gate (T1) | `validate-v2-docs.sh` | exit 1, **16 FAIL lines**, `diff` vs `gate-baseline.txt` **empty** ✅ |
| No new FAIL touches this feature | grep `discount\|docs.json` over FAIL set | **none** ✅ |
| Field parity, path-aware (Phase 16 F2 replacement) | `field-parity-check.py api-reference-v2/discount/index.mdx` | **PASS**, exit 0, parity holds at all 4 structures ✅ |
| Change surface (T2) | `git diff --numstat main..HEAD -- ':!.jonggrang'` | 208+0 and 1+0 across exactly 2 files ✅ |
| Nav position (T3) | `docs.json` parse | new slug **first** in V2 *Discount & Coupon*; V1 group byte-unchanged ✅ |
| `openapi:` frontmatter convention | compared to 4 discount siblings + 2 list siblings | `GET /endpointdiscountv2/index` matches `<VERB> /endpoint<domain>v2/<page>` ✅ |
| File hygiene | `od -c` on tail | trailing newline present ✅ |
| Working tree clean of stray content edits | `git status` excluding workspace dirs | **clean** ✅ |

> **Reading the gate.** Exit code 1 is the *success* state for this feature. The
> 16 FAILs are pre-existing on `main` and fully accounted for by `bug-001` and
> `bug-002`. The pass criterion is the **baseline delta**, in both directions —
> no new FAIL, and no baseline FAIL silently vanishing (which would mean an
> out-of-scope page was edited). Do not "fix" the exit code.
>
> Note the FAIL lines are **indented two spaces** in suite output. `grep "^FAIL"`
> silently matches nothing and looks like a perfect run; use `grep -E "^\s*FAIL"`
> and strip leading whitespace before diffing against `gate-baseline.txt`.

---

## 3. Cleanup applied in this phase

| Item | Action |
|---|---|
| `.jonggrang/progress.txt` Phase-14 entry still asserted the `Status code form API.` typo is "corpus-wide" — the claim Phase 16 F3 measured as wrong (35 "form" / 16 "from"; all four discount siblings already read "from"). | Corrected in place with the measured figures and the F3 cross-reference. |
| `coverage.md` §7 verdict still read "Objective coverage: 8/8 (100%)" while §4 had already been corrected to 7 full + 1 partial (F5). | §7 aligned to 7 full + 1 partial. |

No content file was touched. The page and nav entry are byte-identical to what
entered Phase 17.

---

## 4. Known limitations carried to merge (all recorded, none gating)

| ID | Limitation | Why accepted |
|---|---|---|
| G2 | `products[]` item fields beyond `id` not verified against a live response | Disclosed in the in-page maintainer comment; source-side. |
| G3 | `limit` cap unknown — siblings say "maximum of 50", this page stays silent | Silence is safer than an unverified cap. |
| G5 | No CI wiring for the gate | Suite is run manually; out of scope for a SMALL doc feature. |
| G6 | No real Mintlify render performed | No local Mintlify toolchain available. |
| G7 | Query parameters not asserted by any automated check | Manual review (T4) covers them. |
| F5 | The "headless only, no `/mobile/v2`" half of objective P2 holds but is unasserted | Negative property, true today; recorded rather than papered over. |
| F4 | T3 has 2 of 3 assertions duplicating C1/C2 | Zero-cost duplicates; removing them is churn. |

Manual-only checks that survive: **T4** (heading chain, byte-level CodeGroup
fence shape) and **T5** (real-vs-synthetic judgment on literals). Field parity is
now scripted *and* nesting-aware, so G4 shrank to those two.

---

## 5. Open bugs — both `main`-side, both out of scope

Neither is introduced by this branch; together they produce all 16 baseline FAILs.

- **bug-001** — `api-reference-v2/nameservice/{create,update}.mdx` exist on disk
  but appear in no nav group → unreachable on the docs site. 2 × C2 FAIL.
- **bug-002** — the domain-compliance suite hard-codes `/hl/v2` + the
  `{statusCode, messages}` envelope; the SaaS / software-license pages
  legitimately use `/saas/v2` and `/software/v2` with a different envelope.
  14 FAILs (D1/D4/D5). Needs either a suite exemption list or sandbox base URLs
  on those pages.

Recorded in `bugs.md`. `jonggrang bug` refused to run (`Multiple features
found.`) even with `--feature` supplied, so both were written by hand in the
CLI's format.

---

## 6. Phase ledger

| Phase | Name | Result |
|---|---|---|
| 1–4 | setup, triage, codebase-discovery, skill-discovery | ✅ |
| 8 | implementation (task-001…004) | ✅ |
| 9 | simplification | ✅ |
| 11 | domain-compliance | ✅ |
| 12 | code-quality | ✅ |
| 13 | test-planning | ✅ 6 test cases, 7 gaps recorded |
| 14 | testing | ✅ 6/6, 0 regressions, 0 changes |
| 15 | coverage | ✅ 100% corpus, 15/15 mutation-proven |
| 16 | test-quality | ✅ 5 findings, 3 fixed (F1 fixture committed, F2 parity check replaced, F3 divergence corrected) |
| 17 | completion | ✅ this report |

**Feature complete. Ready for review.**
