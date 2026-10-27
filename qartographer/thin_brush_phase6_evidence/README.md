# Phase 6 standalone experiment — no compiler integration

Final authoritative records:

- `cases.json`: 87 frozen systems, including actual actor-route and portal-site inputs.
- `coefficient-hex.json`: exact binary64 spellings for every supplied coefficient.
- `filtered-final.json`, `double-exact-final.json`, `exact-final.json`: final binary,
  same cases; `oracle-results.json` / `oracle-final.log`: independent strict FME.
  86 definitive cases agree geometrically. One unbounded case explicitly expects
  API Unresolved while the reference correctly reports dimension 3.
- `summary.json`: counters, timings and memory; `final-*.time`: raw process receipts.
  `latency-final.json` is a separate instrumented run, not throughput evidence.
- `actor-actual-region.json`: source-13366 post-CSG fragment 4712 intersected with
  all 12 true pre-partition ancestors. The box control does not substitute for it.
- `portal-site.json`: original failing `SplitNodePortals.front` winding and both
  incident regions. `base-winding-site.json`, `make-portal-site.json`: actual
  oblique-site constraints; make-portal also includes its boundary portal planes.
- `minimized-blockers.json`: minimized D/E/F mathematical counterexamples. These
  may be unbounded without their original domains; they do not replace API fixtures.
- `exact-extents.json`: exact rational projections independent of C++ construction.
- `source-route-results.json`: exact segment/halfspace checks on both unchanged
  source-reader route models, not BSP/engine acceptance.
- `practical-policy-results.json`: no minimum thickness; safe full-parent internal
  divider merges only with source coverage and external topology obligations.
  Missing semantic context withholds collapse approval, not geometry classification.
- `bsp-quantized-cases.json`, `bsp-quantized-results.json`, `bsp-quantized-oracle.json`:
  seven separate binary32-plane models, not changed binary64 expectations.
- `provenance.json`: exact source, binary, dependency/runtime and input identities.
  `SHA256SUMS.json` hashes all preserved evidence, including component source.

Earlier build failures and pre-refinement 78-case measurements remain labelled
by their older names. `build.log` is the missing-Boost-header attempt; installed
GMP was used instead. Intermediate executable hashes were not separately archived.
The final executable is `/tmp/qqbsp-phase6/predicate`; the guard test executable
is `/tmp/qqbsp-phase6/selftest`. Their hashes in provenance identify the final run.
No reproducible-two-clean-build or production release receipt is claimed.

## Reproduce the standalone component

From repository root, with installed GMP development headers/libraries:

    bash qartographer/thin_brush_phase6_evidence/component/run.sh /tmp/qqbsp-phase6-replay-new

The output must not exist. Set `QQBSP_P6_JSON_INCLUDE` if the reference pinned
nlohmann-json include directory is elsewhere. The tested compiler is GCC 13.3,
C++20, -O2, -fno-fast-math, -ffp-contract=off. System GMP is 6.3.0. Sources are
standalone and are not added to any active compiler target. GMP is not vendored.

For the separate pragmatic policy and target-format study, after that command:

    python3 qartographer/thin_brush_phase6_evidence/component/practical_policy.py /tmp/qqbsp-phase6-replay-new
    /tmp/qqbsp-phase6-replay-new/predicate /tmp/qqbsp-phase6-replay-new/bsp-quantized-cases.json filtered > /tmp/qqbsp-phase6-replay-new/bsp-quantized-results.json
    python3 qartographer/thin_brush_phase6_evidence/component/quantized_check.py /tmp/qqbsp-phase6-replay-new
    python3 qartographer/thin_brush_phase6_evidence/component/project_extents.py /tmp/qqbsp-phase6-replay-new
    python3 qartographer/thin_brush_phase6_evidence/component/minimize.py /tmp/qqbsp-phase6-replay-new
    python3 qartographer/thin_brush_phase6_evidence/component/source_route.py /tmp/qqbsp-phase6-replay-new

The source-route script reads the original repository at its reference host path.
The default frozen-case replay does not need any QQBSP build, MAP compilation or
read-only probe rebuild. `fixtures.py` records the original extraction process;
its reference paths require the preserved Phase 3–5 input/probe snapshots. The
published cases and hashes are sufficient to reproduce predicate decisions.

## Read-only site probe

`read-only-probe.patch` applies ONLY to a disposable Phase 5 experimental source,
not accepted P1. Reconstruct that source using Phase 5's preserved snapshots on
HEAD 4b505ae25e508a8910b031e94d6f1ea60ac06a95, then apply this diagnostic patch.
`probe-source/` holds the complete final two changed files as inert `.txt` snapshots.
All geometry policies remain Phase 5's unaccepted policies. The new code dumps
inputs before the old rank exception; it never calls the standalone predicates.
One existing compiler worker is selected for the probe's deterministic logging.

The configure options match the Phase 5 reference build: RelWithDebInfo,
ENABLE_LIGHTPREVIEW=OFF, BUILD_TESTS=OFF, QQBSP_BUILD_TESTS=ON,
FETCHCONTENT_FULLY_DISCONNECTED=ON, with the pinned JSON/Googletest/TBB/Embree
paths documented in Phase 5. Build only `qqbsp_tests`. Run only:

    qqbsp_tests --gtest_filter=testmapsQ1.simpleSealed

The expected process exit is 1 on the original rotated-fixture rank diagnostic.
This is a captured failure site, not an upstream test PASS. No full compiler
acceptance campaign, Halloween rebuild, installation or deployment occurred.
