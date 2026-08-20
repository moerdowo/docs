---
feature_id: fix-v2-credit-endpoint-base-path-mt18vmcz
feature_name: fix-v2-credit-endpoint-base-path-mt18vmcz
tags: [docs, api-v2, credit, base-path, mdx]
updated_at: 2026-08-20T08:32:48.140Z
---

## Context

The V2 credit API reference pages documented their endpoints on the shared V2 host base `https://api.mayar.i{d,o}/hl/v2/credit/...`, but the credit service is served from its own per-service prefix — the same `credit/vN/credit/` shape the V1 credit pages already document. Every documented call on those pages would fail before reaching a route.

This feature ([fix-v2-credit-endpoint-base-path-mt18vmcz](.jonggrang/.output/features/fix-v2-credit-endpoint-base-path-mt18vmcz/)) rewrote `hl/v2/credit` → `credit/v2/credit` across all 7 V2 credit pages, then verified the rewrite structurally. Five tasks, four plan phases, all complete. Docs-only change: no code, no schema, no config.

Repo: Mayar Docs (Mintlify-style MDX + `docs.json`). Full raw notes in the [progress](.jonggrang/.output/features/fix-v2-credit-endpoint-base-path-mt18vmcz/progress.txt) log.

## Facts

**Occurrence inventory (grounded in [task-001](.jonggrang/.output/features/fix-v2-credit-endpoint-base-path-mt18vmcz/jonggrang-tasks.json), matched the planned baseline with zero drift):** 21 occurrences of `hl/v2/credit` across exactly 7 files, all under `api-reference-v2/credit/`. 3 per page — the curl line inside `<RequestExample>`, the Production URL (`api.mayar.id`) and the Sandbox URL (`api.mayar.io`) inside the Endpoint `<CodeGroup>`.

| File | curl | Production | Sandbox |
|---|---|---|---|
| `api-reference-v2/credit/add-credit.mdx` | 10 | 41 | 45 |
| `api-reference-v2/credit/balance.mdx` | 10 | 63 | 67 |
| `api-reference-v2/credit/generate-immutable-checkout.mdx` | 10 | 45 | 49 |
| `api-reference-v2/credit/paginate-credit-history.mdx` | 10 | 64 | 68 |
| `api-reference-v2/credit/regist-credit-usage.mdx` | 10 | 49 | 53 |
| `api-reference-v2/credit/regist-membership.mdx` | 10 | 61 | 65 |
| `api-reference-v2/credit/spend.mdx` | 10 | 41 | 45 |

**Prefix form.** `grep -rn "credit/v1/credit"` under `api-reference/creditbasedproduct/` and `api-reference/usagebasedmembership/` returns 33 lines across 10 files, all shaped `https://api.mayar.i{d,o}/credit/v1/credit/<suffix>`. Service segment `credit`, version segment `vN`, then a second literal `credit` segment before the route. V2 target: `https://api.mayar.id/credit/v2/credit/<suffix>`. `credit/v2/credit` appeared nowhere in the repo before this feature — clean target string, no collision risk.

**Route suffixes preserved byte-for-byte:**
- `add-credit.mdx` → `/customer/add-credit`
- `balance.mdx` → `/customer/balance` (curl uses concrete UUIDs `a1b2c3d4-e5f6-4789-a012-3456789abcde` / `7c9d2e1f-4a5b-4c6d-8e9f-0a1b2c3d4e5f`; CodeGroup uses `(customerId)`/`(productId)` placeholders — each form kept as-is)
- `generate-immutable-checkout.mdx` → `/generate/immutable/checkout`
- `paginate-credit-history.mdx` → `/customer/paginate-credit-history/(customerId)?productId=(productId)&page=1&limit=10` (same concrete-vs-placeholder split as balance)
- `regist-credit-usage.mdx` → `/credit-usage/customer/regist`
- `regist-membership.mdx` → `/membership/customer/regist`
- `spend.mdx` → `/customer/spend`

**Scope boundaries.**
- `hl/v2` legitimately appears in ~80 other `api-reference-v2` pages (customer, invoice, product, webhook, …) — all correctly on the shared base, all out of scope. **Never widen the substitution to bare `hl/v2`.**
- `api-reference-v2/introduction.mdx:53/58` intentionally still declares `https://api.mayar.i{d,o}/hl/v2` as the general V2 base. Justified by precedent: `api-reference-v2/saas/{activate,deactivate,verify}.mdx` state `/saas/v2/license/...` and `api-reference-v2/software/verify.mdx` states `/software/v2/license/verify`, both declaring a per-service base inline with no explanatory note and no change to the general base.
- The only non-docs matches for `hl/v2/credit` are Jonggrang workflow metadata describing this very defect (`plan.md`, `jonggrang-tasks.json`, `progress.txt`, ephemeral fragments) — metadata, not docs, never rewritten.

