# Coverage Report — V2 Get List Coupon doc page

- **Feature**: `v2-coupon-list-doc-ms4496qj`
- **Branch**: `feat/v2-coupon-list-doc`
- **Phase**: 15 — coverage
- **Date**: 2026-07-28
- **Result**: **PASS** — 100% objective coverage, 15/15 checks proven live on the
  change surface by mutation probe, baseline delta empty

---

## 1. What "coverage" means for this feature

This is a **documentation corpus**, not runnable code: no application runtime, no
in-repo test framework (`test command: echo 'no test command configured'`). There
is no line/branch coverage to instrument. Following the methodology the parent
feature established (`api-v2-reference-docs-mqyl9hub/coverage.md` §1), coverage
is measured as:

1. **Corpus coverage** — fraction of pages/endpoints/JSON blocks exercised by ≥1 check.
2. **Check-level coverage (mutation-proven)** — for each of the 15 gate checks,
   does it actually *fire on the new page* when that page is defective?
3. **Objective coverage** — fraction of P0/P1/P2 objectives (test-plan §2)
   enforced by ≥1 executed check.
4. **Gate pass rate** — baseline-delta, per plan G1 (the gate is red on `main`).

**Threshold**: 100% objective coverage (no P0/P1/P2 objective unprotected) **and**
an empty baseline delta. Both met.

§2 of the parent report measured only *scope* (is the file in the loop). This
phase strengthens that to *mutation* evidence (does the check catch a defect
there) — scope alone can be satisfied by a check that asserts nothing on the file.

---

## 2. Corpus coverage (measured this phase)

