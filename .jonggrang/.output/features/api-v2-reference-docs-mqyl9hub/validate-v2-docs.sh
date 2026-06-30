#!/usr/bin/env bash
# Entrypoint for the API V2 Reference documentation-validation & leak-guard suite.
# Run from the repo root:  bash .jonggrang/.output/features/api-v2-reference-docs-mqyl9hub/validate-v2-docs.sh
# Exit 0 == all checks green.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# walk up to the repo root (dir containing docs.json)
ROOT="$HERE"
while [ "$ROOT" != "/" ] && [ ! -f "$ROOT/docs.json" ]; do ROOT="$(dirname "$ROOT")"; done
cd "$ROOT" || exit 2

# Check (1) as the task specifies it literally: python3 -m json.tool.
if ! python3 -m json.tool docs.json >/dev/null; then
  echo "FAIL: docs.json is not valid JSON (python3 -m json.tool)"
  exit 1
fi

# Combined gate (closes G1/R1): run BOTH the structural suite (C1-C8) AND the
# domain-compliance suite (D1-D7), then AND their exit codes. A green run here
# proves both structural integrity and domain compliance — not just one.
rc=0

echo "### Structural suite (C1-C8) ###"
python3 "$HERE/validate-v2-docs.py" || rc=1

echo ""
echo "### Domain-compliance suite (D1-D7) ###"
python3 "$HERE/domain-compliance-v2-docs.py" || rc=1

echo ""
if [ "$rc" -eq 0 ]; then
  echo "GATE: PASS (structural 8/8 + domain 7/7)"
else
  echo "GATE: FAIL (one or more suites failed — see FAIL lines above)"
fi
exit "$rc"
