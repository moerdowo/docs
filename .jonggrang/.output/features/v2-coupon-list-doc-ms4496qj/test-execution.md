# Test Execution — V2 Get List Coupon doc page

- **Feature**: `v2-coupon-list-doc-ms4496qj`
- **Branch**: `feat/v2-coupon-list-doc`
- **Phase**: 14 — testing
- **Date**: 2026-07-28
- **Plan**: `test-plan.md` (Phase 13)
- **Result**: **PASS** — 6/6 test cases pass, 0 regressions, 0 new defects

---

## 1. Result summary

| ID | Test case | Pri | Type | Result |
|----|-----------|-----|------|--------|
| T1 | Baseline-delta gate | P0 | automated, blocking | **PASS** |
| T2 | Change-surface containment | P0 | automated | **PASS** |
| T3 | Nav resolution & position | P1 | CLI | **PASS** |
| T4 | Corpus-consistency spot check | P2 | manual | **PASS** |
| T5 | Data-safety read-through | P0 | manual | **PASS** |
| T6 | Documented-vs-example field parity | P2 | manual | **PASS** |

No test was skipped. No check was modified, weakened, or waived. No fixture was
regenerated (G1 mitigation honoured — `gate-baseline.txt` is byte-unchanged).

Executed in plan order: T1 → T2 → T3 → T4/T5/T6.

---

## 2. T1 — Baseline-delta gate (P0, blocking)

```
bash .jonggrang/.output/features/api-v2-reference-docs-mqyl9hub/validate-v2-docs.sh
SUITE EXIT: 1
FAIL count: 16
diff gate-baseline.txt /tmp/gate-now.txt  →  (empty)
T1 PASS — FAIL set identical to baseline
```

Both stated criteria hold:

1. **No FAIL names a file this feature touches.** All 16 are in
   `api-reference-v2/nameservice/` (×2, C2 orphans — bug-001) and
   `api-reference-v2/saas/` + `api-reference-v2/software/` (×14, D1/D4/D5 —
   bug-002). Zero mention `api-reference-v2/discount/` or `docs.json`.
2. **Set unchanged in both directions.** 16 lines, `diff` empty — nothing added
   (no new defect) and nothing removed (no out-of-scope edit crept in).

Suite exit code is **1**, as the plan predicted. That is the expected value on a
red baseline and was not treated as a failure.

Checks that passed *including the new page* in their scope (the page is inside
the 85-page / 82-endpoint-page counts, not exempted):

```
PASS  C1  docs.json is valid JSON
PASS  C3  frontmatter title present on all 85 pages
PASS  C4  JSX tags balanced on all 85 pages
PASS  C5  code-fence parity (even) on all 85 pages
PASS  C6  embedded JSON parses (94 json blocks)
PASS  C7  leak-grep clean (0 internal identifiers in rendered content)
PASS  C8  tabs[1]=="API V1 Reference"; groups/pages unchanged vs main
PASS  D2  method+path frontmatter on all 82 endpoint pages
PASS  D3  Bearer auth documented on all 82 endpoint pages
PASS  D6  field docs (statusCode+data ResponseFields) on all 82 endpoint pages
PASS  D7  no stray closing tags on all 82 endpoint pages
```

C2 (×2) and D1/D4/D5 (×14) are the pre-existing failures; the only C2/D1/D4/D5
FAIL lines emitted name out-of-scope pages. Counts match the Phase 13 measured
entry state exactly (85 / 82 / 94), so the suite saw the same corpus the plan
was written against.

## 3. T2 — Change-surface containment (P0)

```
git diff main --stat -- api-reference-v2/ docs.json
 api-reference-v2/discount/index.mdx | 208 ++++++++++++++++++++++++++++++++++++
 docs.json                           |   1 +
 2 files changed, 209 insertions(+)
```

Exactly two content files. **209 insertions, 0 deletions** — nothing removed
anywhere. `detail.mdx`, `create.mdx`, `validate.mdx`, `check.mdx` are untouched.

The `docs.json` hunk is the single expected added line:

```diff
             "group": "Discount & Coupon",
             "pages": [
+              "api-reference-v2/discount/index",
               "api-reference-v2/discount/create",
```

`git diff main --stat` over the whole tree shows the only other changes are
Jonggrang workspace artefacts (`.jonggrang/**` — MANIFEST, tasks, progress,
codemap, phase reports). No source or docs file outside the two above.

## 4. T3 — Nav resolution & position (P1)

```
python3 -m json.tool docs.json   →  json ok
391:  "api-reference-v2/discount/index"      ← new, first in group
392:  "api-reference-v2/discount/create"
393:  "api-reference-v2/discount/detail"
394:  "api-reference-v2/discount/validate"
395:  "api-reference-v2/discount/check"
test -f api-reference-v2/discount/index.mdx  →  slug resolves
```

JSON valid; new slug is first in the V2 "Discount & Coupon" group; the original
four follow in their original order; the slug maps to a file on disk. C2 inside
T1 independently confirms the nav↔file relation is 1:1 for the new page (it
raised no orphan/dangling FAIL for it).

## 5. T4 — Corpus-consistency spot check (P2)

Compared against the four sibling V2 list pages (`bundling`, `installment`,
`invoice`, `reqpayment` `index.mdx`) and the four sibling discount pages.