**Repo validation reality.** No automated test suite, no typecheck, no lint, no build step. `testing.framework` = `"none"`; both `testing.command` and `hooks.pre_commit` are a bare `echo 'no test command configured'`. No `package.json`, no `mint.json` at the repo root; `mintlify` not on PATH. Exit 0 from the hook means "the echo ran", not "tests passed".

**docs.json nav.** The `Credit (Membership / Usage)` group lists exactly 7 slugs in this order: `balance`, `spend`, `add-credit`, `paginate-credit-history`, `regist-membership`, `regist-credit-usage`, `generate-immutable-checkout` (each prefixed `api-reference-v2/credit/`). Set equality holds in both directions against the files on disk — no orphan page, no dead nav entry.

**Structural shape of the 7 pages.** Frontmatter `---` at line 1, closing `---` at line 5, three keys between (title / openapi / description). Code fences: 8 per file, except `balance.mdx` at 10 — it legitimately carries two `<ResponseExample>` blocks. `RequestExample` 1/1 on all 7; `ResponseExample` 1/1 on six, 2/2 on balance; `CodeGroup` 1/1 on all 7.

**Commits.** Pre-feature base `19546e9`. `966d248` (task-002, 4 files, +12/-12) and `4522e4e` (task-003, 3 files, +9/-9). Tasks 001, 004 and 005 were read-only and produced no docs commit.

## What Done & Why

**[task-001](.jonggrang/.output/features/fix-v2-credit-endpoint-base-path-mt18vmcz/jonggrang-tasks.json) — Grounding inventory (read-only).** Enumerated all 21 occurrences repo-wide with line numbers, proved none exists outside the 7 credit pages and that the string only ever appears in URL position, confirmed the `credit/vN/credit/` shape from the 33 V1 occurrences, recorded each page's exact route suffix, and confirmed the saas/v2 + software/v2 inline-base precedent. **Why:** tasks 002/003 apply a blind `sed` substitution, which is only safe if the string is syntactically isolated and the replacement collides with nothing. Both verified. No files changed.

**[task-002](.jonggrang/.output/features/fix-v2-credit-endpoint-base-path-mt18vmcz/jonggrang-tasks.json) — Four customer-scoped pages.** Per-file `sed -i 's|hl/v2/credit|credit/v2/credit|g'` on `balance.mdx`, `spend.mdx`, `add-credit.mdx`, `paginate-credit-history.mdx`. 12 URL lines (4 curl + 4 Production + 4 Sandbox), +12/-12, commit `966d248`. Pre-edit grep matched task-001's inventory line-for-line — zero drift, so the blind sed was safe. Post-edit: zero `hl/v2/credit`, exactly 12 `credit/v2/credit` at the expected line numbers; full `git diff` read line-by-line (every changed line a URL line; frontmatter incl. `openapi:` identifiers, descriptions, headers, bodies, error sections untouched); `docs.json` still parses; fence counts even (10/8/8/8). **Tradeoff:** chose a silent minimal correction — no callout explaining the deviation — matching how the sibling saas/v2 and software/v2 pages present their own per-service bases.

**[task-003](.jonggrang/.output/features/fix-v2-credit-endpoint-base-path-mt18vmcz/jonggrang-tasks.json) — Registration and checkout pages.** Identical substitution on `regist-membership.mdx`, `regist-credit-usage.mdx`, `generate-immutable-checkout.mdx`. 9 URL lines, +9/-9, commit `4522e4e`. Same verification: pre-edit grep matched inventory (10/61/65, 10/49/53, 10/45/49), post-edit grep clean, full diff read, `--data-raw` payloads and parameter tables untouched, fences even (8 per file), `docs.json` parses. Completed Phase 2 — all 21 occurrences corrected.

