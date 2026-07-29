# Test Plan — V2 Get List Coupon doc page

- **Feature**: `v2-coupon-list-doc-ms4496qj`
- **Branch**: `feat/v2-coupon-list-doc`
- **Work type**: SMALL
- **Phase**: 13 — test-planning
- **Date**: 2026-07-28
- **Status**: READY for Phase 14 (test-execution)

---

## 1. What "testing" means here

The deliverable is documentation, not code: one new Mintlify page plus one nav
line.

```
git diff main --stat -- api-reference-v2/ docs.json
 api-reference-v2/discount/index.mdx | 208 ++++++++++++++++++++++++
 docs.json                           |   1 +
 2 files changed, 209 insertions(+)
```

There is no runtime, no unit-under-test, and no in-repo test framework
(`test command: echo 'no test command configured'`). Testing is therefore
**static validation as test**, reusing the executable suites already built for
the parent feature — nothing new is authored here:

| Layer | Suite | Checks |
|-------|-------|--------|
| Structural | `validate-v2-docs.py` | C1–C8 |
| Domain | `domain-compliance-v2-docs.py` | D1–D7 |
| Combined entrypoint | `validate-v2-docs.sh` | runs both, ANDs exit codes |

All three live in
`.jonggrang/.output/features/api-v2-reference-docs-mqyl9hub/`.
They are stdlib-only, hermetic (no network/credentials), and deterministic.

### The one thing that makes this feature's testing non-obvious

**The absolute gate is red before this branch touches anything.** 16 FAILs
exist on `main` (bug-001, bug-002 in `bugs.md`) on pages this feature does not
modify. So `exit 0` is *not* the pass criterion — it is unreachable without
fixing out-of-scope pages, which this feature is explicitly not allowed to do.

The pass criterion is a **delta against a recorded baseline** (§4). This is the
central design decision of the plan; §6 covers why it is safe and where it is
weak.

---

## 2. Objectives & risk-based priorities

| Pri | Objective (risk controlled) | Enforced by |
|-----|-----------------------------|-------------|
| P0 | **No regression** — the new page/nav entry introduces zero new FAIL | T1 baseline delta |
| P0 | **Site still builds** — `docs.json` valid, JSX balanced, fences paired, embedded JSON parses | C1, C4, C5, C6 |
| P0 | **No leak** — no internal identifiers, no real merchant/customer data, no live keys | C7, T5 |
| P0 | **No collateral damage** — no page other than the new one changed; V1 tab untouched | C8, T2 |
| P1 | **Endpoint contract correct** — `/hl/v2/coupons` prod + sandbox, Bearer auth, curl example, `statusCode`+`messages` envelope | D1, D3, D4, D5 |
| P1 | **Page is reachable** — nav↔file 1:1 for the new slug, listed first in its group | C2 (new-page portion), T3 |
| P2 | **Field docs complete & corpus-consistent** — every documented response key has a `ResponseField`, headings match sibling list pages | D2, D6, D7, T4 |
| P2 | **Scope honoured** — headless only, no `/mobile/v2`, `detail.mdx` untouched | T2, T6 |

---

## 3. Scope

**In scope (under test)**
- `api-reference-v2/discount/index.mdx` — the new page.
- `docs.json` — the single added nav entry, and non-change of everything else.
- The rest of the corpus **as a regression surface only** (must not get worse).

**Out of scope**
- Fixing the 16 pre-existing FAILs (bug-001 nameservice orphans, bug-002
  saas/software non-`/hl/v2` surfaces). Both are filed, both are `main`-side.
- Semantic fidelity of the response example against the live API. The page is
  explicitly flagged REPRESENTATIVE in its maintainer comment; the `products[]`
  item fields beyond `id` are transcribed from the supplied spec, not captured.
  No credentials for a live call are available at test time.
- A real Mintlify build (`mint build`) — no build tooling in-repo.
- `/mobile/v2/coupons`, the MCP `get_coupons_list` tool, and any V1 page — all
  out of the feature's scope by plan decision, so nothing to test.

---

## 4. Test cases

