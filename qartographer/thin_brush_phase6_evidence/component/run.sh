#!/usr/bin/env bash
set -euo pipefail
p6_component_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
p6_output=${1:?Usage: run.sh NEW_OUTPUT_DIRECTORY}
p6_json_include=${QQBSP_P6_JSON_INCLUDE:-/tmp/qqbsp-bootstrap/pinned/deps/json/json/include}
mkdir -- "$p6_output"
p6_output=$(cd -- "$p6_output" && pwd)
c++ -std=c++20 -O2 -fno-fast-math -ffp-contract=off -Wall -Wextra \
    -Wno-misleading-indentation -Wno-mismatched-new-delete \
    -I"$p6_json_include" "$p6_component_dir/main.cpp" -lgmpxx -lgmp \
    -o "$p6_output/predicate"
c++ -std=c++20 -O2 -fno-fast-math -ffp-contract=off -Wno-misleading-indentation \
    "$p6_component_dir/selftest.cpp" -lgmpxx -lgmp -o "$p6_output/selftest"
"$p6_output/selftest" > "$p6_output/guard-tests.log"
cp -- "$p6_component_dir/../cases.json" "$p6_output/cases.json"
for p6_mode in filtered double-exact exact; do
    /usr/bin/time -v -o "$p6_output/$p6_mode.time" \
        "$p6_output/predicate" "$p6_output/cases.json" "$p6_mode" \
        > "$p6_output/$p6_mode-final.json"
done
"$p6_output/predicate" "$p6_output/cases.json" filtered --latency > "$p6_output/latency-final.json"
python3 "$p6_component_dir/validate.py" "$p6_output" > "$p6_output/oracle.log"
python3 "$p6_component_dir/check_modes.py" "$p6_output"
