# Phase 11 — Domain Compliance: v2-coupon-list-doc

Feature: `v2-coupon-list-doc-ms4496qj`
Diff under review vs `main`: `api-reference-v2/discount/index.mdx` (new, 208 lines) + `docs.json` (+1 nav entry). Nothing else in the doc corpus changed.

## Gate run

```
bash .jonggrang/.output/features/api-v2-reference-docs-mqyl9hub/validate-v2-docs.sh
→ exit 1, 16 FAIL lines
```

Exit 1 is the **recorded pre-existing baseline**, not a regression. Baseline was captured on this branch with an empty `git diff main -- api-reference-v2/ docs.json` (see `.jonggrang/progress.txt`, task-001 addendum). The FAIL set is byte-identical to that baseline:

| Check | Count | Pages |
|---|---|---|
| C2 orphan .mdx not in nav | 2 | `api-reference-v2/nameservice/{create,update}.mdx` |
| D1 missing prod + sandbox base URL | 8 | `saas/{activate,deactivate,verify}.mdx`, `software/verify.mdx` |
| D4 no `<RequestExample>` curl on /hl/v2 | 4 | same 4 pages |
| D5 envelope missing message/messages | 2 | `saas/verify.mdx`, `software/verify.mdx` |

**Exit criterion met: zero FAIL lines name `api-reference-v2/discount/` or `docs.json`.** All 4 D-failing pages and both C2 pages are untouched by this branch. The gate was not weakened — the suites ran unmodified.

## D1–D7 on the new page

The new page is `discount/index.mdx`; stem `index` is not in the suite's `OVERVIEW` exemption set (`introduction`, `statuscode`, `rate-limit`), so it is one of the 82 endpoint pages the per-page checks assert against. Corpus grew 84 → 85 files / 81 → 82 endpoint pages, and every "PASS … on all 82 endpoint pages" line therefore includes it. It is not silently skipped.

- **D1** both `https://api.mayar.id/hl/v2/coupons` and `https://api.mayar.club/hl/v2/coupons` in the `<CodeGroup>`; no `/hl/v1` leak. PASS
- **D2** `openapi: "GET /endpointdiscountv2/index"`. PASS
- **D3** `Authorization` + `Bearer` documented. PASS
- **D4** `<RequestExample>` curl hits `/hl/v2`. PASS
- **D5** envelope `statusCode` + `messages` (plural only, never both). PASS
- **D6** `statusCode` ResponseField present; `data` ResponseField present as required since the envelope carries a `data` object. PASS
- **D7** no stray closing tags in prose. PASS
- **C7** leak-grep clean — URL written as `/hl/v2/coupons`, never `/api/v2/`; no internal handler names, `@mayarid`, or `process.env`.

## Corpus-convention conformance (beyond the automated checks)

Compared against the 5 sibling V2 list pages (`installment`, `reqpayment`, `invoice`, `bundling` `index.mdx`):

- **Section skeleton** identical and in corpus order: `<RequestExample>` → `<ResponseExample>` → `Endpoint:` + `<CodeGroup>` → `## Authorization` → `## Query Parameters` → `## Response` → `### Main Structure (Root)` → `### data Structure (...)` → nested `### <parent>.<child> Structure (...)`.
- **`openapi:` frontmatter** follows the corpus-wide synthetic slug convention `<VERB> /endpoint<domain>v2/<page>` — it is deliberately *not* the real path. `GET /endpointdiscountv2/index` matches `GET /endpointbundlingv2/index` and `GET /endpointinstallmentv2/index`.
- **Pagination vocabulary** matches: `limit` (default 10) + `startingAfter` query params; `hasMore` + `nextStartingAfter` root response fields, with `nextStartingAfter` typed `string | null`.
- **`<ParamField query="x" path="x">`** dual-attribute form matches every other list page.
- **Authorization block** wording verbatim from the corpus template.
- **curl shape** `curl --request GET 'https://api.mayar.id/hl/v2/<res>?limit=10' \ --header 'Authorization: Bearer Paste-Your-API-Key-Here'` — identical to all 5 siblings.
- **Error examples** 400 and 500 with `{statusCode, messages, data: null}`, matching corpus.

### Two deliberate, documented divergences

1. **`data` is an object wrapping a `coupons` array**, where every other V2 list page has `data` as an array-of-object directly. This is source-side (the list projection differs from `detail.mdx`: flat `coupons` array with `status`/`discountValue`/`totalUsage`/`products`, ISO 8601 dates instead of millisecond timestamps). D5/D6 both permit it; the nested `### data Structure (Object)` → `### coupons Structure (Array Of Object)` heading chain follows the same nesting convention `invoice`/`bundling` use for their sub-objects. Recorded in the maintainer comment at the top of the file.
2. **Field description reads "Status code from API."** The corpus is split on this long-standing typo, not uniform: 35 pages read "form", 16 read "from". Re-measured in Phase 16 — the original claim here ("all siblings carry the typo … corrected on the new page only … the other 81 pages") was generalised from a two-page grep and is wrong. The accurate picture: all four *list-page* siblings (`bundling`/`installment`/`invoice`/`reqpayment` `index.mdx`), which supplied this page's structural template, read "form"; but all four *discount-group* siblings (`create`/`detail`/`validate`/`check`), which a reader actually navigates between, already read "from". The new page therefore matches its own nav group exactly and diverges only from the list-page template. Fixing the 35 "form" pages remains out of scope.

Neither divergence is a compliance defect. Both are annotated in-file.

## Open item (carried, not introduced)

The maintainer comment flags that the `products[]` item fields beyond `id` are transcribed from the supplied source spec rather than captured from a live response, and should be confirmed against a live call. This is a source-fidelity caveat already disclosed in the page, not a domain-pattern violation.

## Verdict

**PASS.** The new page and nav entry are fully domain-compliant. The gate's exit 1 is entirely attributable to the 16 pre-existing baseline failures on pages this feature does not touch.
