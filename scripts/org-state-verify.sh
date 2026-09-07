#!/usr/bin/env bash
# org-state-verify.sh — generate the Aftergraph Org State Contract from GitHub remote truth.
# Usage:
#   scripts/org-state-verify.sh [output.json]        # generate + validate (default ./latest-org-state.json)
#   scripts/org-state-verify.sh --check-local PATH1 PATH2 ...   # also verify local clones against remote heads
#
# TRUTH: GitHub remote API only. No manually typed SHA claims — ever.
# SCOPE: docs/platform-topology/1.0.json (slow-changing ownership/topology metadata).
# Requires: gh authenticated (org read access for private repos), jq.
# Exit code: 0 = generated & validated; 1 = API/schema/topology failure; 2 = local clone divergence.
set -euo pipefail

ORG="Aftergraph"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOPOLOGY="$SCRIPT_DIR/../docs/platform-topology/1.0.json"
OUT="${1:-$SCRIPT_DIR/../latest-org-state.json}"
CHECK_LOCAL=0
LOCAL_PATHS=()

if [ "${1:-}" = "--check-local" ]; then
  CHECK_LOCAL=1
  OUT="$SCRIPT_DIR/../latest-org-state.json"
  shift
  LOCAL_PATHS=("$@")
fi

if [ ! -f "$TOPOLOGY" ]; then
  echo "TOPOLOGY-FAIL: missing $TOPOLOGY" >&2
  exit 1
fi

if ! jq -e '.schema_version == "platform-topology/1.0" and .organization == "Aftergraph" and (.repositories | type == "array") and (.repositories | length > 0)' "$TOPOLOGY" >/dev/null; then
  echo "TOPOLOGY-FAIL: invalid platform-topology/1.0 envelope" >&2
  exit 1
fi

expected_count=$(jq -r '.repositories | length' "$TOPOLOGY")
duplicate_count=$(jq -r '[.repositories[].name] | group_by(.) | map(select(length > 1)) | length' "$TOPOLOGY")
if [ "$duplicate_count" != "0" ]; then
  echo "TOPOLOGY-FAIL: duplicate repository names" >&2
  exit 1
fi

# repo — role — canonical branch. This is derived from the topology contract,
# never maintained as a second hard-coded list in this script.
REPOS=()
while IFS=$'\t' read -r repo role branch; do
  [ -n "$repo" ] || continue
  REPOS+=("$repo $role $branch")
done < <(jq -r '.repositories[] | [.name, .role, .canonical_branch] | @tsv' "$TOPOLOGY")

if [ "${#REPOS[@]}" -ne "$expected_count" ]; then
  echo "TOPOLOGY-FAIL: parsed ${#REPOS[@]} repos, expected $expected_count" >&2
  exit 1
fi

# Contract ownership/consumption annotations retained for org-state/1.0.
# Detailed normative ownership is governed by docs/cross-repo-contracts.md;
# repos not explicitly mapped here emit an empty list rather than guessed claims.
contract_of() { # $1=repo
  case "$1" in
    after-graph-governance) echo '[{"name":"mission-state","version":"1.0"},{"name":"policy.token","version":"1.0"},{"name":"org-state","version":"1.0"}]' ;;
    *) echo '[]' ;;
  esac
}

consumes_of() { # $1=repo
  case "$1" in
    after-graph-governance) echo '[]' ;;
    aie) echo '[{"name":"mission-state","version":"1.0"}]' ;;
    works-execution) echo '[{"name":"mission-state","version":"1.0"}]' ;;
    trust-gateway) echo '[{"name":"mission-state","version":"1.0"},{"name":"policy.token","version":"1.0"}]' ;;
    intelligence-systems-research) echo '[{"name":"mission-state","version":"1.0"}]' ;;
    *) echo '[]' ;;
  esac
}

ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
entries=()