`T1` is the gate. `T2`–`T6` are cheap manual/CLI assertions that cover what the
automated suites structurally cannot.

### T1 — Baseline-delta gate (P0, automated, blocking)

**Fixture:** `gate-baseline.txt` in this directory — the 16 FAIL lines,
captured from this working tree on 2026-07-28, sorted and whitespace-normalised.

```bash
bash .jonggrang/.output/features/api-v2-reference-docs-mqyl9hub/validate-v2-docs.sh 2>&1 \
  | grep -E '^\s*FAIL' | sed 's/^ *//' | sort \
  > /tmp/gate-now.txt
diff .jonggrang/.output/features/v2-coupon-list-doc-ms4496qj/gate-baseline.txt /tmp/gate-now.txt \
  && echo "T1 PASS — FAIL set identical to baseline"
```

**Pass:** `diff` is empty (exit 0). Equivalently, and this is the criterion to
state in the report:
1. no FAIL line mentions `api-reference-v2/discount/` or `docs.json`; **and**
2. the FAIL count is exactly 16 and the set is unchanged — no baseline FAIL
   silently *disappeared* either (a vanished FAIL means someone edited an
   out-of-scope page, which is also a scope violation).

**Fail:** any added or removed line. Triage: new line naming the new
page/`docs.json` → real defect, fix the page. New line naming another page →
collateral damage, revert it. Removed line → out-of-scope edit crept in.

> Note the whole-suite exit code stays **1** on success. Do not "fix" this by
> weakening a check; record the exit code and the delta instead.

### T2 — Change-surface containment (P0, automated)

```bash
git diff main --stat -- api-reference-v2/ docs.json
git diff main -- docs.json
```
**Pass:** exactly two files (`discount/index.mdx` new, `docs.json` +1 line, 0
deletions); the `docs.json` hunk is a single added `"api-reference-v2/discount/index"`
line. `detail.mdx` / `create.mdx` / `validate.mdx` / `check.mdx` unmodified.
(C8 already guards the V1 tab; this covers the V2 side.)

### T3 — Nav resolution & position (P1, manual + CLI)

```bash
python3 -m json.tool docs.json > /dev/null && echo "json ok"
grep -n 'api-reference-v2/discount/' docs.json
test -f api-reference-v2/discount/index.mdx && echo "slug resolves"
```
**Pass:** JSON valid; the new slug is the **first** entry in the V2
"Discount & Coupon" group, followed by the original four in their original
order; the slug maps to a file on disk.

### T4 — Corpus-consistency spot check (P2, manual)

Diff the new page's skeleton against the four sibling V2 list pages
(`bundling`, `installment`, `invoice`, `reqpayment` `index.mdx`): tag order,
`Endpoint:` `<CodeGroup>` with `?limit=10` on both prod and sandbox lines, the
double blank line between the two fences, the `Authorization` block form
(`<ResponseField name="Authorization" …>` — *not* `<ParamField header=…>`), and
the heading chain `### Main Structure (Root)` → `### data Structure (Object)` →
`### coupons Structure (Array Of Object)` → `### coupons.products Structure (Array Of Object)`.
**Pass:** no divergence except the two knowingly documented in
`domain-compliance.md` §"Two deliberate divergences" (object-wrapped `data`;
"Status code from API." typo fix).

### T5 — Data-safety read-through (P0, manual)

Read every literal value in the three JSON examples and the curl. **Pass:** all
ids are synthetic UUID-shaped, names are synthetic Indonesian sample strings, the
key is the literal `Paste-Your-API-Key-Here`; no real merchant/customer data, no
token, no internal hostname. (C7 greps for internal *identifiers*; it cannot tell
a real merchant name from a fake one — this is the human half of the P0 leak
objective.)

### T6 — Documented-vs-example field parity (P2, manual)

Every key in the 200 example has a matching `ResponseField`, and vice versa:
root `statusCode`/`messages`/`data`/`hasMore`/`nextStartingAfter`; `data.coupons`;
item `id`/`name`/`status`/`discountValue`/`totalUsage`/`createdAt`/`expiredAt`/`products`;
`products` item `id`/`name`. **Pass:** exact two-way match, no orphan field, no
undocumented key. (D6 only asserts `statusCode` + `data` exist — it does not
check parity, so this gap is covered by hand.)