**[task-004](.jonggrang/.output/features/fix-v2-credit-endpoint-base-path-mt18vmcz/jonggrang-tasks.json) — Consistency sweep (read-only). All five checks PASS.**
1. *Residual:* zero `hl/v2/credit` in docs content, confirmed both by scoped `grep` (excluding `.git`, `.jonggrang`, `node_modules`, `.claude`, `.codex`, `.opencode`) and by index-scoped `git grep` — both exit 1. The unscoped repo-wide grep still returns ~28 lines, all Jonggrang metadata.
2. *Total:* exactly 21 `credit/v2/credit` lines, 3 per page across all 7 — no page over- or under-counted.
3. *Host coverage:* every page has exactly 2 `api.mayar.id` lines (curl + Production) and 1 `api.mayar.io` (Sandbox), zero credit/v2 URLs on any other host; one `<CodeGroup>` pair holding Production then Sandbox fences, one `<RequestExample>` pair holding the curl. curl-vs-Production matched programmatically after normalising UUIDs and placeholders to a single token (5 pages byte-identical; balance and paginate-credit-history differ only in the concrete-vs-placeholder forms they already used). Production-vs-Sandbox matched with the TLD masked.
4. *Suffix parity:* proven byte-level, not sampled — `diff <(git show 19546e9:$f | sed 's|hl/v2/credit|credit/v2/credit|g') $f` IDENTICAL on all 7, so the current file differs from the pre-feature file by that substitution alone and no suffix, parameter, payload or prose byte could have moved. Separately, all 7 V2 route paths were located in V1 (`add-credit`→`addcustomercredit.mdx`, `balance`→`customerbalance.mdx`, `spend`→`spendcustomercredit.mdx`, `generate-immutable-checkout`→`creditbasedproduct/generateimmutablecheckoutlink.mdx`, `regist-credit-usage`→`creditbasedproduct/registernewcustomer.mdx`, `regist-membership`→`usagebasedmembership/registnewmembershipcustomer.mdx`). Only `paginate-credit-history` failed a naive full-string grep: V2 uses `(customerId)` where V1 uses `{memberId}` or an empty segment — the route `/customer/paginate-credit-history/<id>` is identical in all three, and the token-name difference is pre-existing. No suffix was "fixed" to match V1.
5. *Scope:* `git diff 19546e9..HEAD --stat` → exactly the 7 credit pages, +21/-21, 3 lines per file. `git diff --name-only` → only `.jonggrang/` state files dirty, so all docs work is committed. Sentinels verified individually with `git diff --quiet 19546e9..HEAD -- <path>`: `api-reference-v2/introduction.mdx`, `docs.json` and `api-reference/openapi.json` all UNTOUCHED. Both JSON files parse via `node JSON.parse`.

**[task-005](.jonggrang/.output/features/fix-v2-credit-endpoint-base-path-mt18vmcz/jonggrang-tasks.json) — MDX / docs.json / nav validation (read-only). Checks 1-4 PASS, check 5 skipped.**
1. *MDX structure:* frontmatter well-formed on all 7 and proven UNCHANGED — `diff <(git show 19546e9:$f | sed -n '1,5p') <(sed -n '1,5p' $f)` IDENTICAL on all 7, so no title, description or `openapi:` identifier moved a byte. Fences even per file; JSX tags all balanced.
2. *Config parse:* `python3 -m json.tool docs.json` and `node -e 'JSON.parse(...)'` both exit 0; `docs.json` confirmed unchanged in history (`19546e9..HEAD`) and in the worktree.
3. *Nav:* the 7 `Credit (Membership / Usage)` slugs each resolve to an existing `.mdx`; set equality both directions.
4. *Hook:* ran `hooks.pre_commit` / `testing.command` — a bare `echo 'no test command configured'`, exit 0. Reported plainly as a no-op, not as passing tests.
5. *Visual render:* SKIPPED, not worked around — no `package.json`, no `mint.json`, `mintlify` not on PATH, and the task explicitly forbade installing tooling. Substituted a source-level confirmation: read `balance.mdx`'s Endpoint `<CodeGroup>` (emits the Production and Sandbox `credit/v2/credit/customer/balance?...` lines) and re-listed all 21 URL lines. Adequate here because the Endpoint block is a literal fenced string — rendered output equals file content — but would NOT be adequate for a change touching components or templated content.