| Aspect | Sibling convention | New page | Verdict |
|---|---|---|---|
| Frontmatter `openapi` | `GET /endpoint<domain>v2/index` | `GET /endpointdiscountv2/index` | match |
| Tag order | RequestExample → ResponseExample → `Endpoint:` → CodeGroup | identical | match |
| Section order | `## Authorization` → `## Query Parameters` → `## Response` | identical | match |
| `Endpoint:` CodeGroup | `?limit=10` on **both** prod and sandbox lines | both carry it | match |
| Double blank line between fences | 2 blank lines | 2 blank lines (verified byte-wise with `cat -A`) | match |
| Authorization block | `<ResponseField name="Authorization" type="string" required>` + literal `Authorization \| Bearer Paste-Your-API-Key-Here` | identical | match |
| `<ParamField>` form | `query="x" path="x" [default] type=` | identical for all 5 params | match |
| Trailing byte | `\n` | `\n` | match |
| Heading chain | `### Main Structure (Root)` → data → nested | `Main Structure (Root)` → `data Structure (Object)` → `coupons Structure (Array Of Object)` → `coupons.products Structure (Array Of Object)` | match, see below |

The `Endpoint:` CodeGroup is byte-for-byte the same shape as `bundling`,
`installment` and `invoice` (`reqpayment` is the known lone exception that omits
`?limit=10`; the new page correctly follows the majority-of-3 form fixed in
Phase 12).

**Divergences found: exactly the two already documented** in
`domain-compliance.md` §"Two deliberate, documented divergences" — nothing else:

1. `### data Structure (Object)` where siblings have `(Array Of Object)`.
   Source-side: this endpoint wraps a `coupons` array in an object. The nested
   heading chain follows the convention `invoice`/`bundling` use for sub-objects.
2. `Status code from API.` where all siblings carry the long-standing typo
   `Status code form API.` Confirmed by grep: `invoice` and `bundling` both read
   "form"; the new page reads "from". Corrected on the new page only.

## 6. T5 — Data-safety read-through (P0)

Read every literal value in the curl and all three JSON examples.

- IDs: `3f1c8b02-…`, `8a52d7e4-…`, `6f8c19ff-2b6a-4c7e-9f1d-1a2b3c4d5e6f` —
  all synthetic UUID-shaped, the last visibly a `1a2b3c4d5e6f` placeholder.
- Names: `Diskon Awal Tahun`, `Promo Kelas Online`, `Kelas Online Dasar` —
  generic Indonesian sample strings, no real merchant or customer.
- Credential: literal `Paste-Your-API-Key-Here`. No token, no key material.
- Hosts: `api.mayar.id` / `api.mayar.club` only — public documented endpoints,
  no internal hostname.
- Dates/values: round synthetic numbers (50000, 25000, 12, 0), plausible dates.

No leak. This complements C7 (inside T1), which greps for internal *identifiers*
but cannot distinguish a real merchant name from a fake one.

## 7. T6 — Documented-vs-example field parity (P2)

Scripted two-way set comparison between the keys of the 200 example and the
page's `<ResponseField name=…>` set (excluding the `Authorization` block, which
is a header not a response field):

```
example keys  : coupons createdAt data discountValue expiredAt hasMore id
                messages name nextStartingAfter products status statusCode totalUsage
ResponseFields: (identical set)
in example, not documented: []
documented, not in example: []
T6 PASS — exact two-way match
```

14/14 keys documented, 14/14 documented fields present in the example. No orphan
`ResponseField`, no undocumented key. This closes the gap that D6 leaves open
(D6 only asserts `statusCode` + `data` exist, not parity).

---

## 8. Exit criteria

All five plan exit criteria hold:

1. ✅ T1 diff empty; suite exit 1 with exactly the 16 baseline FAILs.
2. ✅ T2 exactly two changed content files; expected `docs.json` one-liner.
3. ✅ T3 JSON valid, slug first in group, file resolves.
4. ✅ T4/T5/T6 pass; divergences limited to the two documented ones.
5. ✅ G2/G3 remain recorded open source-side questions — non-blocking.

No fix was needed — nothing failed, so nothing was changed during Phase 14. The
working tree is byte-identical to what entered the phase.

---

## 9. Open items carried forward (non-gating)

Unchanged from the plan — none of these block Phase 14, all need a source-side
or future-feature answer.

| ID | Item | Owner |
|----|------|-------|
| G2 | `products[]` item fields beyond `id` not live-verified; disclosed in the in-page maintainer comment. No credentials available. | source-side |
| G3 | `limit` cap unknown — siblings document "maximum of `50`", this page says only "Defaults to `10`". Documenting an unverified cap would be worse than the gap. | source-side |
| G4 | Field-parity (T6) and heading-consistency (T4) are manual, so they do not protect future edits. Parent feature R3 still stands. | parent feature |
| G5 | No CI wiring for the gate on `api-reference-v2/**`. Parent feature R2. | parent feature |
| G6 | No real Mintlify render; C4/C5/C6 approximate a build. | accepted |
| bug-001 | 2 C2 orphan FAILs — `nameservice/create.mdx`, `nameservice/update.mdx`. | filed, `main`-side |
| bug-002 | 14 D1/D4/D5 FAILs — `saas/*`, `software/verify` on non-`/hl/v2` surfaces. | filed, `main`-side |

No new bug was found during execution, so nothing new was filed.
