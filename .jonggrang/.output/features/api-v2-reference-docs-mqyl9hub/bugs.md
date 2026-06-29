# Bug Reports — api-v2-reference-docs

## [resolved] bug-001 · 2026-06-29T03:00:24.339Z · fixed in Phase 11 (domain-compliance) 2026-06-29
api-reference-v2/invoice/create.mdx and invoice/edit.mdx (task-013) each end with a stray '</content>' closing tag that has no matching opening tag; correct V2 pages (product/membership groups) do not include it. Likely an authoring artifact that may render literally in Mintlify.

RESOLUTION (Phase 11): The domain-compliance suite's stray-closing-tag check (D7) found the
artifact was BROADER than first reported — a trailing `</content>` on FIVE invoice pages
(create, detail, edit, filter, index) plus an additional sibling `</invoke>` tool-call artifact
on invoice/index.mdx (after its `</content>`). The structural suite's C4 tag-balance never
caught these because `content`/`invoke` are not among its 7 balanced JSX components. All 6 stray
lines were removed (true content on every page ends at the final `</ResponseField>`). Verified:
`grep -rn '</content>\|</invoke>' api-reference-v2/` is now CLEAN, domain-compliance D7 PASS,
and the structural suite remains 8/8 green.

## [open] bug-002 · 2026-06-29T03:59:53.735Z
V2 Reviews statistics endpoints GET /hl/v2/products/{paymentLinkId}/reviews/stats and GET /hl/v2/merchants/reviews/stats return HTTP 500 with messages 'gtFetch(...).then is not a function' on the cache-miss path (the total-reviews fetch is awaited as a non-promise then .then is chained on its result). Both stats shapes were documented as REPRESENTATIVE from source since they could not be captured live. Upstream API defect, not a docs-repo issue.
