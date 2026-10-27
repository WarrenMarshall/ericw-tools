from pathlib import Path
import json
b=Path('/tmp/qqbsp-phase8');e=b/'publish/thin_brush_phase8_evidence';status=json.loads((e/'status.json').read_text());matrix=json.loads((e/'accepted-experiment-matrix/results.json').read_text())
report='''# QQBSP Phase 8 — topology-preserving routing; partial success

2026-10-26. **Keep experimental; do not promote.** The unchanged thin-brush matrix
now compiles **42/42**, with **49,376/49,376** existing source/Minkowski occupancy
comparisons passing. Both formerly failing rotated matrix cases produce BSPs.
An independent rational replay certifies the alternative paths used by their
collision portals. Ordinary source occupancy, stock consumers, and native L-room
player movement pass.

**Halloween still has no output BSP. P1 reduced and RollerSpline still fail.**
This is a useful construction/routing correction, not completion of the mission.
No Halloween collision, opening, false-SOLID, portal-connectivity or native-engine
acceptance is claimed. Recommendation: preserve this implementation for further
work; leave installed P1 in place.

## Isolation and identities

Private source/build: `/tmp/qqbsp-phase8/{source,build}`. This is a copy of the
retained Phase 7 isolated source archive, based on accepted P1
`4b505ae25e508a8910b031e94d6f1ea60ac06a95`; it is not a modification to the active
compiler checkout. P2 remains unapplied. Reviewed the seven thin-brush reports,
Phase 6 predicate/oracle/policy, Phase 7 implementation and captures, and compiler
README, baseline, bootstrap and repository instructions. Phase 6 predicates are
byte-unchanged; there is still one authoritative `SupportedSplit`.

Final ELF: `/tmp/qqbsp-phase8/final-qqbsp`, SHA-256
`BINARY_HASH`. The restored source rebuild produces the **same ELF hash**.
This is a same-build restoration check, not two-clean-build reproducibility.
The banner says `experiment=phase8-unaccepted`.
Installed QQBSP remains
`49d766579a03701d6a5bb3560112bc756afdb8cf4488242e0b8db72668d8c8c0`.

[Status and source hashes](thin_brush_phase8_evidence/status.json),
[Phase 7 base patch](thin_brush_phase8_evidence/phase7-unaccepted.patch),
[Phase 8 incremental patch](thin_brush_phase8_evidence/phase8-on-phase7.patch),
[complete changed-file snapshots](thin_brush_phase8_evidence/implementation/).
The incremental patch passes a dry run against the preserved Phase 7 source.
No installed executable, authored MAP/.qart, Qartographer, Qrucible, VIS/LIGHT,
engine, format, actor dimensions or oracle tolerance changed. No commit, push,
deployment, new threading, asynchronous path or speculative cache was introduced.

## Reproduced failures and preserved context

The final Phase 7 ELF freshly reproduces Halloween partition 2768 and P1 CSG
partition 278. Its `testmapsQ1.simpleSealed` test freshly reproduces the specific
rotated **node-volume partition 82**. A direct rotated compile with chopping
instead encounters an earlier source-fragment CSG failure at partition 68;
these are separate captured operations, not interchangeable witnesses.

| Original operation | Exact binary64 result | Independently rounded float32 planes |
| --- | --- | --- |
| Halloween source line 6336, X=208.000061035 | Both children volume; front extent 3.406549064390434e-14 | Front and section empty |
| P1 hull 1, source line 4, partition 278, 24 supports | Extent [-1.7967265464261725e-13, 0.9496631557675607]; both children volume | Back and section empty |
| Rotated node partition 82, 14 distinct supports | Extent [-6.930295628411783e-14, 200.28220944328072]; both children volume | Back and section empty |

[Fresh reproduction](thin_brush_phase8_evidence/reproduction/),
[independent exact classifications and rational extents](thin_brush_phase8_evidence/remaining-oracle.json).
The old P1 false-positive child E still routes unchanged to its certified side;
the Phase 7 regression test passes.

Halloween's complete original capture retains all **2,397 source records**, the
seven-support BSP parent, and the failing source fragment. Fresh rational replay
again finds `(162,800,-46)` inside a SOLID source and `(222,-864,-192)` outside
every source, both strictly inside that parent. Whole-parent constant-contents
collapse is therefore still invalid. The exclusion certificate names a support
for every source; this is not a centroid-based occupancy claim.
[Fresh mixed-parent certificate](thin_brush_phase8_evidence/reproduction/halloween-node-occupancy.json).

Source and ancestor coefficients, ownership/contents, intended partitions,
windings and rejection steps are retained in fragment logs and JSON. New node
captures additionally retain **all current fragments and complete original
sources**. CSG refusals retain A, B and the intermediate input. Failed portals
retain both ancestor regions, leaf contents and contributing source supports;
no-route captures retain the exact section and graph reachability counts.
These capture the affected construction neighborhoods. For failures before
portalization, neighboring final portals do not yet exist; no fabricated final
portal context or external-connectivity proof is claimed.
The hull-2 blocker, 29-ancestor quadrilateral, sky/roof gap and rotated edge-only
portal remain in the unchanged Phase 6/7 fixtures and focused tests.

## Chosen implementation

1. **Refuse optional CSG carving atomically.** `SubtractBrush` catches only a
   construction-unsupported result. It returns the original A, which makes
   `ChopBrushes` retain the entire A/B pair. Prepared partial pieces are discarded.
   Both original occupied sets, contents, supports and owners remain. This avoids
   an unnecessary intermediate subdivision without pretending that its child is
   geometrically empty. Arithmetic uncertainty still propagates.
2. **Defer failed BSP partitions locally.** `BuildTree_r` prepares node volumes
   and the entire routed brush list before publishing. A construction failure
   excludes that existing source plane at this node and tries another. Each
   candidate is tried at most once. When ordinary winding-bearing candidates are
   exhausted, retained inactive support boundaries may be tried; a disappeared
   winding is not permission to forget its constraint. Exhaustion is an explicit
   construction diagnostic, never a constant SOLID/EMPTY leaf assignment.
3. **Make preparation private and preserve source lifetimes.** Facing brushes
   are copied before setting `onnode`, retaining their original source pointer.
   This prevents a failed attempt from poisoning later candidates or leaving
   dangling leaf source pointers. An initial missing-source-pointer bug caused
   ordinary-map crashes; it was fixed before the final candidate. The final
   ordinary compiles and native test exercise that lifetime boundary.
4. **Defer portal realization.** Area/contact decisions still use Phase 6 on
   retained supports at every split. An area-bearing portal may carry supports
   without a winding until incident leaf occupancy is available. Final construction
   first retries the existing polylib boundary constructor at long-double precision
   and rechecks rank, plane residual and incident-region containment. That shared
   constructor is factored out of the existing brush-face reconstruction.
5. **Omit only certified redundant derived portals.** SOLID/SOLID portals expose
   no boundary and carry no EMPTY connection; their leaves and collision BSP stay.
   An unconstructible EMPTY/EMPTY portal may be omitted **only in collision-hull
   outside filling**, and only when an alternative path joins its original endpoints
   through constructed EMPTY/EMPTY portals whose sections have dimension 2 in the
   float32 model and whose incident target regions have dimension 3. The full graph
   is prepared before this decision. Rendering and VIS never use this rule.
   A missing alternative path, a SOLID/EMPTY boundary or an unresolved predicate
   still rejects. No direct visible connection is removed merely because another
   bent route exists.

Changed pathways: `brushbsp.cc` (CSG, partition preparation/selection, private
routing, diagnostics); `supported_geometry.hh` (shared existing constructor);
`portals.cc/.hh` (deferred realization and collision-only reachability proof);
`qbsp.cc` (enables the rule only in the established nonzero collision-hull branch);
QQBSP CMake banner; focused tests and one frozen failed-portal fixture.
`brush.cc`, P1, and the predicate header are unchanged. The previous whole-node
constant-SOLID recovery is superseded by explicit local partition deferral;
no competing collapse/split path is retained.

## Occupancy and connectivity argument

CSG refusal preserves the **complete original source pair**, point for point, in
both coefficient models. It does not delete either fragment or change the rest
of the source union. Successful BSP partitions use the original shared split,
including all inherited supports and ownership. Trying a different source plane
changes subdivision order, not the requested occupied set. Publication remains
conditional on the existing construction and terminal-coverage checks.

Portal omission changes no plane, leaf contents, brush or source contribution.
SOLID/SOLID incidence cannot provide traversable empty space. For an EMPTY/EMPTY
edge, an alternative path in the unchanged graph preserves reachability between
its endpoints and therefore between every external vertex pair. Applying this
only to collision filling preserves its flood connectivity; it makes no visibility
claim. Every alternative edge is independently area-bearing in both models, and
its incident target regions have volume. Lower-dimensional contact cannot be
promoted into an area portal. Collision boundaries are still emitted from the
unchanged BSP leaves and source-supported partitions.

For the two rotated matrix outputs, all **16 omissions**, with **32 alternative
edges in their recorded paths**, pass an independent Fraction/Fourier–Motzkin
replay: source and target section dimension 2, incident source and target volume,
and a continuous path between the original empty endpoints. All paths have two
edges. [Machine-checkable proof receipts](thin_brush_phase8_evidence/route-verification.json)
and per-case `node.json.portal-proofs.jsonl` retain the coefficients and endpoint
regions. These are local graph proofs, not a general source-union simplifier.

The new real-P1 regression refuses an unconstructible sole EMPTY/EMPTY connection
in collision mode, refuses it for rendering, and permits only SOLID/SOLID internal
omission. Together with the retained coverage tests and freshly replayed Phase 6
policy study, this retains the thin separating-wall, genuine-gap and meaningful
blocker negative tests. [Seven focused tests](thin_brush_phase8_evidence/final-focused.xml)
pass; [policy replay](thin_brush_phase8_evidence/policy/practical-policy-results.json)
refuses deletion of the coincident-float32 adversarial separating wall.
No minimum thickness, epsilon deletion, welding, perturbation or fallback contents
classification is introduced.

This argument does **not** certify all inherited winding closure, mixed-material
CSG presentation, global source/serialized occupancy or native engine arithmetic.
The unchanged matrix and ordinary tests supply bounded output evidence below.

## Remaining concrete failures

* **Halloween off/on AUTO:** gets past original D by deferral, then exhausts one
  local partition at node-volume partitions **9240 / 14188**. The final off
  parent has 18 distinct supports. Its extent is
  `[-11.313708498984777, 5.684341886080802e-14]`; the front exists in binary64
  but is empty in the float32 model. Cap/face clipping loses a child boundary.
  No ancestor restructuring or complete neighborhood quotient has been certified.
* **P1 reduced:** passes the original optional CSG failure, builds its hull-1
  tree and certifies several redundant collision portals. It then refuses a
  different EMPTY connection with no target-representable alternative route.
  The captured section has 23 distinct constraints, dimension 2 in binary64
  and is empty in float32. Its graph has 155 certified vertices; 155 vertices
  are reachable from the first endpoint, but the other endpoint is absent.
  This is missing proof of a representable connection, not permission to remove
  it. Original source constraints remain in the accompanying node/CSG captures.
* **Rotated sealed room (not the thin matrix):** advances beyond earlier choices
  but exhausts a node at partition **122**. The room's full actor compile still
  fails. Its hull-0-only output remains available.
* **RollerSpline:** both modes still exhaust two local partitions. A separate
  single-thread capture reaches a one-candidate exhaustion and retains a
  22-constraint node cut at X=-1344, extent approximately
  `[-2.614582845563001e-8,16]`. Both children and the section survive float32
  rounding. This is a **representable construction/conditioning case**, distinct
  from Halloween's disappearing child. It must not be dismissed as target-empty.

[Final campaign](thin_brush_phase8_evidence/accepted-experiment-campaign/results.json),
[Roller modes](thin_brush_phase8_evidence/accepted-experiment-roller/results.json),
[Roller full context](thin_brush_phase8_evidence/roller-context/),
[exact remaining-witness replay](thin_brush_phase8_evidence/remaining-oracle.json).
The directory name `accepted-experiment-*` only identifies the selected final
experimental artifact; it is **not an acceptance or promotion receipt**.

A bounded reconstruction follow-up reused Phase 6 homogeneous candidates for
float32-area-bearing sections and refused narrowing that changed distinctness
or projected orientation. It did not restore P1, RollerSpline or the rotated
room, so it was **removed from the final implementation**. Its patch, source,
ELF hash and failure logs remain under `rejected-reconstruction/` and `/tmp`.
No unrestricted exact polyhedral engine or competing splitter was retained.

The existing `regress.py ... --full` campaign was attempted. Pristine controls
ran, including full maps; the final candidate aborts at its reduced compile,
so the driver subsequently has no reduced results JSON. This is an incomplete
P1 campaign, not a PASS. Both Roller modes were separately attempted to avoid
hiding the second compile behind the driver's first assertion.

## Unchanged 42-case matrix

Every original sample, hull radius, actor offset, boundary exclusion and expected
contents is unchanged. The supplemental wrapper only aggregates compile failures
instead of aborting before later cases, and requests diagnostic captures. The
original probe source itself is untouched. All 42 final outputs pass. Each row
below names a separate compilation; comparisons cover hulls 0/1/2.

| Case | Seconds | Occupancy comparisons | Mismatches |
| --- | ---: | ---: | ---: |
'''.replace('BINARY_HASH',status['binary_sha256'])
for name,r in matrix.items():report+=f"| {name} | {r['seconds']:.3f} | {sum(r['counts'].values())} | {len(r['failures'])} |\n"
report+='''
[All results and BSP hashes](thin_brush_phase8_evidence/accepted-experiment-matrix/results.json).
Final raw BSP bytes are preserved as `.bsp.bin`; disposable original `.bsp` paths
remain under `/tmp/qqbsp-phase8/evidence/accepted-experiment-matrix`.
The hull-2 front blocker and 29-ancestor winding also retain their passing local
realization tests. These are not substituted for a Halloween final hull-2 check.

## Ordinary output, consumers and native evidence

Three ordinary final BSP29 outputs have zero differences from the retained P1
controls in **3,584** contents comparisons. A separate ordinary L-room `-nofill`
run passes **1,536** independent source/Minkowski checks over hulls 0/1/2, with
zero P1 differences. Filled exteriors are compared to P1, not incorrectly to an
unfilled raw-source union.
[Ordinary comparisons](thin_brush_phase8_evidence/ordinary-comparison/results.json),
[unfilled source oracle](thin_brush_phase8_evidence/ordinary-nofill/results.json).

The Phase 7 rotated hull-0 extra face is investigated: P1 has 6 faces, Phase 8 has
7. One side wall is split into two faces. Exact rational projected edge cancellation
shows that those faces tile the same original wall boundary; their texture vectors
and flags are identical. All other face groups retain those mappings. A floor
edge additionally gains a float32-rounded T-junction vertex, so exact projected
floor boundary equality is not claimed. This narrows the rendering concern but
is not a textured visual acceptance pass.
[Face geometry](thin_brush_phase8_evidence/rotated-render-faces.json),
[exact subdivision check](thin_brush_phase8_evidence/rotated-render-verification.json).

Stock VIS and LIGHT consume the final L-room BSP29: 2 visibility bytes and
456 lighting bytes. Plane, node, clipnode and model lumps remain unchanged.
Native extracted QrustyQuake exits normally, with both saves and advancing server
time. The live grounded WALK player moves from `(-56,-96,88.03125)` to
`(79.96875,-96,88.03125)`. The independent source/configuration-space ray predicts
first blocking X=80; runtime stops exactly 1/32 unit before it, and X=80.1 is
source-solid. No installed engine/assets or consumer tools were modified.
[Native/consumer receipt](thin_brush_phase8_evidence/native-ordinary-final/results.json).
This preserves the ordinary movement regression. It does not certify Halloween,
native thin player/large actors, textured rendering or entity behavior on full maps.

## Runtime, memory and PRECISE limits

Single observations, not controlled performance comparisons. Some exploratory
builds/compiles overlapped. No historical speed budget was an acceptance criterion.

| Final invocation | Result | Wall seconds | Peak RSS KiB | BSP bytes |
| --- | --- | ---: | ---: | ---: |
| P1 reduced | Missing alternative portal proof | 13.21 | 9,244 | none |
| Rotated room, actors | Local partitions exhausted | 1.15 | 8,108 | none |
| Ordinary sealed | Output | 0.65 | 7,676 | 1,680 |
| Ordinary rotated hull 0 | Output | 0.27 | 7,416 | 1,500 |
| Ordinary L-room | Output | 3.14 | 8,776 | 2,288 |
| Halloween off AUTO | Local partitions exhausted | 8.40 | 56,864 | none |
| Halloween on AUTO | Local partitions exhausted | 8.48 | 58,624 | none |

Both smoothing configurations were also attempted with `-forcegoodtree` using the
preserved earlier Phase 8 artifact `a20d6b2b6edd3eccdfda6c6e90dbdc0b058847c2754951e24b8f38cec712703a`.
Each was stopped at 300 seconds, exit 124. Off/on RSS: **40,032 / 42,876 KiB**;
user CPU: **299.92 / 299.83 seconds**. `/usr/bin/time` wraps `timeout`, so these
resource receipts include the interrupted child instead of losing its accounting.
They remain **INCOMPLETE**, not geometric failures or final-ELF PRECISE acceptance.
Both logs stop in initial BSP candidate selection after reporting visible sides;
they do not reach the later collision-only portal rule. That finite candidate
scan invokes the inherited expensive support enumerator repeatedly. CPU activity
shows active computation; the receipts do not quantify completed candidates or
prove useful progress per unit time. There is no measured memory explosion or
observed nontermination. No optimization/threading project was started.
[PRECISE receipts](thin_brush_phase8_evidence/precise/).
An earlier 900-second exploratory run had incomplete accounting and was stopped;
it is not used for resource or geometry conclusions.

## Reproduction and next boundary

Use only disposable paths; never compile directly beside authored maps.
Apply the retained Phase 7 patch once to an isolated accepted-P1 archive with its
pinned submodule sources, then apply `phase8-on-phase7.patch`. Do not apply either
to an already-patched tree. The retained final source can be rebuilt directly:

```sh
cmake -S /tmp/qqbsp-phase8/source -B /tmp/qqbsp-phase8/build -G Ninja \\
  -DCMAKE_BUILD_TYPE=RelWithDebInfo -DQQBSP_BUILD_TESTS=ON \\
  -DFETCHCONTENT_SOURCE_DIR_GOOGLETEST=/tmp/qqbsp-bootstrap/pinned/deps/googletest \\
  -DFETCHCONTENT_SOURCE_DIR_JSON=/tmp/qqbsp-bootstrap/pinned/deps/json/json \\
  -DTBB_DIR=/tmp/qqbsp-bootstrap/pinned/deps/tbb/oneapi-tbb-2021.11.0/lib/cmake/tbb \\
  -Dembree_DIR=/tmp/qqbsp-bootstrap/pinned/deps/embree/lib/cmake/embree-4.4.0
cmake --build /tmp/qqbsp-phase8/build --target qqbsp qqbsp_tests -j 4
/tmp/qqbsp-phase8/build/qartographer/qqbsp_tests \\
  --gtest_filter='phase5.*:phase7.*:phase8.*:qbsp.duplicatePlanes:qbsp.emptyBrush'
python3 /tmp/qqbsp-phase8/run_matrix.py /tmp/qqbsp-phase8/final-qqbsp /tmp/phase8-new-matrix
python3 /tmp/qqbsp-phase8/verify_routes.py
```

`verify_routes.py` verifies the frozen final proof receipts; its input path is
explicit, not implicitly switched to a newly generated matrix. Campaign commands,
input hashes, exits and time/RSS are recorded per case. Drivers are preserved with
their actual absolute research paths. The independent oracle/policy component is
also copied into this evidence; retained drivers importing Phase 7 expect that
unchanged component there. Runtime TBB libraries remain beside the isolated ELF.
Raw BSPs, source trees, all exploratory logs and the rejected reconstruction ELF
remain under `/tmp/qqbsp-phase8`. Evidence hashes are in `manifest.json`.

The next missing construction is now bounded by actual witnesses: a conditioned
representable Roller cut, and ancestor-level restructuring or a stronger coupled
representation proof for the target-empty Halloween/P1 regions. Same float32
planes, smallness and graph reachability through unsupported edges are not proofs.
No general unsupported-source conclusion follows merely from exhausting the
current node's available planes. Global terminal EMPTY exclusion, full target
occupancy certification and inherited boundary-closure guarantees also remain
unfinished. An actual Halloween BSP, its genuine roof opening and false-SOLID
witnesses, meaningful final actor blockers, and native gameplay acceptance remain
mandatory before promotion.
'''
(b/'publish/THIN_BRUSH_PHASE8.md').write_text(report)
