---
feature: api-v2-reference-docs
branch: feat/api-v2-reference-docs
base: "main"
work_type: LARGE
description: Add an API V2 Reference tab with V2 endpoint docs and rename the existing tab to API V1 Reference
created_at: 2026-06-26T10:24:43.681Z
depth: deep
jonggrang-output: true
---

# Plan: API V2 Reference Documentation

## Approach
Introduce a dedicated top-level `api-reference-v2/` folder that holds all V2 documentation (one `.mdx` per endpoint plus three group pages), wired into `docs.json` as a new `tabs[2]` "API V2 Reference" tab whose first group is an "API documentation" group adapted for V2. The existing `tabs[1]` label is renamed "API Reference" → "API V1 Reference" with its pages and nav entries left byte-identical, so no V1 file is ever opened for edit. Each V2 page reuses the proven V1 page template verbatim (RequestExample/ResponseExample/CodeGroup/ParamField/ResponseField) with the `/hl/v2` base URL, the `{statusCode, messages, data}` envelope, and the per-endpoint `message`/`messages` quirk preserved. Response shapes come from live prod (provided key) for safe GET reads and are derived-and-flagged for writes, with all PII scrubbed and zero internal identifiers exposed.

## Phases
1. Structural scaffold — Edit `docs.json`: rename `tabs[1].tab` "API Reference" → "API V1 Reference" (pages untouched), append `tabs[2]` "API V2 Reference" with a seeded "API documentation" group; create the `api-reference-v2/` folder. Validate JSON with `python3 -m json.tool`.
2. API documentation group (V2) — Author V2-adapted `introduction.mdx`, `statuscode.mdx`, `rate-limit.mdx` (base URL `https://api.mayar.id/hl/v2`, envelope `{statusCode, messages, data}`) and wire them into the new group.
3. Core/high-value resource groups — Products & payment links, invoices, payments, transactions, customers, memberships first (most-used, V2-distinct). One page per endpoint from the V1 template; capture real prod shapes for GET reads with the provided key and scrub PII.
4. Remaining resource groups — QR/payment-channels, balances, installments, coupons/discount, bundling, name-services, webhooks, reviews. Derive write-endpoint shapes from source plus representative values and flag as representative.
5. Sandbox & sample fidelity pass — Document sandbox URLs by pattern (prod key 401s on `api.mayar.club`); ensure each page preserves its exact `message` vs `messages` envelope; replace any captured PII with synthetic example values matching V1 style.
6. Validation & leak-guard — Extend the documentation-validation suite: `docs.json` validity, nav↔file 1:1 (no orphans/missing), frontmatter presence, JSX tag balance, code-fence parity, embedded-JSON parse, plus a negative grep that fails if any internal identifier appears under `api-reference-v2/**`.

## Key Decisions
- Decision: Use a dedicated top-level `api-reference-v2/` folder (not nested under `api-reference/`) — guarantees V1 files are never edited and gives the leak-grep a clean root.
- Decision: Rename only `tabs[1].tab` label; leave all V1 pages and their nav entries byte-identical.
- Decision: Mirror the V1 group taxonomy/names for V2 groups so the new tab is consistent and navigable.
- Decision: One `.mdx` per endpoint (preserve V1 granularity), reusing the V1 page template verbatim with the `/hl/v2` base URL.
- Decision: Source response shapes from live prod (provided key) for safe GET reads; derive write shapes from source and flag as representative; scrub all PII to synthetic values.
- Decision: Preserve the `message` (singular, writes/errors) vs `messages` (plural, reads) envelope quirk per endpoint — never normalize.
- Decision: Keep the cosmetic `openapi:` frontmatter convention (V2 variant) or omit; do NOT wire pages to the stock `openapi.json` Plant Store sample.
- Decision: Document the sandbox base URL (`https://api.mayar.club/hl/v2`) by pattern, matching V1 precedent, since the prod key cannot authenticate against sandbox.
- Decision: Exclude the three app-level "MCP" routes (`/v2/customer-detail`, `/v2/unpaid-transactions`, `/v2/product-members`) pending maintainer confirmation.

