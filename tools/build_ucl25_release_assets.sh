#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

output="$PWD/release-assets"
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
mkdir -p "$output"
test "$(python src/ucl.py --version)" = 'UCL CLI 2.5.0 (UCL/2.5-SAP1-PORTABLE, guide UCL/1.5)'

python src/ucl.py upgrade examples/quickstart.txt "$output/ucl-2.5-quickstart.txt"
python src/ucl.py upgrade examples/challenge.txt "$output/ucl-2.5-challenge.txt"
python benchmarks/long_join.py --turns 2000 --pack --out "$scratch/archive.txt"
python src/ucl.py upgrade "$scratch/archive.txt" "$output/ucl-2.5-archive.txt"
cp examples/quickstart_reply.json "$output/ucl-2.5-quickstart-reply.json"
cp examples/challenge_reply.json "$output/ucl-2.5-challenge-reply.json"
cp examples/challenge_retraction.json "$output/ucl-2.5-challenge-retraction.json"

python src/ucl.py continue "$output/ucl-2.5-quickstart.txt" "$scratch/quickstart-next.txt" < "$output/ucl-2.5-quickstart-reply.json"
python src/ucl.py continue "$output/ucl-2.5-challenge.txt" "$scratch/challenge-next.txt" < "$output/ucl-2.5-challenge-reply.json"
python src/ucl.py preflight "$output/ucl-2.5-challenge.txt" < "$output/ucl-2.5-challenge-retraction.json"
python src/ucl.py continue "$output/ucl-2.5-challenge.txt" "$output/ucl-2.5-challenge-retracted.txt" < "$output/ucl-2.5-challenge-retraction.json"

cat > "$output/ucl-2.5-archive-reply.json" <<'JSON'
{
  "claim": "theory",
  "path": [1],
  "action": "withhold-judgment",
  "text": "Act t185 is a hypothetical observation. It does not establish the independent-input condition in t37.",
  "references": ["t185", "t37"]
}
JSON
digest=$(jq -r .packet.integrity.sha256 "$output/ucl-2.5-archive.txt")
python src/ucl.py draft-reply "$output/ucl-2.5-archive.txt" --speaker "New participant" \
    --expect-packet-sha256 "$digest" --expect-ack-action withhold-judgment \
    < "$output/ucl-2.5-archive-reply.json" > "$scratch/short-draft.json"
python src/ucl.py continue "$output/ucl-2.5-archive.txt" "$output/ucl-2.5-archive-continued.txt" \
    --expect-packet-sha256 "$digest" < "$scratch/short-draft.json"

for packet in "$output"/ucl-2.5-*.txt "$scratch"/*-next.txt; do
    python src/ucl.py check "$packet" > /dev/null
    jq -e '.format == "UCL/2.5-SAP1-PORTABLE" and (.packet.guide.version == "UCL/1.5") and (.packet.guide.reply_authoring.short_reply.example.reply.action == "withhold-judgment")' "$packet"
    node tools/check_ucl_portable.js "$packet"
done
python src/ucl.py inspect "$output/ucl-2.5-archive.txt" --handoff --claim theory --path 1 --include-act t185 \
    | jq -e '.archive_blocks_opened == 1 and .requested_acts[0].act.id == "t185" and .claim.scope.path == [1]'
python src/ucl.py template "$output/ucl-2.5-archive.txt" --speaker "New participant" --claim theory --path 1 --seed-formula \
    | jq -e '.explanation == "~[B][A]" and .conclusion == .explanation and .act.text == ""'
python src/ucl.py diff "$output/ucl-2.5-challenge.txt" "$output/ucl-2.5-challenge-retracted.txt" --compact \
    | jq -e '.counts.new_retractions == 1 and .new_retractions[0].retracts == "x4" and .new_retractions[0].cleared_current_stance'
python src/ucl.py inspect "$output/ucl-2.5-archive.txt" --handoff \
    | jq -e '.archive_blocks_opened == 0 and any(.candidate_branches[]; .claim == "theory" and .path == [1] and any(.source_links[]; .act == "t37"))'
python src/ucl.py diff "$output/ucl-2.5-archive.txt" "$output/ucl-2.5-archive-continued.txt" --compact \
    | jq -e '.counts.new_acts == 1 and .counts.stance_changes == 1 and .stance_changes[0].path == [1] and .stance_changes[0].after.action == "withhold-judgment"'

(
    cd "$output"
    sha256sum ucl-2.5-* > SHA256SUMS.txt
    sha256sum -c SHA256SUMS.txt
)
