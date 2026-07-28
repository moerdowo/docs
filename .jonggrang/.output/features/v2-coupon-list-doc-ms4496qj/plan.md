---
feature: v2-coupon-list-doc
branch: feat/v2-coupon-list-doc
base: "main"
work_type: SMALL
description: Add a V2 headless docs page for the paginated GET /hl/v2/coupons list endpoint and register it in navigation
created_at: 2026-07-28T03:47:18.499Z
---

# Plan: V2 Get List Coupon API Doc

## Approach
Add a single new Mintlify page at `api-reference-v2/discount/index.mdx` documenting the cursor-paginated coupon/discount-campaign list endpoint, following the exact structure already used by sibling V2 list pages (`api-reference-v2/bundling/index.mdx`) and the V2 discount pages: frontmatter (`title`, `openapi`, `description`), a maintainer note comment, `<RequestExample>` / `<ResponseExample>` blocks, a `<CodeGroup>` with Production/Sandbox base URLs, then Authorization, Query Parameters, and Response field documentation via `<ParamField>` / `<ResponseField>`. The endpoint is documented as the headless surface only — `https://api.mayar.id/hl/v2/coupons` with the `api.mayar.club` sandbox counterpart — not the `/mobile/v2` path from the source description. The response shape is transcribed verbatim from the supplied specification even where it diverges from the already-published `detail.mdx` (flat `coupons[]`, `totalUsage`, `products[]`, ISO-8601 `createdAt`/`expiredAt` instead of ms timestamps); `detail.mdx` is left untouched. Finally, register the new page first in the existing "Discount & Coupon" group in `docs.json`.

## Phases
1. Grounding & conventions pass — read the sibling V2 list page (`bundling/index.mdx`) and the V2 discount pages to lock down exact frontmatter keys, component usage, sandbox/production `<CodeGroup>` phrasing, and the synthetic-data / maintainer-note convention before writing.
2. Author the page — write `api-reference-v2/discount/index.mdx` covering endpoint URLs, Bearer auth, the five optional query parameters (`limit`, `startingAfter`, `status`, `search`, `productId`), the success envelope (`statusCode`, `messages`, `data`, `hasMore`, `nextStartingAfter`), nested `coupons[]` and `products[]` item fields, and the 400/500 error shapes.
3. Navigation wiring — add `api-reference-v2/discount/index` as the first entry of the "Discount & Coupon" group in `docs.json`, leaving the other four page entries and their order intact.
4. Validation & consistency sweep — verify JSON validity of `docs.json`, confirm the new slug resolves to a real file, check that all example identifiers/values are synthetic and no real merchant data or credentials leak, and confirm no other page or nav entry was modified.

## Key Decisions
- Headless-only surface: document `https://api.mayar.id/hl/v2/coupons` + `https://api.mayar.club/hl/v2/coupons`; the `/mobile/v2/coupons` variant from the source description is not published — per user clarification, the public docs site covers the headless API.
- Response shape transcribed as supplied, not reconciled with `detail.mdx`: the list endpoint returns a different projection (adds `status`, `discountValue`, `totalUsage`, `products`, ISO date strings). Per user clarification, `detail.mdx` stays unchanged; any divergence is a source-side question, not a docs edit.
- File placed at `api-reference-v2/discount/index.mdx` and listed first in its nav group — matches the `index` = list-endpoint convention already used by bundling, installment, invoice, and reqpayment groups.
- Cursor pagination documented explicitly: `nextStartingAfter` from a response is fed back as `startingAfter`, with `hasMore` as the loop terminator — the same framing used on other V2 list pages.
- V2 only: no corresponding page added under `api-reference/discount/` (V1), per user clarification.
- Status values (`active`, `inactive`, `expired`, `upcoming`) are listed as the accepted enum without inventing precise transition semantics, since the user did not supply verbatim definitions.

## Out of Scope
- The MCP tool integration (`get_coupons_list`, section 7 of the source description) — REST endpoint page only.
- Any edit to `api-reference-v2/discount/detail.mdx`, `create.mdx`, `validate.mdx`, or `check.mdx`.
- A V1 equivalent page under `api-reference/discount/`.
- Documenting the `/mobile/v2/coupons` mobile surface.
- Adding or modifying entries in `api-reference/openapi.json` (V2 pages use a pseudo `openapi:` frontmatter path not backed by a spec file; the new page follows the same existing convention).
- Reconciling the timestamp-format inconsistency (ms integers vs ISO strings) across V2 discount pages.

## Dependencies
- Existing V2 docs conventions in `api-reference-v2/bundling/index.mdx` (cursor-paginated list page template) and `api-reference-v2/discount/*.mdx` (auth block, `<CodeGroup>` endpoint block, maintainer-note comment, synthetic example data).
- `docs.json` navigation — the "Discount & Coupon" group under the V2 API reference tab.
- Mintlify MDX components already in use across the site: `RequestExample`, `ResponseExample`, `CodeGroup`, `ParamField`, `ResponseField`.

<!-- jonggrang:clarifications -->
## Clarifications
_Captured from the planning Q&A:_

Goal: Add a Mintlify docs page to the Mayar Docs site for the paginated 'get list coupon' endpoint (GET /v2/coupons, cursor-based, returning discount campaigns with their coupon codes), wired into docs.json navigation alongside the existing V2 Discount pages (create/detail/validate/check).

- **Which API surface and base URL should the page document?** → Headless only — document as GET https://api.mayar.id/hl/v2/coupons (+ api.mayar.club sandbox)
- **How should I treat the response shape you supplied, given it conflicts with the already-published coupon detail page?** → Document exactly as supplied; leave detail.mdx untouched
- **Where should the page live in the file tree and docs.json navigation?** → api-reference-v2/discount/index.mdx, first in the existing Discount group
- **Is section 7 (MCP tool `get_coupons_list`) in scope for this docs change?** → Out of scope — REST endpoint page only
- **Should the V1 docs (api-reference/discount/) also get a list page, and are there exact semantics for the four status values (what makes a campaign 'upcoming' vs 'expired' vs 'inactive') I should state verbatim?** → only implement in v2
