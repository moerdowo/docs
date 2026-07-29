# Bug Reports — v2-coupon-list-doc

> NOTE: `jonggrang bug --feature v2-coupon-list-doc-ms4496qj "..."` refused to run
> ("Multiple features found. Use --feature <featureId>.") even with the flag supplied,
> both before and after the description arg. Entries below were written by hand in the
> CLI's format. See task-001 notes in progress.txt.

## [open] bug-001 · 2026-07-28 · found during task-001 (grounding pass)
docs.json navigation does not reference `api-reference-v2/nameservice/create.mdx` or
`api-reference-v2/nameservice/update.mdx`. Both files exist on disk under
`api-reference-v2/**` but appear in no nav group, so they are unreachable/unpublished on
the docs site. Structural check C2 (`validate-v2-docs.py`) fails with
`orphan .mdx not referenced in nav` for both. Pre-existing on `main` — `git diff main --
api-reference-v2/ docs.json` is empty on this branch, so it is not caused by this feature.
Out of scope for v2-coupon-list-doc (which only adds `api-reference-v2/discount/index`).

## [open] bug-002 · 2026-07-28 · found during task-001 (grounding pass)
The domain-compliance suite (`domain-compliance-v2-docs.py`) hard-codes the assumption that
every V2 endpoint page uses the `/hl/v2` base path and the `{statusCode, messages, ...}`
envelope. The SaaS/software license pages added in 245b82f legitimately use a different
surface (e.g. `https://api.mayar.id/saas/v2/license/verify`) and a different envelope
(`statusCode` + `isLicenseActive`, no `message`/`messages`). Result: 14 FAILs against
`api-reference-v2/saas/{activate,deactivate,verify}.mdx` and
`api-reference-v2/software/verify.mdx` — D1 (missing prod/sandbox `/hl/v2` base URL),
D4 (no curl hitting `/hl/v2`), D5 (envelope missing `message`/`messages`). Either the suite
needs an exemption list for non-`/hl/v2` surfaces, or those pages need sandbox base URLs
added. Pre-existing on `main`; out of scope for this feature.

CONSEQUENCE for this feature's validation task: the combined gate
`bash .jonggrang/.output/features/api-v2-reference-docs-mqyl9hub/validate-v2-docs.sh`
currently exits 1 on a clean tree (2 structural + 14 domain = 16 FAILs). It cannot be used
as an absolute pass/fail. Task-004 must compare against this recorded baseline: the gate is
GREEN-for-this-feature iff the FAIL set is exactly these 16 pre-existing lines and no new
FAIL mentions `api-reference-v2/discount/` or `docs.json`.
