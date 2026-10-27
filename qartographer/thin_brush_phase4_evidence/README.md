# Phase 4 research receipts

Findings only. `probe.py` is read-only and replays preserved failure evidence;
PASS means the known counterexamples reproduce, never compiler acceptance.
`geometric-contract.md` and `production-gate-proposal.md` are proposals only.

`witness-index.json` hashes original Phase 1–3 receipts, frozen MAPs and traces.
Original first-cap, sky/gap, portal and CSG regressions remain in their existing
locations. `hull0-path.json` retains the new source-15143 fragment and volume
sequence; `ancestor-cap.json` contains all 29 true branch constraints plus the
independently reconstructed cap. `actor-tree4/5.tsv`, `actor-contents.tsv`,
`actor-leak-portals.tsv` and `actor-*-blocker.tsv` preserve the new actor witness.
The original compiler oracle scripts are not modified.

Disposable builds and complete trees/logs/BSPs are under /tmp/qqbsp-phase4.
All compiler runs copy the locked full-off.map and execute:

    qqbsp -bsp2 -notex -nopercent -chopfragment -threads 1 -loghulls input.map

The time receipts preserve exact absolute command paths. Final source is under
`instrumentation-source/`, intentionally inert `.txt` files. The two patches
show changes from the already-instrumented Phase 3 diagnostic, NOT production.
Research Python construction/analysis scripts retain absolute /tmp paths and
historical intermediate steps, including the initial compile diagnostics.
`instrument.py` alone is an intermediate construction script, not a turnkey
final build: final source snapshots are authoritative.

For a full trace rebuild, make a new disposable copy of the preserved Phase 3
source, then copy the final four source snapshots to qbsp/{brushbsp,outside,
portals,qbsp}.cc. Leave the inherited uniform diagnostic source changes separate
from active production. Configure a new build with the same CMake parameters:

    cmake -S SOURCE -B BUILD -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -DENABLE_LIGHTPREVIEW=OFF -DBUILD_TESTS=OFF -DQQBSP_BUILD_TESTS=OFF \
      -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
      -DFETCHCONTENT_SOURCE_DIR_JSON=/tmp/qqbsp-bootstrap/pinned/deps/json/json \
      -DFETCHCONTENT_SOURCE_DIR_GOOGLETEST=/tmp/qqbsp-bootstrap/pinned/deps/googletest \
      -DTBB_DIR=/tmp/qqbsp-bootstrap/pinned/deps/tbb/oneapi-tbb-2021.11.0/lib/cmake/tbb \
      -Dembree_DIR=/tmp/qqbsp-bootstrap/pinned/deps/embree/lib/cmake/embree-4.4.0
    cmake --build BUILD --target qqbsp -j 4

Use a new output directory. One worker is required by this research logging's
global pass/path state; this does not introduce a new asynchronous architecture.
The final instrumented executable is e2d97785... as recorded in status.json;
path-dependent debug data can change a reconstructed binary hash. The first two
trace executables were rebuilt in place and were not separately hash-archived.
All three resulting BSPs match byte-for-byte, but this is not a clean-build
reproducibility claim. Do not deploy any instrumented executable.
