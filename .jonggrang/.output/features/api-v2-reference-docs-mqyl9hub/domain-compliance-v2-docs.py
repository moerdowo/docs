#!/usr/bin/env python3
"""
Phase 11 — domain-compliance suite for the API V2 Reference docs.

Where validate-v2-docs.py checks STRUCTURE (valid JSON, nav<->file, tag balance,
leak-guard, V1 unchanged), this suite checks the DOMAIN-MANDATORY patterns every
REST API reference page in this corpus must follow. Run from repo root:

    python3 .jonggrang/.output/features/api-v2-reference-docs-mqyl9hub/domain-compliance-v2-docs.py

Exit 0 == all domain checks green. Exit 1 == one or more failed.

The 3 "API documentation" group pages (introduction/statuscode/rate-limit) are
overview pages, not endpoint pages, and are exempt from the per-endpoint checks
(D1..D6). They are validated only for the base-URL convention (D1).

Domain checks (base-URL-aware — see SERVICES below)
  D1  Base-URL fidelity: every endpoint page documents BOTH the prod and sandbox
      base URL FOR ITS OWN SERVICE (hl -> api.mayar.{id,club}/hl/v2; credit/saas/
      software -> the matching /credit|/saas|/software /v2 base), and no page leaks
      a /hl/v1 base URL.
  D2  Method+path: every endpoint page declares its HTTP verb and path via the
      `openapi:` frontmatter key (METHOD /path).
  D3  Auth documented: every endpoint page documents the Bearer Authorization
      header (Authorization + Bearer).
  D4  Request example: every endpoint page has a <RequestExample> with a curl
      snippet hitting its own service base (hl -> /hl/v2/; external services keep
      their /v1 primary curl and surface /v2 via a Note, so /credit|/saas|/software
      at either version satisfies the check).
  D5  Response envelope: every endpoint page's <ResponseExample> JSON carries the
      mandatory envelope key statusCode. For the strict (hl, credit) services it
      also carries EXACTLY ONE of message/messages (the singular/plural quirk).
      The saas/software services use per-service envelopes whose verify reads
      carry NO message key on success (statusCode + domain fields), so there the
      rule relaxes to AT MOST ONE of message/messages (never both). `data` is
      OPTIONAL — status-only writes legitimately return no data object.
  D6  Field docs: every endpoint page documents request/response fields with at
      least one ParamField or ResponseField, and documents the statusCode
      ResponseField. (The data ResponseField is required only when the response
      envelope actually carries a data object — see D5.)
  D7  No stray/unknown closing tags in PROSE (catches authoring artifacts such as
      a trailing </content> that the structural suite's 7-tag balance misses).
      Tags inside ``` code fences and inline `code` spans are excluded, since
      real API response data may legitimately embed HTML (e.g. an `<p>...</p>`
      description string inside a JSON example).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve()
while ROOT != ROOT.parent and not (ROOT / "docs.json").exists():
    ROOT = ROOT.parent
V2_DIR = ROOT / "api-reference-v2"

# overview (non-endpoint) pages exempt from D2..D6
OVERVIEW = {"introduction", "statuscode", "rate-limit"}

# --- Base-URL awareness (MR !3501) --------------------------------------------
# Only the api-custom-paymenlink surface lives under /hl/v2. MR !3501 also mirrors
# three EXTERNAL services under a /v2 prefix on their OWN gateway base:
#   credit    -> api.mayar.{id,club}/credit/v2   (Credit Based Product + Membership (Credit))
#   saas      -> api.mayar.{id,club}/saas/v2     (Membership (SaaS))
#   software  -> api.mayar.{id,club}/software/v2 (Software License Code)
# Those external pages keep their /v1 primary curl and surface the /v2 base via a
# Note, and they use PER-SERVICE envelopes (credit: message-success/messages-400;
# saas/software verify: statusCode + domain fields, NO message key on success).
# So D1/D4/D5 must be base-URL-aware: each endpoint page is classified by the base
# path it actually documents, then validated against THAT service's prod/sandbox
# base, curl base, and envelope convention — never assuming /hl/v2 universally.
SERVICES = {
    "hl": {
        "prod": "api.mayar.id/hl/v2", "sandbox": "api.mayar.club/hl/v2",
        "curl": "/hl/v2/", "strict_envelope": True,
    },
    "credit": {
        "prod": "api.mayar.id/credit/v2", "sandbox": "api.mayar.club/credit/v2",
        "curl": "/credit/v", "strict_envelope": True,
    },
    "saas": {
        "prod": "api.mayar.id/saas/v2", "sandbox": "api.mayar.club/saas/v2",
        "curl": "/saas/v", "strict_envelope": False,
    },
    "software": {
        "prod": "api.mayar.id/software/v2", "sandbox": "api.mayar.club/software/v2",
        "curl": "/software/v", "strict_envelope": False,
    },
}


_COMMENT_RE = re.compile(r"\{/\*.*?\*/\}", re.S)


def service_of(raw):
    """Classify an endpoint page by the base path it documents. /hl/v2 wins first
    (api-custom-paymenlink); external services are identified by their own base
    prefix. Defaults to hl so a page that somehow documents no base still gets the
    strict /hl/v2 checks (fails loudly rather than silently exempting itself).

    Classification runs over RENDERED content (MDX `{/* ... */}` comments stripped):
    the external-service maintainer notes mention the phrase "/hl/v2 surface" to
    explain they are NOT under it, and that prose must not mis-classify the page."""
    rendered = _COMMENT_RE.sub("", raw)
    if "/hl/v2" in rendered:
        return "hl"
    if "/credit/v" in rendered:
        return "credit"
    if "/saas/v" in rendered:
        return "saas"
    if "/software/v" in rendered:
        return "software"
    return "hl"

# Known JSX components used across the corpus; any other </Tag> is "unknown".
KNOWN_TAGS = {"RequestExample", "ResponseExample", "CodeGroup", "ParamField",
              "ResponseField", "Note", "Warning", "Tip", "Info", "Card",
              "CardGroup", "Steps", "Step", "Tabs", "Tab", "Accordion",
              "AccordionGroup", "Frame", "Expandable", "ResponseFields"}


def block(text, tag):
    m = re.search(r"<" + tag + r"\b.*?</" + tag + r">", text, re.S)
    return m.group(0) if m else ""


def strip_code(text):
    """Remove ``` fenced blocks and inline `code` spans so a stray-tag scan sees
    only rendered PROSE — real response data may embed HTML inside JSON examples."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    return text


def main():
    fails = []
    oks = []
    files = sorted(V2_DIR.rglob("*.mdx"))
    endpoint_files = [f for f in files if f.stem not in OVERVIEW]

    # Guard against a vacuous all-green: with 0 endpoint pages the count==n gates
    # (D2..D7) would all pass while asserting nothing.
    if not files or not endpoint_files:
        print("  FAIL  D0  no endpoint .mdx pages found — nothing to validate")
        print(f"RESULT: FAIL (corpus empty: files={len(files)}, "
              f"endpoints={len(endpoint_files)})")
        return 1

    d1 = d2 = d3 = d4 = d5 = d6 = d7 = 0

    for f in files:
        rel = str(f.relative_to(ROOT))
        raw = f.read_text()
        is_ep = f.stem not in OVERVIEW

        # ---- D1 base-URL fidelity (all pages), base-URL-aware ----
        svc = SERVICES[service_of(raw)] if is_ep else None
        ok1 = True
        if "/hl/v1" in raw:
            fails.append(("D1", rel, "leaks a /hl/v1 base URL into V2"))
            ok1 = False
        if is_ep:
            if svc["prod"] not in raw:
                fails.append(("D1", rel, f"missing prod base URL {svc['prod']}"))
                ok1 = False
            if svc["sandbox"] not in raw:
                fails.append(("D1", rel, f"missing sandbox base URL {svc['sandbox']}"))
                ok1 = False
        if ok1:
            d1 += 1

        if not is_ep:
            continue

        # ---- D2 method + path via openapi frontmatter ----
        fm = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw, re.S)
        fm_body = fm.group(1) if fm else ""
        m = re.search(r"^openapi:\s*[\"']?\s*"
                      r"(GET|POST|PUT|PATCH|DELETE)\s+(/\S+)",
                      fm_body, re.M)
        if m:
            d2 += 1
        else:
            fails.append(("D2", rel, "no `openapi: METHOD /path` in frontmatter"))

        # ---- D3 auth documented ----
        if re.search(r"Authorization", raw) and re.search(r"Bearer", raw):
            d3 += 1
        else:
            fails.append(("D3", rel, "Bearer Authorization not documented"))

        # ---- D4 request example w/ curl on the page's own service base ----
        req = block(raw, "RequestExample")
        if req and "curl" in req and svc["curl"] in req:
            d4 += 1
        else:
            fails.append(("D4", rel,
                          f"no <RequestExample> curl hitting {svc['curl']}"))

        # ---- D5 response envelope ----
        resp = block(raw, "ResponseExample")
        env_ok = False
        env_has_data = False
        if resp:
            jm = re.search(r"```json[^\n]*\n(.*?)\n```", resp, re.S)
            if jm:
                try:
                    obj = json.loads(jm.group(1))
                    has_sc = "statusCode" in obj
                    has_sing = "message" in obj
                    has_plur = "messages" in obj
                    env_has_data = "data" in obj
                    # strict services (hl, credit): exactly one of message/messages.
                    # relaxed services (saas, software): per-service envelope may
                    # carry NO message key on success -> at most one, never both.
                    if svc["strict_envelope"]:
                        key_ok = has_sing ^ has_plur
                        key_req = "exactly-one-of(message|messages)"
                    else:
                        key_ok = not (has_sing and has_plur)
                        key_req = "at-most-one-of(message|messages)"
                    if has_sc and key_ok:
                        env_ok = True
                    else:
                        miss = []
                        if not has_sc:
                            miss.append("statusCode")
                        if not key_ok:
                            miss.append(
                                f"{key_req}"
                                f" [message={has_sing} messages={has_plur}]")
                        fails.append(("D5", rel,
                                      "envelope keys wrong: " + ", ".join(miss)))
                except Exception as e:  # noqa: BLE001
                    fails.append(("D5", rel, f"response JSON parse: {e}"))
            else:
                fails.append(("D5", rel, "no ```json in <ResponseExample>"))
        else:
            fails.append(("D5", rel, "no <ResponseExample>"))
        if env_ok:
            d5 += 1

        # ---- D6 field docs ----
        n_param = len(re.findall(r"<ParamField\b", raw))
        n_resp = len(re.findall(r"<ResponseField\b", raw))
        has_sc_field = re.search(r'<ResponseField\s+name="statusCode"', raw)
        # data ResponseField is required ONLY when the envelope carries data (D5)
        has_data_field = re.search(r'<ResponseField\s+name="data"', raw)
        data_ok = has_data_field or not env_has_data
        if (n_param + n_resp) > 0 and has_sc_field and data_ok:
            d6 += 1
        else:
            why = []
            if (n_param + n_resp) == 0:
                why.append("no ParamField/ResponseField")
            if not has_sc_field:
                why.append('no ResponseField name="statusCode"')
            if not data_ok:
                why.append('envelope has data but no ResponseField name="data"')
            fails.append(("D6", rel, "; ".join(why)))

        # ---- D7 no unknown/stray closing tags (PROSE only) ----
        prose = strip_code(raw)
        stray = sorted({t for t in re.findall(r"</([A-Za-z][A-Za-z0-9]*)>", prose)
                        if t not in KNOWN_TAGS})
        if stray:
            fails.append(("D7", rel, "stray/unknown closing tag(s): "
                          + ", ".join(f"</{t}>" for t in stray)))
        else:
            d7 += 1

    n = len(endpoint_files)
    total = len(files)
    if d1 == total:
        oks.append(("D1", f"base-URL fidelity OK ({total} pages; prod+sandbox, no v1)"))
    for cid, cnt, label in [
        ("D2", d2, "method+path frontmatter"),
        ("D3", d3, "Bearer auth documented"),
        ("D4", d4, "request example on /hl/v2"),
        ("D5", d5, "response envelope (statusCode+data+message^messages)"),
        ("D6", d6, "field docs (statusCode+data ResponseFields)"),
        ("D7", d7, "no stray closing tags"),
    ]:
        if cnt == n:
            oks.append((cid, f"{label} on all {n} endpoint pages"))

    print("=" * 72)
    print("API V2 Reference — Phase 11 domain-compliance suite")
    print("=" * 72)
    for cid, summ in oks:
        print(f"  PASS  {cid}  {summ}")
    if fails:
        print("-" * 72)
        for cid, rel, det in fails:
            print(f"  FAIL  {cid}  {rel}: {det}")
        print("-" * 72)
        print(f"RESULT: FAIL ({len(fails)} issue(s))")
        return 1
    print("-" * 72)
    print(f"RESULT: PASS (all {len(oks)} domain checks green)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