for spec in "${REPOS[@]}"; do
  set -- $spec
  repo="$1"; role="$2"; topology_branch="$3"
  full="$ORG/$repo"
  echo "→ $full" >&2

  meta=$(gh api "repos/$full" --jq '{default_branch, private, archived}' 2>/dev/null || { echo "  ⚠ API failed" >&2; continue; })
  branch=$(echo "$meta" | jq -r .default_branch)
  if [ "$branch" != "$topology_branch" ]; then
    echo "  ✗ TOPOLOGY DRIFT: canonical_branch=$topology_branch GitHub default_branch=$branch" >&2
    exit 1
  fi

  head_sha=$(gh api "repos/$full/branches/$branch" --jq '.commit.sha' 2>/dev/null || { echo "  ⚠ branch fetch failed" >&2; continue; })
  head_msg=$(gh api "repos/$full/commits/$head_sha" --jq '.commit.message | split("\n")[0]' 2>/dev/null || echo "?")
  protected=$(gh api "repos/$full/branches/$branch/protection" >/dev/null 2>&1 && echo true || echo false)

  # PR list lacks mergeable; preserve UNKNOWN unless a dedicated mergeability
  # query is added. Head SHA is still captured as exact identity.
  pr_list=$(gh api "repos/$full/pulls?state=open&per_page=20" --jq '[.[] | {number, title, draft, head_sha: .head.sha}]' 2>/dev/null || echo '[]')
  prs='[]'
  if [ "$pr_list" != "[]" ] && [ -n "$pr_list" ]; then
    prs=$(echo "$pr_list" | jq -c '[.[] | . as $p | {number: $p.number, title: $p.title, is_draft: $p.draft, mergeable: "UNKNOWN", head_sha: $p.head_sha}]')
  fi

  entry=$(jq -nc \
    --arg full "$full" --arg role "$role" --arg branch "$branch" \
    --arg sha "$head_sha" --arg short "${head_sha:0:7}" --arg msg "$head_msg" \
    --argjson priv "$(echo "$meta" | jq -c .private)" \
    --argjson arch "$(echo "$meta" | jq -c .archived)" \
    --argjson prot "$protected" --argjson prs "$prs" \
    --argjson auth "$(contract_of "$repo")" --argjson cons "$(consumes_of "$repo")" \
    '{full_name: $full, role: $role, canonical_branch: $branch,
      remote_head_sha: $sha, remote_head_short: $short, head_commit_message: $msg,
      private: $priv, archived: $arch, protected: $prot,
      open_pull_requests: $prs, authoritative_contracts: $auth, consumed_contracts: $cons}')
  entries+=("$entry")
done

if [ "${#entries[@]}" -ne "$expected_count" ]; then
  echo "ORG-STATE-FAIL: GitHub returned ${#entries[@]} of $expected_count topology repositories; refusing partial truth" >&2
  exit 1
fi

combined=$(jq -nc \
  --arg v "org-state/1.0" --arg ts "$ts" \
  --arg gen "$SCRIPT_DIR/org-state-verify.sh" --arg org "$ORG" \
  --argjson repos "$(printf '%s\n' "${entries[@]}" | jq -s .)" \
  '{schema_version: $v, generated_at: $ts, generator: $gen, org: $org, repositories: $repos}')

schema="$SCRIPT_DIR/../docs/contracts/org-state/1.0.json"

# Structural + schema validation. Prefer jsonschema when installed; jq fallback
# still validates the topology-derived repository count and SHA shape.
SCHEMA_WIN=$(cygpath -w "$schema" 2>/dev/null || echo "$schema")
if command -v python3 >/dev/null 2>&1 && python3 -c "import jsonschema" 2>/dev/null; then
  echo "$combined" | python3 -c "
import json, sys
from jsonschema import validate, ValidationError
doc = json.load(sys.stdin)
schema = json.load(open(r'$SCHEMA_WIN', encoding='utf-8'))
try:
    validate(doc, schema)
    print('SCHEMA-OK', file=sys.stderr)
except ValidationError as e:
    print(f'SCHEMA-FAIL: {e.message}', file=sys.stderr)
    sys.exit(1)
" || exit 1
else
  echo "$combined" | jq -e --argjson expected "$expected_count" \
    '.schema_version == "org-state/1.0" and (.repositories | length) == $expected and all(.repositories[]; (.remote_head_sha | length) == 40 and (.remote_head_short | length) == 7)' \
    >/dev/null || { echo "SCHEMA-FAIL (jq fallback)" >&2; exit 1; }
  echo "SCHEMA-OK (jq fallback)" >&2
fi

echo "$combined" | jq . > "$OUT"
echo "✓ org-state written: $OUT ($(echo "$combined" | jq '.repositories | length') repos)" >&2

if [ "$CHECK_LOCAL" = 1 ]; then
  divergent=0
  for p in "${LOCAL_PATHS[@]}"; do
    gitpath=$(cygpath -m "$p" 2>/dev/null || echo "$p")
    if [ ! -d "$gitpath/.git" ]; then echo "  ⚠ not a repo: $p" >&2; continue; fi
    name=$(basename "$p")
    local_head=$(git -C "$gitpath" rev-parse HEAD 2>/dev/null || echo "?")
    remote_of=$(echo "$combined" | jq -r --arg n "$name" '.repositories[] | select(.full_name | endswith("/" + $n)) | .remote_head_sha' 2>/dev/null || true)
    if [ -n "$remote_of" ] && [ "$local_head" != "$remote_of" ]; then
      echo "  ✗ DIVERGENCE: $name local=$local_head remote=$remote_of" >&2
      divergent=1
    else
      echo "  ✓ $name matches remote ($local_head)" >&2
    fi
  done
  [ "$divergent" = 1 ] && exit 2
fi

echo "DONE" >&2
