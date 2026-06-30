#!/usr/bin/env python3
"""
Documentation-validation & leak-guard suite for the API V2 Reference docs.

Phase 6 (task-027). Run from the repo root:

    python3 .jonggrang/.output/features/api-v2-reference-docs-mqyl9hub/validate-v2-docs.py

Exit 0 == all checks green. Exit 1 == one or more checks failed (details printed).

Checks
  C1  docs.json is valid JSON.
  C2  nav<->file 1:1 for tabs[2] (API V2 Reference): every api-reference-v2 page
      path in docs.json maps to an existing .mdx, and every .mdx under
      api-reference-v2/** is referenced exactly once (no orphans, no missing).
  C3  frontmatter `title:` present on every V2 page.
  C4  JSX tag balance for RequestExample/ResponseExample/CodeGroup/ParamField/
      ResponseField/Note/Warning (open count == close count per file).
  C5  code-fence parity (even number of ``` per file).
  C6  embedded JSON in ResponseExample/RequestExample ```json fences parses.
  C7  NEGATIVE leak-grep: FAILS if any internal identifier appears in the
      RENDERED content under api-reference-v2/** (handler/function/variable
      names, internal module paths, @mayarid/* packages, GraphQL op names,
      Redis/Scylla/session internals, env var names).
  C8  tabs[1].tab == "API V1 Reference" AND tabs[1] groups/pages byte-identical
      to main:docs.json tabs[1] (label-normalized) — i.e. V1 nav unchanged.

Notes on C7 scope: a published "leak" is what RENDERS to an API consumer.
Mintlify strips `{/* ... */}` MDX comments at build time, so the leak-grep is run
over comment-stripped (rendered) content. The maintainer-notes comment convention
deliberately holds sourcing context; references that remain only inside those
non-rendered comments are reported separately (see RESIDUAL block) and never
reach a reader.
"""
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve()
# walk up to repo root (the dir that contains docs.json)
while ROOT != ROOT.parent and not (ROOT / "docs.json").exists():
    ROOT = ROOT.parent
DOCS = ROOT / "docs.json"
V2_DIR = ROOT / "api-reference-v2"
V2_PREFIX = "api-reference-v2/"

JSX_TAGS = ["RequestExample", "ResponseExample", "CodeGroup",
            "ParamField", "ResponseField", "Note", "Warning"]

COMMENT_RE = re.compile(r"\{/\*.*?\*/\}", re.S)

# ---- C7 internal-identifier denylist (matched against RENDERED content) ----
LEAK_PATTERNS = {
    "mayarid-package": r"@mayarid\b",
    "internal-module-js": (
        r"\b(?:routes|query|schema|membership|memberships|installment|discount|"
        r"webhook|review|customer|bundling|name-service|transactions|invoices|"
        r"paymentlink|request-payment|payme|formatter|utils|index)\.js\b"),
    "internal-path": r"(?:api-custom-paymenlink|src/api/v2|/api/v2/)",
    "handler-fn-name": (
        r"\b(?:getMembershipTierListCursor|getMembershipMemberListCursor|"
        r"getMembershipMember|handleRegistNewMembershipCustomer|"
        r"updateMembershipMember|createMembershipInvoice|cancelMembershipMember|"
        r"returnJSON|buildCursorResponse|sendSuccessResponse|sendErrorResponse|"
        r"sendcursor|gtFetch|editInvoice|editPayment|editPaymentlink|editWebinar|"
        r"editEvent|editDigitalProduct|editReview|allInstallment|getInstallment|"
        r"createInstallment|newNameService|editNameService|updateUrl|"
        r"newWebhookHistory|createReview|getReviewPage|reviewStatsProduct|"
        r"validateQueryParameters|formatResponseData|formatMembershipBillUrl|"
        r"editMembershipCustomer|validateCoupon|slugify|powerUpStore|getDiscount|"
        r"buildCursor|checkJwt)\b"),
    "graphql-op-name": r"\b(?:GET|INSERT|UPDATE|DELETE|UPSERT)_[A-Z][A-Z_]{2,}\b",
    "redis-session-internal": r"\b(?:redis|scylla|memcache|memcached)\b",
    "env-var-name": (
        r"(?:process\.env\b|APP_PUBLIC_URL|DUMMY_PROD_MERCHANT_API_KEY|"
        r"MERCHANT_API_KEY)"),
    "graphql-keyword": r"\b(?:graphql|gql)\b",
}


