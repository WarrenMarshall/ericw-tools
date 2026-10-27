# Thin-brush correctness, Phase 2 — findings; no accepted P3

2026-10-26. **Production unchanged. P1 preserved; P2 unapplied.**

The remaining failures have several concrete mechanisms, not one Z-axis defect.
A diagnostic that made split extent, cut-winding clipping and tiny-edge policy
consistent passed the original 21-geometry / 42-compile matrix, including every
original actor witness. It failed the broader Halloween gate and produced a
leaking, much larger full-map BSP. It is rejected, not an accepted correction.
No native, stripped-artifact, release, deployment or deterministic-output PASS
is claimed. No push or compiler-algorithm commit was made.

## Geometric contract

The [pre-experiment contract](thin_brush_phase2_evidence/contract.md) distinguishes:

- A valid solid: bounded oriented source halfspaces with a reliably resolved,
  positive-volume interior and consistent full-dimensional boundary geometry.
- Degeneracy: inconsistent/unbounded halfspaces, collapsed dimensionality or
  zero volume. Mathematical nonzero volume does not itself certify numerical
  representability.
- Numerical slivers: derived fragments requiring evidence from their supports,
  conditioning, winding geometry and parent relationship. Thickness alone cannot
  establish that a fragment is arithmetic noise.
- Legitimate thinness: a resolved source-supported solid or derived fragment
  below a historical heuristic length. It must retain its occupancy boundaries.

The node volume must equal the root region intersected with ancestor halfspaces.
Fragments must represent the original source intersected with that region and
any CSG subtraction. A selected partition must create the same two reliable
regions that admission certified. Splitting must conserve occupancy; subtraction
must conserve A-minus-B and ultimately the source union. A terminal leaf may
combine brush contents only when occupancy is constant throughout its region.
Exhausting heuristic candidate selection is not evidence of constant occupancy.

No accepted correction to those invariants was implemented. The tested uniform
threshold change does not distinguish source support from numerical artifacts.
It is a causal experiment, explicitly insufficient as the requested design.

## First incorrect stages

Traces use the preserved rejected node-volume-only prototype, with diagnostic
logging in a disposable source snapshot, one compiler thread and unchanged MAPs.
[Instrumentation](thin_brush_phase2_evidence/instrument.py),
[commands](thin_brush_phase2_evidence/run-traces.py),
[complete traces](thin_brush_phase2_evidence/traces/).
The logging lambda prints its own `operator()` name; `EXTENT check` identifies
CheckSplitBrush and `EXTENT real volume=0/1` distinguishes fragments/node volumes.

| Category | First established incorrect decision |
| --- | --- |
| Original Z-thin under P1 | Previously preserved CheckSplitBrush 0.1-unit side-admission rejection; no new attribution replaces that trace. |
| Y-thin (`axis-0`) under prototype | CheckSplitBrush builds a cut polygon for Z=-32 or +32. After selecting both Y supports, clipping against the second Y support changes four points to zero under default `clip_back` epsilon 0.1. Remaining source sides still have four-point windings, but admission rejects both Z boundaries. |
| X-thin (`axis-1`) under prototype | Same clipping failure after both X supports are selected; the four remaining Y/Z candidate cut polygons disappear. |
| Rotated under prototype | Thin-plane pair is selected first. Subsequent four side candidates lose their cut polygons against the second thin support (four/five points to zero). The thin separation is approximately 0.00800000000012, not an unresolved sign. |
| Overlap, hull 0 | First, CheckSplitBrush deletes lateral cut polygons after the outer thin supports are chosen (level 6). Independently, actual SplitBrushList fragment splitting loses solid occupancy, not CSG subtraction in this flag configuration: selected Z=0.004 sees front=0.002, back=-0.006. SplitBrush's 0.1 shortcut returns the entire fragment to the back, losing the valid upper slice. Another selected support sees front=0.006, back=-0.002. Synthetic cut clipping continues rejecting the remaining side candidates. |
| Overlap, actor hulls | Actual SubtractBrush/ChopBrushes loses a 0.002-thick outside portion at an expanded lower support. SplitBrush returns no front piece and subtraction drops that part of the union. |
| Near-coplanar pair, actor hulls | Actual SubtractBrush loses a 0.0082-thick outside portion: hull 1 trace front=0.0082/back=-55.9998; hull 2 front=0.0082/back=-87.9998. This is a compiler CSG defect, not just boundary uncertainty. |
| Adjacent | No remaining failure under the prototype or diagnostic. No invented bad stage is assigned to a passing case. |

`-chopfragment` permits fragmentation when chopping is enabled; it does **not**
turn on hull-0 ChopBrushes. In both requested flag modes, hull 0 here goes directly
to BSP processing. Actor hulls always chop. The traces cover actual actor CSG,
not a synthetic-volume approximation to it.

Orientation dependence comes from plane ordering interacting with cut-polygon
clipping. The Z-thin box happens to choose its two thin supports last, leaving
no lateral candidates to build inside the thin region. X/Y/rotated boxes do not.
The observed failure is not an axial distance-calculation special case. Both
SelectSplitPlane and ChooseMidPlaneFromList use the same faulty volume predicate;
the reduced traces exercise precise selection, not a claimed execution of FAST
midplane selection.