---

## 5. Traceability

| Objective (§2) | Covered by |
|---|---|
| No regression | T1 |
| Site builds | C1, C4, C5, C6 (inside T1) |
| No leak | C7 (inside T1) + T5 |
| No collateral damage | C8 (inside T1) + T2 |
| Endpoint contract | D1, D3, D4, D5 (inside T1) |
| Page reachable | C2 (inside T1) + T3 |
| Field docs complete | D2, D6, D7 (inside T1) + T4, T6 |
| Scope honoured | T2, T6 |

Every P0/P1/P2 objective has at least one executing check. No objective is
unprotected.

**Measured entry state (2026-07-28, this working tree):** structural 7/8 PASS
(C2 fails ×2, pre-existing), domain 4/7 PASS (D1 ×8, D4 ×4, D5 ×2, all
pre-existing), 85 pages / 82 endpoint pages / 94 JSON blocks, suite exit 1.
The new page is inside all 85/82 counts — it is not exempted (`index` is not in
the suite's `OVERVIEW` exemption set), so every "PASS … on all 82 endpoint
pages" line includes it. Delta vs `main`: +1 page, +1 endpoint page, +3 JSON
blocks.

---

## 6. Gaps & residual risk

Stated explicitly rather than silently accepted.

| ID | Gap | Status |
|----|-----|--------|
| G1 | **A red baseline weakens the gate.** With 16 known FAILs, a genuinely new FAIL is detected by *diff*, not by exit code. If the fixture is ever regenerated on a dirtier tree, a real defect gets absorbed into "baseline". | Mitigated: the fixture is committed with this plan and its provenance is stated (captured 2026-07-28 with the feature's diff already applied — so it is a *post-change* baseline, and T1 additionally asserts no FAIL names the changed files). Do not regenerate it during Phase 14. |
| G2 | **Response example not live-verified.** `products[]` fields beyond `id` come from the supplied spec. | Accepted, disclosed in-page via the maintainer comment. No credentials available. Would need a source-side confirmation to close. |
| G3 | **`limit` cap unknown.** All four sibling pages document "maximum of `50`"; this page says only "Defaults to `10`" because the supplied spec did not state a cap. | Open, non-gating (code-quality F2). Documenting an unverified cap would be worse than the gap. Needs a source-side answer. |
| G4 | **No field-parity or heading-consistency check in the suites.** T4/T6 are manual, so they do not protect future edits. | Accepted for a SMALL feature; the parent feature's R3 (add heading-consistency to the validator) still stands. |
| G5 | **No CI wiring.** Nothing runs the gate automatically on future edits to `api-reference-v2/**`. | Deferred, non-gating (parent feature R2). |
| G6 | **No real render.** C4/C5/C6 approximate a Mintlify build. | Accepted — no build tooling in-repo. |
| bug-001 / bug-002 | Pre-existing corpus defects producing all 16 baseline FAILs. | Open, filed, out of scope, non-gating for this feature. |

---

## 7. Execution plan (Phase 14)

**Entry criteria:** working tree on `feat/v2-coupon-list-doc`; `main` ref present
(C8 oracle); `gate-baseline.txt` present and unmodified.

**Order:** T1 first (it is the blocking gate and the most likely to surface
anything), then T2, T3, then the manual T4–T6.

**Exit criteria — all must hold:**
1. T1 diff empty; suite exit 1 with exactly the 16 baseline FAILs.
2. T2 shows exactly two changed files and the expected `docs.json` one-liner.
3. T3 JSON valid, slug first in group, file resolves.
4. T4, T5, T6 pass with divergences limited to the two already documented.
5. G2/G3 remain recorded as open source-side questions — they do **not** block.

**On failure:** fix the new page (the only file this feature owns) and re-run.
If a check is judged a false positive, record the rationale in
`test-execution.md`; do not edit the suites to make the gate green.

**Report to:** `.jonggrang/.output/features/v2-coupon-list-doc-ms4496qj/test-execution.md`.
