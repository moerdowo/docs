# Bug Reports — fix-v2-credit-endpoint-base-path

> NOTE: `jonggrang bug "..." --feature fix-v2-credit-endpoint-base-path-mt18vmcz` refused to
> run ("Multiple features found. Use --feature <featureId>.") with the flag in either
> position. Root cause confirmed by reading the CLI: the global option parser at
> /usr/lib/node_modules/jonggrang/bin/jonggrang.js:5191 consumes `--feature` into
> WORK_FEATURE_ID and never forwards it, so `cmdBug`'s own `subArgs.indexOf('--feature')`
> (line ~2400) always misses and `forcedFeatureId` stays null. With >1 feature on disk and a
> non-TTY stdin, `jonggrang bug` is therefore unusable. Entries below were written by hand in
> the CLI's format. The v2-coupon-list-doc feature hit and recorded the same defect.

## [open] bug-001 · 2026-08-20 · found during task-004 (consistency sweep)
V1 doc defect, out of scope for this feature. In
`api-reference/creditbasedproduct/customerbalance.mdx` the Sandbox entry of the Endpoint
`<CodeGroup>` (line 41) is missing the `=` after `customerId`:

    https://api.mayar.io/credit/v1/credit/customer/balance?customerId{customerID}

The Production entry directly above it (line 37) is correct
(`...?customerId={customerID}`). A reader copying the Sandbox URL gets a malformed query
string with no `customerId` parameter. Surfaced while comparing V2 route suffixes against
their V1 counterparts for check 4; V1 pages are explicitly out of scope for
fix-v2-credit-endpoint-base-path, so it was recorded rather than corrected.

## [open] bug-002 · 2026-08-20 · found during task-004 (consistency sweep)
V1 doc defect, out of scope for this feature. In
`api-reference/creditbasedproduct/paginatecustomercredithistory.mdx` both Endpoint
`<CodeGroup>` entries omit the path-parameter placeholder, leaving an empty path segment:

    https://api.mayar.id/credit/v1/credit/customer/paginate-credit-history/?productId={productId}
    https://api.mayar.io/credit/v1/credit/customer/paginate-credit-history/?productId={productId}

The page's own curl example supplies a concrete id in that position
(`/paginate-credit-history/PQVS4KGY?...`), and the sibling page
`api-reference/usagebasedmembership/paginatecustomercredithistory.mdx` documents the same
route as `/paginate-credit-history/{memberId}?...`. So the creditbasedproduct Endpoint block
is internally inconsistent with its own example and with its sibling. Same origin and same
out-of-scope rationale as bug-001.
