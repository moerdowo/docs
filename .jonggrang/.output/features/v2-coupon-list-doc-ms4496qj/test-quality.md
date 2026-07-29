# Test Quality Review — V2 Get List Coupon doc page

- **Feature**: `v2-coupon-list-doc-ms4496qj`
- **Branch**: `feat/v2-coupon-list-doc`
- **Phase**: 16 — test-quality
- **Date**: 2026-07-28
- **Purpose**: no low-value tests, correct assertions
- **Result**: **PASS with corrections applied** — 5 findings, 3 fixed in this
  phase, 2 recorded. No finding changes the verdict on the page itself.

---

## 1. Method

Phase 16 audits the *tests*, not the page. Every quantitative claim in
`test-plan.md`, `test-execution.md` and `coverage.md` was re-derived from the
tree rather than read forward, and each test case was examined for two failure
modes:

- **Low value** — does the assertion duplicate one already made elsewhere, or
  assert something that cannot fail?
- **Wrong assertion** — does the check actually verify what its report claims,
  and is the recorded result factually true?

Where a check was weaker than advertised, it was rewritten and mutation-tested
rather than merely flagged.

**Re-verified as correct** (no finding):

| Claim | Verdict |
|---|---|
| Suite exit 1; exactly 16 FAIL lines | ✅ re-run, confirmed |
| T1 baseline delta empty, both directions | ✅ re-run, `diff` empty |
| `gate-baseline.txt` is byte-unchanged and stored sorted | ✅ confirmed |
| No FAIL line names `discount/` or `docs.json` | ✅ confirmed |
| New page is inside the 82 endpoint pages (stem `index` not in `OVERVIEW`) | ✅ confirmed in source and by count (85 − 3 = 82) |
| T2: exactly 2 content files, 209 insertions, 0 deletions | ✅ confirmed |
| T3 position: new slug first in the Discount & Coupon group | ✅ confirmed |
| T4 `Endpoint:` CodeGroup byte-shape matches bundling/installment/invoice | ✅ confirmed with `cat -A`, incl. the double blank line |
| T5 data safety: all literals synthetic, no credential | ✅ re-read, confirmed |

---

## 2. Findings

### F1 — The blocking gate's fixture is not committed (HIGH, fixed)

`test-plan.md` §6 states G1 is *"Mitigated: the fixture is committed with this
plan and its provenance is stated."* It was not. `git ls-files` showed
`gate-baseline.txt` untracked, along with `test-plan.md`, `domain-compliance.md`
and `bugs.md`.

T1 is the one blocking test, and its entire pass criterion is a diff against
that fixture. Untracked, the oracle is invisible in review and disappears on a
fresh checkout — the stated mitigation for the plan's own top risk did not
exist. This is the highest-impact finding: not a wrong assertion, but an
assertion with no durable basis.

**Fixed:** all four files committed in this phase.

### F2 — T6's "exact two-way match" could not detect a deleted section (HIGH, fixed)

`test-execution.md` §7 and `coverage.md` §5 report T6 as an *"exact two-way
match"* of documented fields against example keys, and `coverage.md` §4 credits
it as fully automated, closing the parity gap D6 leaves open.

The implementation compared a **flat set** of example keys against a **flat set**
of `<ResponseField name=…>` values. This page reuses `id` and `name` at two
depths (`coupons` and `coupons.products`), so the flat sets collapse nesting.
Demonstrated by mutation — deleting the **entire** `### coupons.products
Structure` section (both of its `ResponseField`s):

```
AFTER deleting the whole 'coupons.products' section:
  in example not documented: []
  documented not in example: []
  T6 verdict would be: PASS (undetected!)
```

A check that a whole missing documentation section walks straight past is not
the parity guarantee the reports claim.

**Fixed:** replaced with a path-aware check,
`field-parity-check.py`, which resolves each `### <path> Structure (…)` heading
to a node in the response example and compares key sets *at that node*, plus
asserts every object node in the example has a documenting section.

Result on the page — it genuinely passes the stronger check:

```
PASS  Main              path=(root)                  5 field(s)
PASS  data              path=data                    1 field(s)
PASS  coupons           path=data.coupons            8 field(s)
PASS  coupons.products  path=data.coupons.products   2 field(s)
RESULT: PASS (parity holds at all 4 structures)
```

Mutation-tested, so the new assertion is proven live rather than asserted:

| Mutation | Old T6 | New check |
|---|---|---|
| Delete the whole `coupons.products` section | PASS (missed) | **FAIL** — `example node data.coupons.products undocumented` |
| Drop one nested field (`products.name`) | — | **FAIL** — `missing=['name']` |
| Rename a root field (`hasMore` → `hasMoreX`) | — | **FAIL** — `missing=['hasMore'] orphan=['hasMoreX']` |
| Negative control (pristine) | PASS | **PASS**, exit 0 |

### F3 — The recorded "Status code from API." divergence was factually wrong (MEDIUM, fixed)

