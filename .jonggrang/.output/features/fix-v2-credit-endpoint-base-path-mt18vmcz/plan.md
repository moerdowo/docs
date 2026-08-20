---
feature: fix-v2-credit-endpoint-base-path
branch: feat/fix-v2-credit-endpoint-base-path
base: "main"
work_type: BUGFIX
description: Correct the V2 Credit (Membership / Usage) endpoint paths from /hl/v2/credit/* to /credit/v2/credit/*
created_at: 2026-08-20T08:12:17.596Z
---

# Plan: Fix V2 Credit Endpoint Base Path

## Approach
The seven pages under `api-reference-v2/credit/` document their endpoints on the shared V2 host prefix `/hl/v2/credit/...`, but the credit service is actually served from its own prefix — `/credit/v2/credit/...` — mirroring the V1 pages that already use `/credit/v1/credit/...`. This is a documentation-only correction: rewrite the host path segment in every place it appears on those pages (the `curl` request example, and the Production and Sandbox entries of the Endpoint `<CodeGroup>`) while leaving the route suffix, parameters, payloads, and response bodies untouched. The V2 `introduction.mdx` base URL (`https://api.mayar.id/hl/v2`) stays as-is, since the credit service is a documented deviation of the same kind already established by the `saas/v2` and `software/v2` pages, which state their own full base inline with no extra note. No nav or spec changes are needed: `docs.json` references page slugs only, and the `openapi:` frontmatter values are internal placeholder identifiers, not real URLs.

## Phases
1. Grounding — confirm the exact target prefix and every occurrence site: enumerate the 7 credit pages, the 3 URL occurrences per page, and verify no other page, guide, or config in the repo embeds a `hl/v2/credit` URL.
2. Rewrite the credit endpoint URLs — apply the `hl/v2/credit` → `credit/v2/credit` substitution across all `api-reference-v2/credit/*.mdx` pages, for both the `api.mayar.id` (Production) and `api.mayar.io` (Sandbox) hosts.
3. Consistency sweep — re-grep for residual `hl/v2/credit` strings, confirm each page's curl example and Endpoint block agree with each other and with the corresponding V1 page's route suffix, and confirm nothing outside the credit pages changed.
4. Validation — check MDX structure is intact (frontmatter, `<RequestExample>` / `<ResponseExample>` / `<CodeGroup>` fences unbroken), `docs.json` still parses, and the Credit nav group renders the same page set.

## Key Decisions
- Scope the change to the host prefix only: `hl/v2/credit` → `credit/v2/credit`, preserving each route suffix (`/customer/balance`, `/customer/spend`, `/customer/add-credit`, `/customer/paginate-credit-history/...`, `/membership/customer/regist`, `/credit-usage/customer/regist`, `/generate/immutable/checkout`) exactly as documented today — the reported defect is the prefix, not the routes.
- Apply the correction to Sandbox (`api.mayar.io`) as well as Production (`api.mayar.id`); the two always mirror each other in this repo, and leaving Sandbox on the old prefix would create a new inconsistency.
- Leave `api-reference-v2/introduction.mdx` unchanged — `/hl/v2` remains the general V2 base, and per-service bases are documented inline on the page (existing `saas/v2` and `software/v2` precedent).
- Do not add explanatory notes or restructure the Credit pages; a silent, minimal correction keeps the diff reviewable and matches how sibling deviating services are presented.
- Treat the user-supplied path as authoritative: the backend source is not reachable from this workspace, so the target prefix is taken from the feature request and cross-checked against the V1 `credit/v1/credit/*` pages rather than against server routing code.

## Out of Scope
- The V1 pages under `api-reference/creditbasedproduct/` and `api-reference/usagebasedmembership/` — they already document `credit/v1/credit/*` correctly.
- Any change to the general V2 base URL in `api-reference-v2/introduction.mdx`, or to other V2 sections that legitimately use `/hl/v2`.
- Rewriting request/response schemas, parameter tables, error sections, or example payloads on the credit pages.
- Nav restructuring in `docs.json`, page renames, or new pages.
- Changes to `api-reference/openapi.json` or the `openapi:` frontmatter identifiers.
- Verifying the endpoints against a live API or the backend repository.

## Dependencies
Existing `api-reference-v2/credit/*.mdx` pages and their established page shape (curl `<RequestExample>` + Endpoint `<CodeGroup>` with Production/Sandbox entries); the V1 credit pages as the reference for the `credit/vN/credit/*` prefix form; the `saas/v2` and `software/v2` V2 pages as the precedent for a per-service base that deviates from `/hl/v2`; the `Credit (Membership / Usage)` nav group in `docs.json`.
