# Phase 12 — Code Quality Review

Feature: `v2-coupon-list-doc-ms4496qj`
Date: 2026-07-28
Scope reviewed: `api-reference-v2/discount/index.mdx` (new, +221), `docs.json` (+1 line)

## Verdict

PASS. One consistency defect found and fixed; two low-severity observations left open
(both need information this feature does not have).

## Method

Compared the new page field-for-field against the four sibling V2 cursor-paginated list
pages (`bundling`, `installment`, `invoice`, `reqpayment` `index.mdx`) and against the
sibling discount pages (`detail`, `create`). Checked frontmatter shape, maintainer-comment
convention, tag ordering/spacing, code-fence titles, heading text, `ParamField`/
`ResponseField` attribute style, type-string vocabulary, JSON validity, trailing newline,
and nav registration.

## Findings

### F1 — CodeGroup endpoint URLs omitted `?limit=10` — FIXED

The `Endpoint:` `<CodeGroup>` block listed bare
`https://api.mayar.{id,club}/hl/v2/coupons`. Three of the four sibling list pages —
including `bundling/index.mdx`, the page this file was authored against — carry the
`?limit=10` suffix on both Production and Sandbox lines (`reqpayment/index.mdx` is the lone
exception). Fixed: both lines now read `.../hl/v2/coupons?limit=10`, matching the curl
example in `<RequestExample>`.

### F2 — `limit` ParamField omits the documented `50` cap — OPEN (low)

All four sibling list pages describe `limit` as
"Number of items to return per page. Defaults to `10`, with a maximum of `50`."
This page says only "Defaults to `10`." Either the cap applies to `/hl/v2/coupons` too (the
page is then incomplete) or it genuinely does not (an intentional divergence that the
maintainer comment should record, the way the ISO-8601 divergence is recorded). Left
unchanged deliberately — asserting a `50` cap that was not in the supplied source spec
would be inventing API behaviour. Needs a source-side answer.

### F3 — cursor-pagination `<Note>` dropped in Phase 9 — OPEN (informational)

Task-002 acceptance criterion #9 required "a short explicit note on cursor pagination: feed
`nextStartingAfter` back as `startingAfter` and keep looping while `hasMore` is true".
Phase 9 (simplification) removed that `<Note>` block. The removal is convention-aligned —
no sibling V2 list page carries such a note — but the "keep looping while `hasMore` is
true" semantics are now only implied, spread across the `startingAfter` ParamField and the
`hasMore` / `nextStartingAfter` ResponseFields. Recorded for traceability, not re-added:
re-adding it would make this the only list page in the corpus with one.

## Checks that passed

- Frontmatter: `title` / `openapi` / `description`, all double-quoted, same order as siblings.
  `openapi: "GET /endpointdiscountv2/index"` follows the corpus-wide synthetic-slug pattern.
- Maintainer JSX comment placed immediately after frontmatter; states the source, the
  detail.mdx divergence, the unverified `products` fields, headless-only scope, synthetic data.
- Tag ordering `<RequestExample>` → `<ResponseExample>` → `Endpoint:` `<CodeGroup>` →
  `## Authorization` → `## Query Parameters` → `## Response`: matches siblings exactly,
  including the double blank line between the Production and Sandbox fences.
- Authorization documented as `<ResponseField name="Authorization" type="string" required>`
  with the `Authorization | Bearer Paste-Your-API-Key-Here` example — the actual corpus
  convention (task-002 called for `<ParamField header=...>`; no page in the repo uses that).
- `### Main Structure (Root)` / `### data Structure (Object)` /
  `### coupons Structure (Array Of Object)` / `### coupons.products Structure (Array Of Object)`
  heading chain matches `discount/detail.mdx`, the right template for the object-wrapped
  `data` shape.
- Type vocabulary (`string<uuid>`, `array of object`, `string | null`) matches corpus usage.
- All 3 embedded `json` blocks parse. `docs.json` parses; diff is exactly the one added line,
  first in the V2 Discount & Coupon group.
- No real merchant/customer data, no live keys; ids are synthetic UUID-shaped values.
- No `/mobile/v2` reference. Trailing newline present, as on every other page.

## Regression gate

Re-ran the combined suite (`validate-v2-docs.sh`, C1–C8 + D1–D7) after the F1 fix.
Exit 1, 16 FAILs — byte-identical to the task-001 and Phase 11 baselines
(C2 ×2 nameservice orphans; D1 ×8 / D4 ×4 / D5 ×2 on saas + software pages).
Zero FAIL lines name `api-reference-v2/discount/` or `docs.json`.
