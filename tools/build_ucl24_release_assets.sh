#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

output="$PWD/release-assets"
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
mkdir -p "$output"

python src/ucl.py upgrade examples/quickstart.txt "$output/ucl-2.4-quickstart.txt"
python src/ucl.py upgrade examples/challenge.txt "$output/ucl-2.4-challenge.txt"
python benchmarks/long_join.py --turns 2000 --pack --out "$scratch/archive.txt"
python src/ucl.py upgrade "$scratch/archive.txt" "$output/ucl-2.4-archive.txt"
cp examples/quickstart_reply.json "$output/ucl-2.4-quickstart-reply.json"
cp examples/challenge_reply.json "$output/ucl-2.4-challenge-reply.json"
cp examples/challenge_retraction.json "$output/ucl-2.4-challenge-retraction.json"

python src/ucl.py continue "$output/ucl-2.4-quickstart.txt" "$scratch/quickstart-next.txt" < "$output/ucl-2.4-quickstart-reply.json"
python src/ucl.py continue "$output/ucl-2.4-challenge.txt" "$scratch/challenge-next.txt" < "$output/ucl-2.4-challenge-reply.json"
python src/ucl.py preflight "$output/ucl-2.4-challenge.txt" < "$output/ucl-2.4-challenge-retraction.json"
python src/ucl.py continue "$output/ucl-2.4-challenge.txt" "$output/ucl-2.4-challenge-retracted.txt" < "$output/ucl-2.4-challenge-retraction.json"

for packet in "$output"/ucl-2.4-*.txt "$scratch"/*-next.txt; do
    python src/ucl.py check "$packet" > /dev/null
    jq -e '.format == "UCL/2.4-SAP1-PORTABLE" and (.packet.guide.reply_authoring.example.explanation == "~[B][A]")' "$packet"
    node tools/check_ucl_portable.js "$packet"
done
python src/ucl.py inspect "$output/ucl-2.4-archive.txt" --handoff --claim theory --path 1 --include-act t185 \
    | jq -e '.archive_blocks_opened == 1 and .requested_acts[0].act.id == "t185" and .claim.scope.path == [1]'
python src/ucl.py template "$output/ucl-2.4-archive.txt" --speaker "New participant" --claim theory --path 1 --seed-formula \
    | jq -e '.explanation == "~[B][A]" and .conclusion == .explanation and .act.text == ""'
python src/ucl.py diff "$output/ucl-2.4-challenge.txt" "$output/ucl-2.4-challenge-retracted.txt" --compact \
    | jq -e '.counts.new_retractions == 1 and .new_retractions[0].retracts == "x4" and .new_retractions[0].cleared_current_stance'
(
    cd "$output"
    sha256sum ucl-2.4-* > SHA256SUMS.txt
    sha256sum -c SHA256SUMS.txt
)