The default `clip_back` epsilon is 0.1. The rejected prototype changed side/edge
checks but not that default. It therefore never reaches its lowered tiny-edge
predicate for these null polygons. Separately, WindingIsTiny counts at least
three edges longer than its threshold: a valid 64-by-0.008 rectangle has only
two edges longer than 0.02 and would fail that policy even with accurate clipping.
That last observation follows directly from the predicate; it is not misreported
as a separate traced rejection in a polygon that was already null.

BuildTree_r then receives no candidate and LeafNode combines the residual SOLID
brush into a region still containing exterior space. Child node volumes in the
traced prototype were created, but the next admission loses their remaining
boundaries. The violation precedes BSP serialization.

## Actor-boundary classification

Original witnesses, expected contents and source margins are unchanged in
[actor-witnesses.json](thin_brush_phase2_evidence/actor-witnesses.json).
For example hull 1 oracle point `(0,32,-28.00385)` corresponds to engine point
`(0,32,-32.00385)` after the established offset. Hull 2 oracle point
`(0,32,-44.00385)` corresponds to `(0,32,-64.00385)`.
Both are source-solid, approximately 0.00015 inside the lower expanded boundary.

Additional samples at depths 0.001 and 0.004 retain the exact source halfspace
oracle. The near-coplanar prototype is incorrectly EMPTY at both depths in both
actor hulls; the diagnostic is SOLID. The overlap prototype is incorrectly EMPTY
at depth 0.001. Together with the actual subtraction trace, this rules out merely
float-output ambiguity or an incorrect actor-offset model as the explanation.
No boundary exclusion or tolerance was increased, and no original witness was
removed. Arbitrary points close to other boundaries remain a numerical question;
this evidence only classifies the reported cases.

## Diagnostic and complete matrix

The inert [REJECTED patch](thin_brush_phase2_evidence/uniform-epsilon-REJECTED.patch)
uses the existing DIST_EPSILON (0.0001) for side admission, midwinding clip_back,
and tiny-edge tests in both CheckSplitBrush and SplitBrush, including source
fragments/CSG. It retains the prototype's now-unused node-volume flag to preserve
exact experimental source identity; this is not proposed production code.
No source coordinates, hull sizes, P1 logic, formats, or oracle tolerances changed.

[All before/after hull counts](thin_brush_phase2_evidence/matrix-comparison.json),
[complete diagnostic results](thin_brush_phase2_evidence/uniform-epsilon-matrix.json).
Each table entry applies independently to default and -chopfragment and gives
raw mismatch counts as hull 0 / 1 / 2. Repeated equivalent support normals retain
repeated checks. Thus every one of the 42 compiles is represented.

| Geometry | P1 | Rejected node-only prototype | Uniform diagnostic |
| --- | --- | --- | --- |
| original | 111 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| control | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-0.0005 | 111 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-0.002 | 111 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-0.008 | 111 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-0.015625 | 111 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-0.02 | 111 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-0.05 | 111 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-0.099 | 109 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-0.1 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-0.101 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-0.25 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-1 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| thickness-16 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| axis-0 | 110 / 0 / 0 | 20 / 0 / 0 | 0 / 0 / 0 |
| axis-1 | 108 / 0 / 0 | 40 / 0 / 0 | 0 / 0 / 0 |
| translated | 111 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| rotated | 75 / 0 / 0 | 12 / 0 / 0 | 0 / 0 / 0 |
| adjacent | 124 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| overlap | 130 / 20 / 20 | 10 / 20 / 20 | 0 / 0 / 0 |
| near-coplanar | 240 / 10 / 10 | 0 / 10 / 10 | 0 / 0 / 0 |

The permanent `thin_brush_probe.py` ran unchanged, exited 0 for the diagnostic,
and produced all 42 results. That PASS applies only to its matrix, not release.

A supplemental 0.000075-unit source box was also examined to delimit numerical
claims. ParseBrush's approximate opposite-plane comparison identifies its two
supports as duplicates (DIST_EPSILON=0.0001), before BSP splitting. It produces
out-of-range brush warnings and an empty BSP with zero plane/clipnode lumps and
zero headnodes. The existing unguarded research BSP reader loops on that malformed
empty result, so the supplemental run was interrupted (130); it is **INCOMPLETE**,
not an additional matrix PASS or a certified split-admission counterexample.
The [input/log/raw output](thin_brush_phase2_evidence/below-plane-equivalence/)
are preserved. This is evidence of an existing representation/admission limit;
it does not authorize an arbitrary minimum thickness or changes to the original
oracle. The original 0.0005 minimum sweep case remains a resolved, passing case
under the diagnostic.

## Broader regression and compatibility gate