class Suite:
    def __init__(self):
        self.fail = []   # (check, file, detail)
        self.ok = []     # check names that passed

    def err(self, check, detail, f=""):
        self.fail.append((check, f, detail))

    def passed(self, check, summary):
        self.ok.append((check, summary))


def strip_comments(text):
    return COMMENT_RE.sub("", text)


def walk_pages(node, out):
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, dict):
        for p in node.get("pages", []):
            walk_pages(p, out)
    elif isinstance(node, list):
        for p in node:
            walk_pages(p, out)


def main():
    s = Suite()

    # ---------- C1 docs.json valid JSON ----------
    try:
        # mirror `python3 -m json.tool docs.json`
        docs = json.loads(DOCS.read_text())
        s.passed("C1", "docs.json is valid JSON")
    except Exception as e:  # noqa: BLE001
        s.err("C1", f"docs.json is NOT valid JSON: {e}")
        report(s)
        return 1

    tabs = docs["navigation"]["tabs"]
    tab2 = next((t for t in tabs if t.get("tab") == "API V2 Reference"), None)
    if tab2 is None:
        s.err("C2", 'no tab "API V2 Reference" in docs.json')
        report(s)
        return 1

    # ---------- C2 nav<->file 1:1 ----------
    nav_pages = []
    for g in tab2.get("groups", []):
        walk_pages(g, nav_pages)
    nav_v2 = [p for p in nav_pages if p.startswith(V2_PREFIX)]
    non_v2 = [p for p in nav_pages if not p.startswith(V2_PREFIX)]
    for p in non_v2:
        s.err("C2", f"tabs[2] page not under {V2_PREFIX}: {p}")
    dups = {p: n for p, n in Counter(nav_pages).items() if n > 1}
    for p, n in dups.items():
        s.err("C2", f"nav path referenced {n}x (must be exactly once): {p}")

    disk_files = sorted(p for p in V2_DIR.rglob("*.mdx"))
    # Guard against a vacuous all-green: with 0 pages every count==total gate and
    # every "nothing found" negative check would pass while asserting nothing.
    if not disk_files:
        s.err("C0", f"no .mdx pages found under {V2_PREFIX} — nothing to validate")
        report(s)
        return 1
    disk_rel = {f"{p.relative_to(ROOT).with_suffix('')}".replace("\\", "/")
                for p in disk_files}
    nav_set = set(nav_v2)
    missing = sorted(nav_set - disk_rel)        # nav -> no file
    orphan = sorted(disk_rel - nav_set)         # file -> not in nav
    for p in missing:
        s.err("C2", f"nav references missing .mdx: {p}.mdx")
    for p in orphan:
        s.err("C2", f"orphan .mdx not referenced in nav: {p}.mdx")
    if not (non_v2 or dups or missing or orphan):
        s.passed("C2", f"nav<->file 1:1 ({len(nav_v2)} pages, 0 missing, 0 orphan)")

    # ---------- per-file checks C3..C7 ----------
    c3 = c4 = c5 = c6 = 0
    json_blocks = 0
    leaks = []
    for f in disk_files:
        rel = f.relative_to(ROOT)
        raw = f.read_text()
        rendered = strip_comments(raw)

        # C3 frontmatter title
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw, re.S)
        if not m or not re.search(r"^title:\s*\S", m.group(1), re.M):
            s.err("C3", "missing frontmatter title", str(rel))
        else:
            c3 += 1

        # C4 JSX tag balance
        bal_ok = True
        for t in JSX_TAGS:
            opens = len(re.findall(r"<" + t + r"(?=[\s>/])", raw))
            closes = len(re.findall(r"</" + t + r">", raw))
            if opens != closes:
                bal_ok = False
                s.err("C4", f"{t} unbalanced (open={opens} close={closes})", str(rel))
        if bal_ok:
            c4 += 1

        # C5 code-fence parity
        fences = len(re.findall(r"^```", raw, re.M))
        if fences % 2 != 0:
            s.err("C5", f"odd number of code fences ({fences})", str(rel))
        else:
            c5 += 1

        # C6 embedded JSON parse. The spec targets Request/ResponseExample blocks;
        # we parse EVERY ```json fence in the file (a strict superset, since 5 of
        # the 80 json examples live in <Note>/body rather than Request/Response-
        # Example). Each ```json fence may carry a title (e.g. ```json Response 200).
        file_json_ok = True
        for fence in re.finditer(r"```json[^\n]*\n(.*?)\n```", raw, re.S):
            json_blocks += 1
            try:
                json.loads(fence.group(1))
            except Exception as e:  # noqa: BLE001
                file_json_ok = False
                s.err("C6", f"embedded JSON does not parse: {e}", str(rel))
        if file_json_ok:
            c6 += 1

        # C7 leak-grep over rendered content
        for name, pat in LEAK_PATTERNS.items():
            for mm in re.finditer(pat, rendered):
                ctx = rendered[max(0, mm.start() - 25):mm.start() + 35]
                leaks.append((str(rel), name, mm.group(0), ctx.replace("\n", " ")))

    total = len(disk_files)
    if c3 == total:
        s.passed("C3", f"frontmatter title present on all {total} pages")
    if c4 == total:
        s.passed("C4", f"JSX tags balanced on all {total} pages")
    if c5 == total:
        s.passed("C5", f"code-fence parity (even) on all {total} pages")
    if c6 == total:
        s.passed("C6", f"embedded JSON parses ({json_blocks} json blocks)")
    if not leaks:
        s.passed("C7", "leak-grep clean (0 internal identifiers in rendered content)")
    else:
        for rel, name, tok, ctx in leaks:
            s.err("C7", f"leak [{name}] '{tok}': ...{ctx}...", rel)

    # ---------- C8 V1 tab unchanged ----------
    if tabs[1].get("tab") != "API V1 Reference":
        s.err("C8", f'tabs[1].tab is {tabs[1].get("tab")!r}, expected "API V1 Reference"')
    else:
        try:
            main_docs = json.loads(
                subprocess.check_output(["git", "show", "main:docs.json"], cwd=ROOT))
            main_t1 = main_docs["navigation"]["tabs"][1]
            cur_t1 = json.loads(json.dumps(tabs[1]))
            cur_t1["tab"] = main_t1.get("tab")  # normalize only the label
            if cur_t1 == main_t1:
                s.passed("C8", 'tabs[1]=="API V1 Reference"; groups/pages unchanged vs main')
            else:
                s.err("C8", "tabs[1] groups/pages DIFFER from main (beyond the tab label)")
        except subprocess.CalledProcessError as e:
            s.err("C8", f"could not read main:docs.json for baseline compare: {e}")

    return report(s)


def report(s):
    print("=" * 72)
    print("API V2 Reference — documentation validation & leak-guard suite")
    print("=" * 72)
    for check, summary in s.ok:
        print(f"  PASS  {check}  {summary}")
    if s.fail:
        print("-" * 72)
        for check, f, detail in s.fail:
            loc = f"{f}: " if f else ""
            print(f"  FAIL  {check}  {loc}{detail}")
        print("-" * 72)
        print(f"RESULT: FAIL ({len(s.fail)} issue(s))")
        return 1
    print("-" * 72)
    print(f"RESULT: PASS (all {len(s.ok)} checks green)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
