#!/usr/bin/env python3
"""
Phase 16 — path-aware documented-vs-example field parity for a V2 reference page.

Replaces the Phase 14/15 T6 check, which compared a FLAT SET of example keys
against a FLAT SET of `<ResponseField name=...>` values. That comparison is
blind to nesting: when a key name is reused at two depths (here `id` and `name`
appear under both `coupons` and `coupons.products`), an entire documentation
section can be deleted and the flat sets still match exactly. Proven empirically
in test-quality.md F2.

This version compares PER STRUCTURE. The page groups its ResponseFields under
`### <path> Structure (...)` headings; each heading is resolved to a node in the
response example and the two key sets are compared at that node only.

    python3 field-parity-check.py api-reference-v2/discount/index.mdx

Exit 0 == parity holds at every documented structure. Exit 1 == mismatch.
"""
import json
import re
import sys
from pathlib import Path

# Header blocks that document a request header, not a response field.
NON_RESPONSE_SECTIONS = {"Authorization"}

HEADING_RE = re.compile(r"^###\s+(.+?)\s+Structure\s*\(", re.M)
FIELD_RE = re.compile(r'<ResponseField\s+name="([^"]+)"')


def example_nodes(page_text):
    """Map dotted path -> set of child keys, for every object node in every
    ```json example. Arrays are transparent (an array of objects contributes its
    items' keys at the array's own path)."""
    nodes = {}

    def walk(obj, path):
        if isinstance(obj, dict):
            nodes.setdefault(path, set()).update(obj.keys())
            for k, v in obj.items():
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for item in obj:
                walk(item, path)

    for m in re.finditer(r"```json[^\n]*\n(.*?)\n```", page_text, re.S):
        walk(json.loads(m.group(1)), "")
    return nodes


def resolve(heading, nodes):
    """`Main` -> root. Otherwise the heading is a dotted path with the container
    prefix elided (`coupons` means `data.coupons`); resolve it as a unique
    path suffix."""
    if heading == "Main":
        return ""
    if heading in nodes:
        return heading
    cands = [p for p in nodes if p == heading or p.endswith("." + heading)]
    if len(cands) == 1:
        return cands[0]
    return None


def main(argv):
    if len(argv) != 2:
        print(f"usage: {argv[0]} <page.mdx>", file=sys.stderr)
        return 2
    page = Path(argv[1])
    text = page.read_text()
    nodes = example_nodes(text)

    # Split the page into `### ... Structure (...)` sections.
    heads = list(HEADING_RE.finditer(text))
    if not heads:
        print(f"  FAIL  P0  {page}: no `### <path> Structure (...)` headings found")
        return 1

    problems = []
    print("=" * 72)
    print(f"Field parity (path-aware) — {page}")
    print("=" * 72)

    documented_paths = set()
    for i, h in enumerate(heads):
        name = h.group(1)
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        section = text[h.end():end]
        fields = set(FIELD_RE.findall(section)) - NON_RESPONSE_SECTIONS

        path = resolve(name, nodes)
        if path is None:
            problems.append(f"heading `{name}` resolves to no node in the example")
            print(f"  FAIL  {name:<20} heading matches no example node")
            continue
        documented_paths.add(path)

        expected = set(nodes[path])
        missing = sorted(expected - fields)   # in example, undocumented
        orphan = sorted(fields - expected)    # documented, not in example
        label = path or "(root)"
        if missing or orphan:
            if missing:
                problems.append(f"{label}: undocumented key(s) {missing}")
            if orphan:
                problems.append(f"{label}: orphan ResponseField(s) {orphan}")
            print(f"  FAIL  {name:<20} path={label:<24} "
                  f"missing={missing} orphan={orphan}")
        else:
            print(f"  PASS  {name:<20} path={label:<24} {len(expected)} field(s)")

    # Every object node in the example must have a documenting section.
    undocumented = sorted(set(nodes) - documented_paths)
    for p in undocumented:
        problems.append(f"example node `{p or '(root)'}` has no documenting section")
        print(f"  FAIL  {'<no heading>':<26} example node `{p or '(root)'}` undocumented")

    print("-" * 72)
    if problems:
        for p in problems:
            print(f"  * {p}")
        print(f"RESULT: FAIL ({len(problems)} issue(s))")
        return 1
    print(f"RESULT: PASS (parity holds at all {len(documented_paths)} structures)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
