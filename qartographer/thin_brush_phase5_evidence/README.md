# Phase 5 unaccepted implementation evidence

The final source snapshots and `phase5-unaccepted.patch` are inert. Active P1
sources and production binaries were not patched. Final receipts are:

- `candidate-status.json`: exact final source, executable and tests hashes.
- `candidate-compiles.json` and `candidate-*/`: final four compilations, exact
  inputs/commands/hashes, logs, raw time measurements, and the successful BSP.
- `final-rank-focused.xml` / `.log`: final five tests, four pass and one fail.
- `original-source-occupancy.json`: 18 focused source/Minkowski occupancy checks.
- `phase5-witness.json`: compact unchanged coefficients/windings extracted from
  Phase 4's terminal region and ancestor/cap records. Tests use those coefficients;
  the all-ancestor case represents an exactly identical support only once.
- `preserved-witness-replay.json`: unchanged Phase 4 oracle replay, NOT acceptance.

Earlier records are retained as failures, not substituted for final results:

- `checkpoint-ab.log`: first test setup crashed (empty test texture table); no
  geometry verdict. The fixture setup was corrected, not compiler policy.
- `checkpoint-ab-retry.*`: box passes; double reconstruction fails narrow cut.
- `checkpoint-ab-precise.*`: both local cases pass with long-double reconstruction
  before the all-ancestor extension.
- `final-focused.*`: all-ancestor test initially counted identical support faces
  twice (test assembly bug), and ordinary sealed portal failed. The fixture now
  models a single original support once; no approximate plane welding is used.
- `compile-checkpoints.json`, `final-compiles.json` and corresponding non-candidate
  directories: prior iterations; their binary hashes distinguish those runs.
  Earlier executables were not separately archived. Only the final executable
  has an exact retained standalone copy; do not claim replayable archived binaries
  for the intermediate hashes.
- `build*.log`: build attempts, including diagnostic formatter compile failure;
  corrected locally without modifying shared fmt/source infrastructure.

All original MAPs and historical evidence remain in the original repository at
unchanged paths/hashes. Runtime MAP copies and compiler builds are retained only
under `/tmp/qqbsp-phase5`. Repository evidence omits duplicate runtime `.map`,
`.bsp` and generated `.prt` files; the successful raw BSP is preserved as `.bsp.bin`.
`SHA256SUMS.json` hashes the preserved evidence files. The report is hashed in
`report-sha256.txt`.

## Reconstruct/build

Use downstream HEAD 4b505ae25e508a8910b031e94d6f1ea60ac06a95, with the
baseline.json-pinned submodules/dependencies. Extract a private archive, then
replace the six files from `implementation/` snapshots, stripping only their
`.txt` suffix. Copy `phase5-witness.json` to SOURCE/qartographer/phase5-witness.json.
The validation fixture currently uses the original research path
`/tmp/qqbsp-phase5/source`; preserve that path or explicitly adjust the test path
and record its resulting source/binary identity. No production code is changed.
The experimental CMake identity is intentionally hardcoded to the parent plus
phase5-unaccepted label, rather than claiming a nonexistent algorithm commit.

Configuration used:

    cmake -S /tmp/qqbsp-phase5/source -B /tmp/qqbsp-phase5/build -G Ninja \
      -DCMAKE_BUILD_TYPE=RelWithDebInfo -DENABLE_LIGHTPREVIEW=OFF \
      -DBUILD_TESTS=OFF -DQQBSP_BUILD_TESTS=ON \
      -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
      -DFETCHCONTENT_SOURCE_DIR_JSON=/tmp/qqbsp-bootstrap/pinned/deps/json/json \
      -DFETCHCONTENT_SOURCE_DIR_GOOGLETEST=/tmp/qqbsp-bootstrap/pinned/deps/googletest \
      -DTBB_DIR=/tmp/qqbsp-bootstrap/pinned/deps/tbb/oneapi-tbb-2021.11.0/lib/cmake/tbb \
      -Dembree_DIR=/tmp/qqbsp-bootstrap/pinned/deps/embree/lib/cmake/embree-4.4.0
    cmake --build /tmp/qqbsp-phase5/build --target qqbsp qqbsp_tests -j 4

Final test filter:

    phase5.*:qbsp.duplicatePlanes:qbsp.emptyBrush:testmapsQ1.simpleSealed

Full compile commands are recorded, not inferred. Failure exits are intentional
receipts of unresolved geometry, not PASS. No two-clean-build reproducibility,
full upstream acceptance, completed matrix, native or consumer PASS is claimed.
