#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
test "$(python src/ucl.py --version)" = 'UCL CLI 2.4.1 (UCL/2.4-SAP1-PORTABLE, guide UCL/1.4)'
python -m zipfile -e evidence/ucl24-missing-source-relays.zip "$scratch"
archive="$scratch/research/starting.txt"
original="$scratch/research/recovered-reply.txt"
next="$scratch/replayed.txt"

python src/ucl.py check "$archive" >/dev/null
python src/ucl.py inspect "$archive" --handoff --claim theory --path 1 --include-act t185 \
    | jq -e '.briefing_version == 2 and .source_format == "UCL/2.4-SAP1-PORTABLE"
        and .archive_blocks_opened == 1 and .requested_acts[0].act.id == "t185"
        and (.open_issue.source | startswith("/packet/history/unresolved/"))
        and any(.claim.acknowledgements[]; .ack_id == "condition37" and .author_act == "t37" and .source_act == "t1")'
jq -e '.contribution' "$scratch/research/recovered-raw.txt" > "$scratch/contribution.json"
python src/ucl.py preflight "$archive" < "$scratch/contribution.json"
python src/ucl.py continue "$archive" "$next" < "$scratch/contribution.json"
python src/ucl.py check "$next" >/dev/null
node tools/check_ucl_portable.js "$original"
node tools/check_ucl_portable.js "$next"
test "$(jq -r .packet.integrity.sha256 "$next")" = "$(jq -r .packet.integrity.sha256 "$original")"
python src/ucl.py diff "$archive" "$next" --compact \
    | jq -e '.counts.new_acts == 1 and .counts.stance_changes == 1 and .stance_changes[0].path == [1]'
