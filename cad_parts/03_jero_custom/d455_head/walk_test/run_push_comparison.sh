#!/usr/bin/env bash
# Pushed walk test over many push patterns, for each payload case. Appends one line per run to results.csv.
#   bash cad_parts/03_jero_custom/d455_head/walk_test/run_push_comparison.sh [first_seed] [last_seed]
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
cd "$ROOT"
OUT="$HERE/results.csv"
[ -f "$OUT" ] || echo "case,seed,result,fell_at_s" > "$OUT"
for s in $(seq "${1:-101}" "${2:-140}"); do
  for c in baseline new_head_nominal; do
    line="$(.venv/Scripts/python.exe training/jero_sim.py --payload-file "$HERE/${c}_payloads.json" gate -o upstream/Open_Duck_Mini/BEST_WALK_ONNX_2.onnx --seed "$s" --push --push-mag 0.3 2>&1 | grep -E "no fall|fell at" | head -1)"
    if echo "$line" | grep -q "no fall"; then echo "$c,$s,pass," >> "$OUT"; else echo "$c,$s,fall,$(echo "$line" | sed -E 's/.*t=([0-9.]+)s.*/\1/')" >> "$OUT"; fi
  done
done
echo DONE