- All 13 selected unchanged upstream QBSP tests passed.
- P1 original reduced regression: pristine 104 failures; diagnostic 0.
- Frozen RollerSpline, both modes: diagnostic hulls 0/1/2 all 0 failures.
  Pristine retains the expected player/large negative controls 82/35 default
  and 84/42 chopfragment. P1's source change is byte-unchanged.
- All four historical thin-cell/opening fixtures pass.
- Halloween actor supports/clearance pass the established checks, but the gate
  exits 1 on **three hull-0 differences between full-off and full-on**. No receipt
  is promoted. Logs and failures are preserved under
  [broader evidence](thin_brush_phase2_evidence/broader/).

The existing Halloween hull-0 equality check is a compatibility gate, not an
independent source oracle. Investigation of its three differences uses direct
MAP halfspaces, excluding CLIP; the source is EMPTY at margins approximately
0.130905, 0.846961 and 0.261203. All render brushes are included conservatively,
so none can supply SOLID occupancy at these exterior points. The separate
preserved source-face geometry agrees. Diagnostic full-on is correctly EMPTY;
full-off is incorrectly SOLID. Thus the failure must **not** be described as
three newly lost source-solid samples. It demonstrates unresolved full-map
correctness/order dependence and a failed established gate.
[MAP analysis](thin_brush_phase2_evidence/map-witnesses.json),
[source-face analysis](thin_brush_phase2_evidence/full-witnesses.json).

Additionally, both diagnostic full maps report an outside leak; full-on reaches
occupant `light` at `(-1408,-2080,208)`. Pristine full-on does not report this leak.
The diagnostic therefore changes filling and greatly increases emitted geometry.
Whether that leak exposes a real source opening or an additional clipping/portal
inconsistency was not certified. Existing portal clipping/tiny policies remain
unchanged; lowering brush split tolerances does not prove their consistency.
These unresolved facts block acceptance rather than justify more blanket changes.

No native player/large-actor, native hull-0 point/projectile, stock VIS/LIGHT,
stripped release, two-artifact comparison or installed-behavior validation was
run for the rejected diagnostic. The existing native player fixture does not
certify native hull 2. Historical P1 acceptance is not new candidate acceptance.
Both-mode full-map release and determinism gates remain uncompleted.

## Performance and output comparison

Single sequential observations, not a statistical performance certification:

| Full-on | Pristine alpha10, this run | Accepted P1, historical bootstrap | Uniform diagnostic |
| --- | ---: | ---: | ---: |
| QBSP elapsed | 13.120 s | 13.215 s | 14.780 s |
| BSP bytes | 2,993,988 | not freshly measured | 7,133,828 |
| Clipnodes | 27,275 | 26,296 | 29,635 |
| Faces | 16,424 | 16,424 | 42,664 |
| Hull-0 nodes | 13,364 | not freshly measured | 42,458 |

Full-off elapsed: pristine 12.125 s; diagnostic 13.153 s. Diagnostic full-on is
about 12.7% slower than this pristine run, 138% larger in bytes and has 12.7% more
clipnodes than historical accepted P1. The no-fill leak explains a major source
of extra emitted world geometry; the residual clipnode/performance changes have
not been certified acceptable. Exact artifact hashes and per-case sizes are in
[output-comparison.json](thin_brush_phase2_evidence/output-comparison.json).
No second clean build or normalized repeat-output comparison was performed;
there is no deterministic-output claim.

## Proposed direction and disposition

The demonstrated mechanisms share an invariant violation—heuristics deleting
resolved occupancy—but occur at three different operations: admission extent,
cut-polygon construction, and actual fragment splitting/CSG. Fixing only one
cannot establish correctness. The experiments do not establish that a new kernel
is necessary, or that simply substituting DIST_EPSILON is safe.

A future correction should share a certified split decision between admission
and realization, preserve source/ancestor support identities, validate winding
dimensionality and resolved child halfspaces, and verify fragment/CSG occupancy
conservation. Uncertain results need explicit handling rather than mostly-side
assignment or a SOLID terminal region. How to distinguish safe source-supported
thin fragments from numerical artifacts, while preserving full-map filling and
reasonable output, remains unresolved. This is a direction, **not** a validated
proposed implementation.

No P3 accepted/committed, no compiler provenance/banner change, no deployment,
no baseline promotion, no GitHub push. Stock utilities, authored maps, VIS/LIGHT,
Qartographer production code and Qrucible were untouched. Research files only
are added to this repository; original Phase 1 evidence/probe remain unchanged.
Installed QQBSP SHA-256 remains
`49d766579a03701d6a5bb3560112bc756afdb8cf4488242e0b8db72668d8c8c0`.
[Artifact identities](thin_brush_phase2_evidence/identities.json),
[evidence hashes](thin_brush_phase2_evidence/manifest.json).

Disposable artifacts are under `/tmp/qqbsp-phase2`; the diagnostic executable is
`uniform-epsilon-qqbsp`. The previously preserved `/tmp/qqbsp-p3` source and main
prototype executable were restored to their rejected-prototype bytes after the
experiment. Binary hashes, not their unchanged experimental P1 banner, identify
these modified research builds. No accepted correction or release exists.