**Out-of-scope defects found and REPORTED, not corrected** (recorded in this feature's `bugs.md` during task-004, both still open, both pre-existing V1 defects):
- **bug-001:** `api-reference/creditbasedproduct/customerbalance.mdx:41` Sandbox URL is missing the `=` after `customerId` (`?customerId{customerID}`); the Production entry at `:37` is correct.
- **bug-002:** `api-reference/creditbasedproduct/paginatecustomercredithistory.mdx` Endpoint block omits the path-parameter placeholder entirely (`/paginate-credit-history/?productId=...`), contradicting its own curl example and its `usagebasedmembership` sibling.

## Lessons Learned

- **A read-only grounding inventory with exact line numbers pays for itself.** Pre-edit greps in both task-002 and task-003 matched task-001's inventory with zero drift, which made a blind per-file `sed` safe and turned verification into a diff read rather than a re-investigation.
- **A mechanical prefix rewrite is only safe blind under two proven conditions:** the string appears exclusively in one syntactic position, and the replacement string collides with nothing in the repo. Both held here, so `sed -i` beat hand-editing 21 sites — and it is idempotent and re-runnable.
- **The strongest available check for a mechanical docs rewrite** is `diff <(git show <pre-feature-base>:$f | sed '<the same substitution>') $f`. Identical output proves the file differs from the original by that substitution alone — no sampling, no per-section review. Used for the suffix check (task-004) and the frontmatter check (task-005). Verifying "value unchanged by this feature" this way beats spot-checking the current file.
- **A "grep repo-wide for X must return zero" acceptance criterion is unsatisfiable when X is the defect string**, because Jonggrang's own `plan.md`, tasks JSON, `progress.txt` and memory fragments all quote it. Task-004's criterion as written would have false-failed. Use `git grep` (index-scoped, needs no exclude list) as the authoritative residual check, or scope with `--exclude-dir=.git --exclude-dir=.jonggrang --exclude-dir=node_modules`.
- **Docs-repo validation gate** (what substitutes for a test suite): exact expected match count at expected line numbers, full `git diff` read line-by-line, `JSON.parse`/`json.tool` on `docs.json`, per-file code-fence parity, JSX tag pairing, nav slug-to-file resolution, and a diff against the pre-feature base commit.
- **Even-but-different fence counts are correct.** `balance.mdx` has 10 fence lines and two `<ResponseExample>` blocks while the other 6 credit pages have 8 and one. Do not "normalise" it.
- **Selecting the right nav group:** three groups in `docs.json` match `/credit/` — `Membership (Credit)` (5 V1 pages), `Credit Based Product` (6 V1 pages) and the V2 `Credit (Membership / Usage)` (7 pages). Select the V2 group by its `api-reference-v2/credit/` page prefix, never by group title.
- **Harness gotcha:** `cd` inside a Bash tool call persists into subsequent calls. A follow-up command assuming the repo root failed with "No such file or directory". Use absolute paths or re-`cd`.
- **`jonggrang bug --feature` is broken here** — see Promotion Candidates for the root cause and workaround.

## Open Questions / What Next

**The one open item for the human reviewer, unchanged since task-001 and carried through every task:** the `credit/v2/credit` target prefix has **never been checked against backend routing code**. It rests on the feature request plus the V1 `credit/v1/credit/` precedent only. Project memory records the backend checkout at `/root/.jonggrang/workspace/Mayar Source`; that path does not exist in this worktree. **Confirm the prefix against the server before merging.** This was accepted per the plan's Key Decisions rather than blocking the fix.

Otherwise the feature is complete: all 5 tasks done, all 4 plan phases done, the fix verified complete, internally consistent and correctly scoped. Nothing outstanding for a follow-up task.

Still open but out of scope: bug-001 and bug-002 (pre-existing V1 doc defects, recorded in this feature's `bugs.md`, untouched).

## Promotion Candidates

- **AGENTS.md — state plainly that this repo has no automated validation.** `testing.framework` = `"none"`; `testing.command` and `hooks.pre_commit` are both `echo 'no test command configured'`; no typecheck, lint, build, `package.json` or `mint.json`. Exit 0 means "the echo ran", NOT "tests passed" — agents must say so explicitly instead of reporting a green validation. Document the substitute gate for MDX edits: `docs.json` JSON parse, per-file code-fence parity, JSX tag pairing, nav slug-to-file resolution, full `git diff` read, and a base-commit diff under the intended transform.
- **Jonggrang workflow — residual-check scoping.** Any search-and-replace verification step must scope to tracked source (`git grep`), not the workflow metadata that names the string being replaced. Plans should stop writing "grep repo-wide must return zero" for a defect string.
- **`jonggrang bug` is BROKEN and needs an upstream fix.** `jonggrang bug "..." --feature <id>` always dies with "Multiple features found. Use --feature <featureId>." whenever more than one feature exists on disk and stdin is not a TTY. Root cause confirmed by reading the CLI source: the global option parser at `/usr/lib/node_modules/jonggrang/bin/jonggrang.js:5191` matches `--feature` first and consumes it into `WORK_FEATURE_ID`, so it is stripped before `cmdBug` runs; `cmdBug`'s own `subArgs.indexOf('--feature')` (~line 2400) then finds nothing and `forcedFeatureId` stays null. `--feature=<id>` does not work either (the switch matches the bare token only), and `jonggrang bug --help` fails identically. Workaround: hand-append to `.jonggrang/.output/features/<feature>/bugs.md` in the CLI's format, `## [open] bug-00N · <date> · found during <task>`. This is the **second** feature to hit it — the `v2-coupon-list-doc` feature used the same workaround.
- **Harness gotcha worth documenting:** `cd` inside a Bash tool call persists into the next call; use absolute paths in follow-up commands.
- **Byte-level transform proof as a standard technique:** `diff <(git show <base>:$f | sed '<substitution>') $f` for verifying that a mechanical rewrite changed nothing else.