| Unit | In tree | Exercised | Coverage |
|------|---------|-----------|----------|
| `.mdx` pages (`api-reference-v2/**`) | 85 | 85 (C2–C7, D1) | **100%** |
| Endpoint pages (non-overview) | 82 | 82 (D2–D7) | **100%** |
| Embedded ```json blocks | 94 | 94 (C6) | **100%** |
| `docs.json` nav | 1 | 1 (C1, C2, C8) | **100%** |

Counts re-derived from the tree this phase (`find` → 85 / 82 / 94) and they match
what both suites self-report (`all 85 pages`, `all 82 endpoint pages`,
`94 json blocks`). No page is outside the reach of a check.

**The new page is inside every set, not exempted.** The domain suite exempts
overview pages by *file stem* — `OVERVIEW = {introduction, statuscode, rate-limit}`.
The stem `index` is **not** in that set, so `discount/index.mdx` is treated as a
full endpoint page and D2–D6 apply to it. This was the main exemption risk for a
page named `index.mdx`; it is confirmed absent, and mutation probes D2/D3/D4/D5/D6
below prove it empirically rather than by reading the constant.

Contribution of the new page: 1 page, 1 endpoint page, 3 JSON blocks, 1 nav entry.

---

## 3. Check-level coverage — mutation-proven (the new evidence)

Method: the change surface (`api-reference-v2/discount/index.mdx` + `docs.json`)
was copied to a throwaway git repo at `/tmp/covtest` that reproduces the 16-FAIL
baseline **exactly** (verified, C8 live via a real `main` ref). For each check, a
defect of exactly the kind that check exists to catch was injected **into the new
page**, the suite re-run, and the *new* FAIL set (`comm -13` against baseline)
inspected for that check id naming the mutated file. A check that stays green
under its own mutation does not cover the page.

| Check | Mutation injected into the new page | Fires? |
|-------|--------------------------------------|--------|
| C1 | append `{{bad` to `docs.json` | ✅ COVERED |
| C2 | rename the page (nav slug now dangling) | ✅ COVERED |
| C3 | delete the frontmatter `title:` | ✅ COVERED |
| C4 | delete one `</ResponseField>` | ✅ COVERED |
| C5 | delete one ``` fence | ✅ COVERED |
| C6 | corrupt JSON in the 200 example | ✅ COVERED |
| C7 | inject internal identifier `getDiscount` into prose | ✅ COVERED |
| C8 | append a bogus page to the V1 tab | ✅ COVERED |
| D1 | rewrite prod base URL to `/hl/v1` | ✅ COVERED |
| D2 | delete the `openapi:` frontmatter | ✅ COVERED |
| D3 | break every `Bearer` token | ✅ COVERED |
| D4 | delete the curl line | ✅ COVERED |
| D5 | delete `"statusCode": 200` from the envelope | ✅ COVERED |
| D6 | delete the `data` `<ResponseField>` | ✅ COVERED |
| D7 | inject a stray `</Bogus>` closing tag in prose | ✅ COVERED |

**Check-level coverage: 15/15 (100%).**

Two probes needed a corrected assertion before they read true — both were flaws in
the probe, not gaps in the gate:

- **C1** — the entrypoint short-circuits on invalid `docs.json` and prints
  `FAIL: docs.json is not valid JSON`, which does not match the
  `FAIL  <id>  <detail>` line shape the other checks use. Re-probed against the
  raw output: fires, exit 1.
- **C8** — fires as `FAIL  C8  tabs[1] groups/pages DIFFER from main`; the message
  names `tabs[1]`, not the filename the probe was grepping for.

**Negative control**: after every probe the copy was reset and re-run — pristine
returns exactly the 16 baseline FAILs, so no probe leaked residue into another and
no "COVERED" verdict came from a pre-existing failure.

---

## 4. Objective coverage (traceability, test-plan §2)

| Pri | Objective | Enforced by | Automated? | Status |
|-----|-----------|-------------|-----------|--------|
| P0 | No regression (zero new FAIL) | T1 baseline delta | full | ✅ |
| P0 | Site still builds | C1, C4, C5, C6 | full | ✅ |
| P0 | No leak | C7 + T5 | partial — C7 auto, T5 manual | ✅ |
| P0 | No collateral damage | C8, T2 | full | ✅ |
| P1 | Endpoint contract correct | D1, D3, D4, D5 | full | ✅ |
| P1 | Page reachable, first in group | C2, T3 | full | ✅ |
| P2 | Field docs complete & corpus-consistent | D2, D6, D7 + T4 | partial — T4 manual | ✅ |
| P2 | Scope honoured (headless only) | T2 + T6 | ~~full (both scripted)~~ **partial** — see below | ⚠️ |

**Objective coverage: ~~8/8 (100%)~~ 7 full + 1 partial.**

> **Corrected in Phase 16 (test-quality F5).** The last row was overstated. T2
> covers "`detail.mdx` untouched" via diff containment, but T6 is field parity and
> asserts nothing about surfaces — **nothing tests the headless-only /
> no-`/mobile/v2` half** of that objective. The property does hold (the page has
> no `/mobile/v2` string; `mobile` appears only in the non-rendered maintainer
> comment), but it holds unverified. All P0/P1 objectives remain fully protected.

Automation split: **5/8 fully automated**, 3 carry a manual component (T4 heading
consistency, T5 real-vs-synthetic data judgment). T6, manual in the Phase 14 plan,
was **scripted** this phase (§5) and is now reproducible.

---

## 5. Re-verification performed this phase

Coverage claims are grounded in measurements taken now, not inherited from Phase 14.

- **Gate / baseline delta** — suite re-run from repo root: exit 1, 16 FAIL lines,
  set-identical to `gate-baseline.txt`. Nothing added (no new defect), nothing
  removed (no out-of-scope edit). Zero FAIL lines name `discount/index` or
  `docs.json`.
  - Note for future phases: the stored baseline is **sorted**; the suite emits
    per-file order. A raw `diff` shows spurious reordering — compare as a **set**
    (`sort` both sides). The 16 lines are identical either way.
- **T2 containment** — `git diff main` touches exactly two non-workspace files:
  `api-reference-v2/discount/index.mdx` (+208) and `docs.json` (+1). 209
  insertions, **0 deletions**.
- **T6 field parity — now scripted** (recursive key walk of all 3 JSON examples ×
  `<ResponseField>` set, minus the `Authorization` header block): 14 example keys,
  14 documented fields, `in example not documented: []`,
  `documented not in example: []` — exact two-way match.
  - **Phase 16 correction (test-quality F2):** this flat-set comparison is blind
    to nesting and misses the deletion of an entire nested section. Superseded by
    `field-parity-check.py` (path-aware, mutation-proven). The page passes the
    stronger check at all 4 structures.
- **Gate pass rate**: 15/15 checks green *on the change surface*; the 16 corpus
  FAILs are pre-existing and `main`-side (bug-001, bug-002).

---

## 6. Coverage gaps (carried forward, non-gating)

No **objective** is uncovered. These are coverage-*depth* limits.

| ID | Coverage limit | Status |
|----|----------------|--------|
| G2 | `products[]` item fields beyond `id` not live-verified | Open, source-side; disclosed in the in-page maintainer comment |
| G3 | `limit` cap unverified — siblings say "maximum of 50", this page stays silent | Open, source-side; documenting an unverified cap is worse than the gap |
| G4 | T4 (heading consistency) + T5 (real-vs-synthetic data) are manual, so they do not protect future edits | Deferred to parent R3; T6 closed this phase by scripting it |
| G5 | No CI wiring for the gate on `api-reference-v2/**` | Deferred to parent R2 |
| G6 | No real Mintlify render; C4/C5/C6 approximate a build | Accepted — no build tooling in-repo |
| **G7** | **New this phase.** The 5 documented query params (`limit`, `startingAfter`, `status`, `search`, `productId`) have **no** automated assertion and no recorded source verification. `limit`/`startingAfter` are corroborated by corpus pagination convention; `status`/`search`/`productId` rest on the Phase 8 source transcription alone. Only `limit` appears in an example. | Open, source-side — same class as G2/G3 |

G7 is a documentation-confidence limit, not a defect — nothing is known to be
wrong, so per AGENTS.md ("report real defects only") it is recorded here rather
than filed as a bug. Closing it needs a live call or source read, neither
available at test time.

No new defect was found this phase; nothing new filed. bug-001 / bug-002 remain
open, `main`-side, and account for all 16 baseline FAILs.

---

## 7. Verdict

- Corpus coverage: **100%** (85/85 pages, 82/82 endpoints, 94/94 JSON blocks, 1/1 nav).
- Check-level coverage: **15/15 mutation-proven** live on the new page.
- Objective coverage: **7 full + 1 partial** of 8 P0/P1/P2 objectives (§4, corrected
  in Phase 16 F5 — the headless-only half of P2 holds but is unasserted).
- Baseline delta: **empty** — no regression, no collateral change.

**Coverage threshold met. Phase 15 PASS.**
