# QQBSP Phase 5 — implemented experimental slice; incomplete, revise

2026-10-26. **Not an accepted compiler correction.** An isolated implementation
now preserves the two primary local geometry witnesses. The coherent full-map
slice remains blocked by numerical extent certification and portal rank handling.
P1, P2, active compiler sources, authored inputs and installed binaries are unchanged.

## 1. Implementation and production boundary

Implementation: `/tmp/qqbsp-phase5/source`, a Git archive of downstream HEAD
`4b505ae25e508a8910b031e94d6f1ea60ac06a95` with copied pinned submodule sources.
This starts from accepted P1, not the rejected uniform-epsilon experiment. Read
root AGENTS.md, README/baseline, BOOTSTRAP, NATIVE_ENGINE, all four thin-brush
reports and their relevant witness/provenance records. No new kernel, threads,
format, actor dimensions, exporter behavior or VIS/LIGHT changes were introduced.

The recoverable implementation is [the inert patch](thin_brush_phase5_evidence/phase5-unaccepted.patch),
with complete changed-file snapshots under `thin_brush_phase5_evidence/implementation/`.
The experimental CMake identity explicitly says `experiment=phase5-unaccepted`.
It does not identify this as an accepted P3 or production release. The archive
build uses a fixed experimental parent label; exact file/binary hashes, rather
than that label alone, identify this candidate.

Final executable SHA-256:
`6124279cd12d8a9c6bfb549f11a4e6f522df9cc419aef8329aa3cb18c0602793`.
An exact executable copy remains `/tmp/qqbsp-phase5/phase5-unaccepted-qqbsp`;
its adjacent build directory retains the runtime libraries and symbols.
[Source/artifact status](thin_brush_phase5_evidence/candidate-status.json)
records source-file and test-executable hashes. No two-clean-build or output
determinism certification is claimed.

## 2. Shared operation and changed responsibilities

The intended contract is the Phase 4 supported-halfspace contract: bounds may
conservatively over-report intersection; source/ancestor constraints define the
parent; both children retain those constraints and opposing partition supports;
heuristic exhaustion cannot prove constant occupancy; portals must remain in
both incident regions. **The implementation below is a partial realization of
that contract, not a complete certificate.**

* `supported_geometry::distance`: evaluates represented point/plane distance
  with long-double arithmetic and a magnitude-dependent arithmetic enclosure.
* `box_side` / `BoxOnPlaneSide`: exclusive answers require separation of the
  complete bounding box from the plane. Contact/uncertainty returns BOTH.
  The 0.001 geometric dead band is removed rather than replaced by another
  minimum thickness. Leading/trailing corners retain efficient box rejection.
* `winding_rank`: uses oriented triangle area with an arithmetic error estimate,
  rather than requiring three long edges. Fewer than three vertices is explicitly
  lower-dimensional; unresolved area is uncertainty, not certified empty.
* `boundary_residual_ok` / `BoundaryConsistent`: check face-plane and parent
  halfspace residuals. The double-scale bound is a **backward residual filter**,
  not a proven forward intersection/conditioning bound.
* `ReconstructFace` / `SupportedBoundary`: when stored windings are inconsistent,
  privately reconstruct from retained planes using the existing templated
  polylib clipping with long-double coordinates; narrow back to existing double
  windings and recheck residuals. Preserve original source ownership. No convex
  hull, approximate plane merging, coordinate inflation or welding is used.
* `SupportedSplit`: one actual operation for node volumes, brush fragments and
  CSG. Exact support identity handles facing. Otherwise it resolves extents,
  constructs and checks the cap, clips faces, retains **every parent halfspace**
  even when its winding becomes empty, adds opposing caps, validates children
  and refuses silent tiny-volume removal. `microvolume` cannot silently authorize
  deletion of a resolved child; that situation now raises a diagnostic.
* `CheckSplitBrush` / `CheckPlaneAgainstVolume`: admission calls `SupportedSplit`
  and examines its children. The independent stack-based duplicate implementation
  and mostly-side split fallback are removed. This deliberately incurs temporary
  allocation/repeated work; performance is not accepted yet.
* `SplitBrushList`, `BuildTree_r`, `SubtractBrush`: consume the same operation.
  Existing contents precedence, CSG ordering, actor expansion, bevel selection
  policy and ownership transport remain in their established locations.
* `LeafNode`: sufficient coverage guard requires each contributing fragment to
  contain the node region, through matching supports or vertex inequalities.
  Missing volume or unproved coverage raises `UNCERTIFIED_OCCUPANCY`; it does not
  assign blanket EMPTY. This is deliberately incomplete for general union coverage
  and does not yet implement a fallback partition search.
* `BaseWindingForNode`, `MakeNodePortal`, `SplitNodePortals`: remove geometric
  clipping dead bands, use the shared area/rank predicate, and retain the **clipped
  remainder** when only one side survives. `CheckPortalRegion`, called before
  portal publication, checks both incident nodes' ancestor halfspaces.

