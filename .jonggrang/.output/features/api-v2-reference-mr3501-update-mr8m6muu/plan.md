---
feature: api-v2-reference-mr3501-update
branch: feat/api-v2-reference-mr3501-update
base: "main"
work_type: LARGE
description: Update API V2 Reference docs for MR !3501 — bump 4 external groups to /v2, author mirrored-v1 pages, consolidate QR nav into Transaction, remove Name Services
created_at: 2026-07-06T02:39:51.103Z
---

# Plan: Update API V2 Reference for MR !3501 v2 Routing

## Approach
Base all work on `origin/feat/api-v2-reference-mr3501-sync` (the confirmed base: 87 v2 .mdx pages including the 4 external-service groups, plus the QR / Payment Channels and Name Services nav groups). Ground the coverage matrix and description reconciliation on the MR !3501 monorepo source read via `git show <branch>:<path>` — first establishing the correct local source-checkout path (fetch/clone if absent). Bump the 4 external-service groups to their new `/v2` base URLs, author `/hl/v2` pages only for mirrored-v1 endpoints that RESTful apiV2 does not already cover, then reorganize the API V2 Reference nav in `docs.json` (move QR / Payment Channels pages into Transaction, delete the empty group, remove Name Services entirely). Every authored/edited page preserves the envelope-key quirk (`message`/`messages`), uses synthetic samples, and must pass the C1–C8 structural gate, C7 leak-guard, and D1–D7 domain-compliance gate.

## Phases
1. Base setup & source grounding — checkout/confirm `feat/api-v2-reference-mr3501-sync` as the working base; locate or fetch the MR !3501 monorepo source checkout and verify `git show` access to `routes.js`/`index.js` for the affected services.
2. Coverage matrix — from `api/v1/routes.js`, `api/v2/routes.js`, and `index.js`, build the definitive per-endpoint matrix (RESTful-apiV2-covered vs mirrored-v1-only vs already-has-page); output the exact lists of pages to author, edit, and delete.
3. External-service base-URL bump — update the 4 groups (Credit Based Product, Membership (Credit), Software License Code, Membership (SaaS)) to `/credit/v2`, `/saas/v2`, `/software/v2` base URLs; response shapes unchanged (same controllers).
4. Author mirrored-v1 `/hl/v2` pages — create `.mdx` pages only for mirrored-v1 endpoints apiV2 does not cover, using the standard template, correct envelope key, and synthetic samples.
5. Navigation wiring — add new pages to the API V2 Reference tab; move all QR / Payment Channels pages into Transaction and drop the empty group; remove the Name Services group and delete its two `.mdx` pages; validate `docs.json` after every edit.
6. Description/accuracy pass — reconcile all V2 Reference descriptions and field docs against MR !3501 source (base URLs, params, responses), correcting stale text.
7. Validation & leak-guard — run the C1–C8 / C7 / D1–D7 gate to exit 0; grep for dangling references to removed Name Service pages; scrub internal identifiers/PII; fix and re-run until green.

## Key Decisions
- Decision: Base branch = `origin/feat/api-v2-reference-mr3501-sync` (per user clarification; the originally-planned `feat/v1-coverage-into-api-v2-reference` worktree does not exist). Never work on `main` — it has no V2 content.
- Decision: For api-custom-paymenlink, present the canonical RESTful apiV2 form where it exists and only author pages for mirrored-v1 routes apiV2 does not define — avoids duplicate/conflicting pages.
- Decision: External-service `/v2` groups are same-controller mirrors → treat as a base-URL version bump (v1→v2) + v2 nav, not new field documentation.
- Decision: QR / Payment Channels move is nav-only — page bodies (base URLs, params, responses, envelope keys) are unchanged; the emptied group is removed after the move.
- Decision: Name Services endpoints (POST Create / POST Update Name Service) are deleted entirely — `.mdx` pages and `docs.json` entries removed together; not migrated elsewhere.
- Decision: Preserve the envelope-key quirk exactly per endpoint; all sample values synthetic (no real PII). `docs.json` edits are small, localized, and each followed by `python3 -m json.tool docs.json`.

## Out of Scope
- Any changes under `api-reference/**` (V1 Reference).
- Backend service code, `openapi.json` stub, or `openapi:` frontmatter semantics.
- New field/response documentation for the 4 external-service groups beyond the base-URL bump.
- Changing the content of moved QR / Payment Channels pages, or re-authoring/relocating the removed Name Services endpoints.
- Building/deploying the Mintlify site or adding application/unit tests; reworking `docs.json` global structure or the Guides / API V1 Reference tabs.

## Dependencies
- Base worktree/branch `feat/api-v2-reference-mr3501-sync` (87 v2 pages incl. the 4 external-service groups + QR / Payment Channels + Name Services nav groups).
- MR !3501 monorepo source checkout (path to be confirmed/fetched in Phase 1) — read via `git show`, no network; source of the coverage matrix and accuracy reconciliation.
- Current `docs.json` API V2 Reference nav layout (QR / Payment Channels, Transaction, Name Services group definitions and member page paths).
- Established page template, per-service base URLs, envelope-key quirk, synthetic-sample/PII-scrub convention.
- Validation gate: `.jonggrang/.output/features/api-v2-reference-docs-mqyl9hub/validate-v2-docs.sh` (C1–C8 incl. C7 leak-grep, plus D1–D7 domain compliance).
- Tooling on box: git, python3, curl, jq.

<!-- jonggrang:clarifications -->
## Clarifications
_Captured from the planning Q&A:_

Goal: Update the API V2 Reference docs to reflect MR !3501's v2 mirrors: bump the 4 external-service groups to their /v2 base URLs, author /hl/v2 pages for mirrored-v1 endpoints apiV2 doesn't already cover, consolidate the QR / Payment Channels nav group into Transaction, and remove the Name Services endpoints entirely — all passing the C1–C8 / C7 / D1–D7 docs gate.

- **The plan's stated base branch `feat/v1-coverage-into-api-v2-reference` (worktree `…-mr4yheje`, '90 pages + 4 external groups') does not exist locally or on origin. Which branch should be the actual base?** → Use origin/feat/api-v2-reference-mr3501-sync (has all 4 external groups + QR/Payment Channels + Name Services groups, 87 v2 .mdx pages)
- **The authoritative read-only source monorepo `/root/.jonggrang/workspace/Mayar Source` (@ MR !3501) is missing, and the root `.jonggrang/progress.txt` is deleted. How should I ground the coverage matrix (Phase 1) and the description/accuracy reconciliation (Phase 5)?** → Point me to the correct source-checkout path (or I should clone/fetch it) so I can read routes.js/index.js via git show