## Affected Areas
- `docs.json` — rename `tabs[1].tab` and append `tabs[2]` "API V2 Reference" with its groups (the navigation tree).
- New folder `api-reference-v2/` — one `.mdx` per V2 endpoint (~60), mirroring the V1 group structure.
- New `api-reference-v2/introduction.mdx`, `api-reference-v2/statuscode.mdx`, `api-reference-v2/rate-limit.mdx` — the V2 "API documentation" group, base URL `https://api.mayar.id/hl/v2`.
- Existing `api-reference/**` V1 pages — NOT modified (only the tab label changes); these are the copyable template (`api-reference/invoice/create.mdx`, `api-reference/membership/getmemberdetail.mdx`, etc.).
- `api-reference/openapi.json` — left as the stock cosmetic sample; not wired.
- Validation script under `.jonggrang/.output/` — extended with V2 nav↔file and leak-guard checks.

## Risks
- Risk: Large scope (~60 endpoints across ~18 groups) is unrealistic in one pass — Mitigation: phase by resource group, prioritizing the V2-distinct/most-used groups first.
- Risk: Accidental V1 content drift — Mitigation: dedicated `api-reference-v2/` folder so no V1 file is ever opened; rename the tab label only.
- Risk: Normalizing the `message`/`messages` envelope — Mitigation: verify each endpoint against source/live response and mirror verbatim per page.
- Risk: Leaking internal identifiers (handler/function/variable names, internal paths, `@mayarid/*` packages, GraphQL/Redis/env names) — Mitigation: negative grep over `api-reference-v2/**` in the validation suite; publish only the public REST surface.
- Risk: Sandbox samples blocked (prod key 401s on `api.mayar.club`) — Mitigation: document sandbox URLs by pattern per V1 precedent; capture real shapes from prod for safe GET reads.
- Risk: Live prod data is a real merchant's — Mitigation: scrub all PII (emails/phones/names/IDs) to synthetic values matching V1 style before publishing.
- Risk: `docs.json` has irregular indentation — Mitigation: keep edits valid JSON and validate with `python3 -m json.tool` after each change.

## Alternatives Considered
- Option 2 (Nest V2 under `api-reference/v2/`): rejected — physically interleaves V2 with V1, raising the chance of accidentally editing a V1 file and preventing the leak-grep/validation from cleanly targeting "V2 only" by folder root, with no upside over a dedicated folder.
- Option 3 (Single combined page per group): rejected — breaks the established 1-endpoint-per-page V1 convention, makes the two tabs feel inconsistent, harms deep-linking, bloats ParamField/ResponseExample blocks, and breaks the nav↔file 1:1 validation pattern.

## Out of Scope
- Any modification to V1 page content under `api-reference/**` (only the tab label changes).
- The three app-level "MCP"-oriented `/v2/*` routes (customer-detail, unpaid-transactions, product-members) — possibly internal; need maintainer sign-off.
- Wiring a real OpenAPI spec to `openapi.json` (stock Mintlify sample; left cosmetic).
- Capturing live sandbox response samples (blocked: prod key 401s on `api.mayar.club`).
- Exposing any internal service identifiers (function/variable/handler names, internal paths, `@mayarid/*` packages, GraphQL query names, Redis/session internals, env var names).
- The unmerged membership-only `feat/membership-v2-api-docs` branch and its `membershipv2/` pages — superseded by this full-surface V2 effort.
- Adding build/test/lint tooling beyond the existing documentation-validation script.

## Dependencies
- Mintlify docs site (`docs.json` `$schema: mintlify.com/docs.json`, theme `mint`) with components `<RequestExample> <ResponseExample> <CodeGroup> <ParamField> <ResponseField> <Note> <Warning>`.
- The V1 per-endpoint page template and `docs.json` tab/group/pages nav shape (proven precedent to copy).
- Source service for content sourcing only: GitLab monorepo `mayarid/source`, V2 code under `api-custom-paymenlink/api/v2/`, master route table `api/v2/routes.js`; public base `https://api.mayar.id/hl/v2`.
- `DUMMY_PROD_MERCHANT_API_KEY` env (prod merchant JWT, verified working on prod reads) for capturing real GET response shapes.
- Tooling present: `glab`, `curl`, `jq`, `python3` for sourcing and JSON validation; no build/test/lint framework in-repo.