Source `brush.cc`, including P1, is byte-unchanged. Public `SupportedSplit` in
`brushbsp.hh` also provides direct validation of the real implementation rather
than a separate test algorithm. No acceptance runner or original oracle changed.

## 3. Checkpoint results

| Checkpoint | Status | Evidence and remaining requirement |
| --- | --- | --- |
| A — classification/routing | **Partial; not complete** | Exact local hull-2 fragment retained; full P1 reduced actor compile fails and Halloween PRECISE path is not reached. |
| B — supported splitting | **Partial; not complete** | Long narrow cut realized against all 29 ancestors; original thin source samples pass. First-cap, sky-gap, orientation/CSG matrix and general conditioning remain uncertified. |
| C — terminal occupancy | **Blocked** | Guard implemented; original fixture source samples pass. Both full maps abort before the three false-solid witnesses can be validated. |
| D — portals/filling | **Fail / incomplete** | Unclipped-winding fallback removed and containment guards added, but an ordinary sealed-room regression aborts on unresolved portal rank. No Halloween connectivity acceptance. |

[Final focused XML](thin_brush_phase5_evidence/final-rank-focused.xml): **4/5 pass**:
`phase5.Hull2ResolvedFrontFragment`, `phase5.NarrowQuadrilateralRankAndRealization`,
upstream duplicate-plane and empty-brush tests pass. Upstream
`testmapsQ1.simpleSealed` fails while compiling its rotated fixture, with
`PHASE5 NUMERICAL_UNCERTAINTY: portal area/rank unresolved`.
This is a new candidate usability regression, not dismissed as an unrelated test.

### A: actual front fragment

The direct test uses the exact preserved pre-partition bounds and split
X=-1280.000244141. Broad phase returns BOTH. Actual splitting produces a front
width **0.00024414099993919081**, containing
(-1280.0001220705,-1440,236.73692674130805); the back child excludes that point.
Both children retain MAP source identity and the original brush pointer. The
parent remains unchanged. Parent volume and sum of child volumes both equal
**1155678.882245101** in the tested double representation.

This demonstrates local retention and exclusive interior routing, not that the
full-map final hull-2 witness has become SOLID. The independent analytic source
box remains SOLID at margin 48; full-map output is unavailable for this candidate.

### B: narrow cut and conservation

The test loads the preserved terminal node windings and support coefficients,
then includes all 29 true ancestor constraints. An ancestor already present as
the same exact oriented support is represented once, without approximate merging.
The historical edge-count predicate rejects the supplied quadrilateral; the new
rank predicate accepts it. Actual cap area is **0.0074346256473068455**, against
independent **0.007434625516377664** (difference about 1.31e-10).

Original stored-parent volume is **26436.66707115664**; realized child sum is
**26436.667070281077**, difference about -8.76e-7. The explicit test tolerance is
1e-4 volume units and 1e-7 area units; these are comparison checks, **not**
certification tolerances used to decide whether a region exists. Residual checks
also execute. This does not prove complete face incidence, closure or union
conservation for arbitrary parents. Before adapting the test's duplicate ancestor
records, it counted identical faces twice and failed volume conservation; that
failure is preserved rather than hidden. The fixture now models the same original
ancestor as one support, as the real tree does.

### C/D: original source and early stops

[Final compiles](thin_brush_phase5_evidence/candidate-compiles.json) preserve
commands, hashes, return codes and failed logs. All use unchanged input copies,
`-bsp2 -notex -nopercent -chopfragment -threads 1`.

* Original thin fixture compiles. [Independent source checks](thin_brush_phase5_evidence/original-source-occupancy.json)
  pass **18/18** point/actor occupancy comparisons, including the original five
  positions and a clear actor control. This is focused evidence, not the 42-case matrix.
* P1 reduced fixture aborts in hull 1, MAP opening brace line **4**, partition
  **272**, with two represented vertex extents but no resolved rank-2 cut.
* Both Halloween inputs abort in initial hull 0 at MAP opening brace line
  **6336**, partition **2768**, X=208.000061035, with the same diagnostic.
  No candidate Halloween BSP is emitted; no false-solid/false-empty witness is
  claimed corrected by an aborted compile.
* The ordinary sealed-room test fails on portal rank as described above. No
  reduction in aggregate portal violations or successful flood is claimed.

The [preserved-witness replay](thin_brush_phase5_evidence/preserved-witness-replay.json)
checks fixture/evidence hashes and independently replays the three source-empty
margins for **each** frozen MAP, plus the hull-2 analytic source box. Its PASS
means the historical counterexamples remain reproducible, not candidate PASS.
The Phase 3 genuine source opening and midpoint route remain unchanged source
facts. This candidate has not validated their BSP/portal realization.

## 4. Precise numerical and architectural blockers