`test-execution.md` §5 and `domain-compliance.md` §"Two deliberate, documented
divergences" both asserted that *all* siblings carry the typo `Status code form
API.`, that the fix is *"corrected on the new page only"*, and that *"the other
81 pages"* would need fixing. The stated evidence was a grep of two pages
(`invoice`, `bundling`) generalised to the corpus.

Measured across the corpus:

| | Count |
|---|---|
| Pages reading `Status code form API.` (typo) | **35** |
| Pages reading `Status code from API.` | **16** |

The corpus is split, not uniform, and 81 is not a number that appears anywhere
in the data. More importantly the direction of the finding was wrong: all four
**discount-group** siblings (`create`, `detail`, `validate`, `check`) *already*
read "from". The new page is **consistent with its own nav group**; it diverges
only from the four **list-page** siblings that supplied its structural template.

The page's wording needs no change — it was right for a reason the reports got
wrong. **Fixed:** both documents corrected in place with the measured figures.

### F4 — T3 is two-thirds duplicate assertion (LOW, recorded)

T3's three assertions:

| Assertion | Value |
|---|---|
| `python3 -m json.tool docs.json` | **Duplicate** — C1 is exactly this check, already inside T1 |
| `test -f api-reference-v2/discount/index.mdx` | **Duplicate** — C2 asserts nav→file resolution for every slug; `test-execution.md` §4 concedes "C2 inside T1 independently confirms the nav↔file relation" |
| New slug is **first** in its group | **Unique** — no automated check covers ordering |

Only the third assertion earns its place. Not corrected: the duplicates are
zero-cost and cause no false confidence, so removing them is churn. Recorded so
T3 is not mistaken for three independent signals. Worth noting that T3's one
load-bearing assertion is the *manual* one.

### F5 — One objective is credited to tests that do not assert it (LOW, recorded)

`test-plan.md` §2 and `coverage.md` §4 map the P2 objective *"Scope honoured —
headless only, no `/mobile/v2`, `detail.mdx` untouched"* to **T2 + T6**, marked
*"full (both scripted)"*.

T2 covers `detail.mdx` untouched (via diff containment). T6 is field parity and
asserts nothing whatsoever about surfaces. **Nothing tests the headless-only
half of the objective.** The property does hold — the page contains no
`/mobile/v2` string, and `mobile` appears only inside the non-rendered
maintainer comment — but it holds unverified by any check.

So `coverage.md`'s **8/8 objective coverage** is marginally overstated: 7 fully
covered, 1 partially. This does not change the phase verdict (the uncovered half
is a negative property that is true today), but the traceability table should not
read "full".

---

## 3. Low-value test sweep

Every test case assessed for whether it earns its keep:

| ID | Verdict | Note |
|----|---------|------|
| T1 | **High value** | The only blocking gate; catches regression across the whole corpus. Fixture now committed (F1). |
| T2 | **High value** | Sole guard on V2-side collateral damage; C8 only covers the V1 tab. No overlap. |
| T3 | **Partly low value** | 2 of 3 assertions duplicate C1/C2 (F4); ordering assertion is unique. |
| T4 | **High value** | Catches what no automated check does (heading chain, byte-level fence shape). One recorded result was wrong (F3). |
| T5 | **High value** | Genuinely complements C7 — a denylist grep cannot tell a real merchant name from a synthetic one. Human judgment is the right tool. |
| T6 | **Was low value, now high** | Advertised guarantee did not hold (F2); replaced and mutation-proven. |

No test asserts something that cannot fail. No test was found to be pure
ceremony. The suite-level guards against vacuous green (`C0`/`D0`, which fail if
the corpus is empty) are present and correct — a good sign the parent feature
already thought about this failure mode.

---

## 4. Assertion-correctness sweep

| Reported claim | Status |
|---|---|
| T1 gate, 16 FAILs, empty delta | ✅ correct, reproduced |
| T2 change surface | ✅ correct, reproduced |
| T3 nav position | ✅ correct (but see F4 on redundancy) |
| T4 CodeGroup / heading chain | ✅ correct, byte-verified |
| T4 "Status code form/from" divergence | ❌ **wrong** → F3, corrected |
| T5 data safety | ✅ correct, re-read |
| T6 "exact two-way match" | ⚠️ **weaker than claimed** → F2, replaced |
| G1 "fixture is committed" | ❌ **wrong** → F1, now true |
| coverage 8/8 objectives | ⚠️ **overstated** → F5, 7 full + 1 partial |
| coverage 15/15 mutation-proven | ✅ plausible and consistent with the suite source; C1/C8 probe corrections are honestly disclosed |

---

## 5. Carried forward (unchanged, non-gating)

G2 (`products[]` not live-verified), G3 (`limit` cap unknown), G5 (no CI
wiring), G6 (no real Mintlify render), G7 (query params unasserted) all stand as
recorded. G4 shrinks: field parity is now scripted **and** nesting-aware, so only
T4 (heading consistency) and T5 (real-vs-synthetic judgment) remain manual.

`bug-001` / `bug-002` remain open, `main`-side, and account for all 16 baseline
FAILs. **No new bug was filed** — F1–F5 are defects in the tests and their
reports, not in the product, and Phase 16 owns those artefacts directly.

---

## 6. Verdict

The page and nav entry are unchanged by this phase and remain correct; no
finding here casts doubt on the deliverable. Two claims that were load-bearing
for confidence turned out to be unfounded — the gate fixture was never committed
(F1) and the parity check could not detect a deleted section (F2) — and both are
now genuinely true rather than merely asserted. One recorded result was factually
wrong and has been corrected (F3). Two traceability overstatements are recorded
(F4, F5).

**Phase 16 PASS.**