The code resolves arithmetic signs for **represented rounded vertices**, but
those are not automatically certified extrema of the underlying halfspace
intersection. Both full maps encounter a stored maximum X=208.00006103500016,
only about **1.71e-13** beyond partition 2768. Their negative extent is about
-91.999969482. The P1 reduced cut's positive represented extent is about
**7.62e-12**, versus negative extent about -41.1462. Arithmetic uncertainty of
one dot product alone does not enclose accumulated vertex-construction error.
The subsequent supported cap cannot establish a rank-2 cut, so the candidate
stops. Complete source-identifiable planes and windings are in the failed logs.

The safe next implementation needs an adaptive **halfspace extent decision**
with construction error/conditioning, or a stronger support-intersection result
that can distinguish true separation, exact/lower-dimensional contact and
unresolved numerical intersection. It must feed both classification and
realization. Merely applying the backward-residual allowance to side signs would
be another unproved geometry deletion policy and was not done.

Additional incomplete obligations:

* A winding satisfying backward residuals is not yet a complete convex boundary
  certificate. Face incidence/closure, convexity, construction error and complete
  support-to-boundary consistency are not proven. Broad-phase bounds must also
  be certified to enclose the authoritative region, not merely stored windings.
* Rank uncertainty in ordinary portals needs a reliable lower-dimensional/contact
  decision; blanket removal or blanket retention would both be unsafe.
* Retaining all support records separates constraints from active boundary
  polygons, but these still share `side_t`. General inactive/redundant-support
  realization and duplicate-boundary accounting require a defined invariant.
* Terminal coverage currently uses a sufficient per-fragment condition; union
  coverage, fallback partitioning and proof that stored region vertices suffice
  remain incomplete. The guard alone is not certified terminal occupancy.
* CSG now shares splitting and has no mostly-side/tiny discard in that operation,
  but complete subtraction conservation and all outer routing decisions have not
  been certified. Source-plane equivalence discarded before this operation is
  not recovered. Near-coincident source planes remain a representation boundary.
* Serialized float32 plane effects, native collision, BSP traversal, format limits
  and engine/VIS/LIGHT compatibility have not been accepted for this candidate.

Long double is finite precision and platform-dependent (host x86 extended
precision here). Its use is a local stronger predicate, not arbitrary precision.
The candidate has explicit numerical diagnostics, not a proof that every
mathematical positive-volume region is representable. Valid narrow cuts must
survive; unresolved cuts must not be silently routed or classified as invalid.

## 5. Cost and output measurements

| Final invocation | Exit | Wall time (time -v) | Peak RSS KiB | BSP bytes |
| --- | ---: | ---: | ---: | ---: |
| Thin original | 0 | <0.01 s (compiler: 0.002 s) | 7,164 | 1,512 |
| P1 reduced | 1 | 0.01 s | 7,760 | none |
| Halloween off | 1 | 0.31 s | 41,800 | none |
| Halloween on | 1 | 0.35 s | 44,384 | none |

Failed runs are **early-abort costs**, not performance improvements over P1.
Original emitted output: 6 nodes, 7 leaves, 2 faces, 12 clipnodes, 17 planes.
Its BSP lump bytes in standard order are
`[30,340,12,48,0,264,40,56,0,144,308,8,40,32,64]`.
The log still reports four degenerated render faces during TJunc: source
occupancy checks do not establish preservation of the complete render boundary.
The original hull-0 tree has 36 tree portals (reported for each portalization)
and 12 VIS portals. It passes the new incident-region residual guard; that is
not an independent source-connectivity certification. The single source brush
has six input sides; comprehensive fragment counts are unavailable for failed
full-map processing. No full-map node/leaf/face/clipnode/lump counts, complete
portal counts, FAST/PRECISE comparison or native-engine measurement exist for
this candidate. No historical size target was imposed.

## 6. Validation stopping point and recommendation

The full vertical slice fails before the known Halloween witness paths. Therefore
the unchanged **42-compilation matrix, RollerSpline, historical actor fixtures,
full upstream suite, representative full ordinary maps, native QrustyQuake,
VIS/LIGHT compatibility, repeated-build determinism and engine-limit checks were
not reached**. Their historical receipts are controls, not current PASSes.
No gate, witness, source margin, matrix case or accepted baseline was relaxed.
Initial failed reconstruction tests, test-setup crash, build diagnostics and
later passing/failing evidence are retained and labelled in the evidence README.

**Recommendation: revise.** This is useful implementation work with two actual
local geometric improvements, but it does not satisfy Phase 5 completion criteria.
The three Halloween false solids, hull-2 final false empty, real source opening,
complete fragment conservation and portal connectivity remain unvalidated for
this candidate. Do not promote or deploy it. Resolving the extent-certificate
boundary is the next dependency, before more full regression expenditure.

No compiler correction was applied to the active checkout. Only this report and
inert evidence are added. No commit, push, production promotion, installation,
deployment, P2 application, authored MAP/.qart edit, Qartographer/Qrucible change,
VIS/LIGHT change or stock utility replacement occurred. Installed QQBSP remains
SHA-256 `49d766579a03701d6a5bb3560112bc756afdb8cf4488242e0b8db72668d8c8c0`.
