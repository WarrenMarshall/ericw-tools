# Thin-brush Phase 3 — Halloween growth, source leak, and partition invariants

2026-10-26. **Findings only. P1 preserved; P2 unapplied; diagnostic rejected.**

The Halloween hull-0 leak exposes a real, approximately **0.00012207-unit source
opening** between a sky wall and a roof support. P1's first tree falsely extends
SKY through that opening because node-volume admission rejects its missing
boundary. The diagnostic admits the boundary and exposes the opening. The leak
is not evidence that legitimate thin geometry must be discarded.

Most output growth is a consequence of the resulting no-fill/no-rebuild path.
A hull-0-only control attributes 3,854,040 of the 4,110,580 additional bytes to
that path, with 256,540 bytes remaining when comparing unfilled outputs. This
is a controlled subtraction, not an assertion that every remaining fragment is
correct. The diagnostic still creates three source-false SOLID witnesses in
full-off and retains inconsistent portal clipping. It is not a safe correction.

## Scope, provenance, and reproducibility

Read AGENTS.md, README.md, baseline.json, THIN_BRUSH.md, THIN_BRUSH_PHASE2.md,
BOOTSTRAP.md, NATIVE_ENGINE.md and the preserved Phase 1/2 traces, patches,
oracles, fixture identities and receipts. Work stayed in `/tmp/qqbsp-phase3`.
Only this report and research evidence were added to the repository.

Production checkout HEAD: `4b505ae25e508a8910b031e94d6f1ea60ac06a95`.
Pinned pristine upstream: `ccaeb8457a1267860ebe99ed1df7394ebdd6b435`.
The P1 control is the existing symbol-rich baseline build from downstream
`a39a599d08967998d01e85d10ac356f823e27a35`; its manifest records no tracked changes.
The uniform diagnostic is the exact preserved rejected Phase 2 executable,
not a newly reconstructed substitute. Its P1 banner does not identify its
experimental algorithm; hashes do.

| Executable | SHA-256 |
| --- | --- |
| Pristine alpha10 | `b80a35bc57eee9906c259abf2aa30a475c6a3f0864b6e4f9c16f233f9658d880` |
| P1 development control | `a097cb6a6288b930eb018797464ef6a2a7e64d173fd113bdd1659167a1be30ff` |
| Uniform diagnostic | `830d77aad4512515e3ac0ef608f4c43dca0406a952dbe60c6da68e91af7d84d5` |

Frozen MAP hashes:

- full-on: `16250e50546f9d1c4654d75e0a6683f70f7eff332ec730793c5f836d39716318`.
- full-off: `d5f2ab2a0c5a22d2f0ecaecf77a1bbd72a3c2ce2e3c444fe0b4c517092e5986c`.

Every comparison uses unchanged copies and `-bsp2 -notex -nopercent
-chopfragment -threads 1`. Controls add `-nofill`; targeted hull-0 traces add
`-noclip`; the full-off instrumentation adds `-loghulls`. These exceptions are
labelled and are not substituted for the matched full compilations. No authored
MAP, decimal coordinate, actor extent or oracle exclusion tolerance changed.

[Reproduction receipts](thin_brush_phase3_evidence/reproduction.json) record
commands, input/binary/output hashes, all lump sizes, elapsed time, peak RSS,
counts and leak warnings. Logs and `/usr/bin/time -v` receipts are retained.
Times are sequential single-threaded observations; some diagnostic build/read
work overlapped them. They are not controlled performance or determinism
certification, and should not be compared directly with Phase 2's multithreaded
13–15 second observations. No two-clean-build reproducibility claim is made.

## Matched full-map reproduction

Counts are all emitted models combined. Hull-1/2 clipnode counts are independently
traversed reachable records; no sharing or unreachable clipnodes were found.
RSS is KiB. Time is wall seconds measured by the runner.

| Input / compiler | BSP bytes | Nodes | Leaves | Faces | Models | Clip H1 / H2 | Time | Peak RSS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| on / pristine | 2,993,988 | 13,364 | 7,631 | 16,424 | 94 | 14,785 / 12,490 | 45.25 | 1,348,716 |
| on / P1 | 2,976,400 | 13,364 | 7,631 | 16,424 | 94 | 14,186 / 12,110 | 46.89 | 1,374,956 |
| on / uniform | 7,133,828 | 42,458 | 23,298 | 42,664 | 94 | 16,012 / 13,623 | 53.95 | 1,512,268 |
| off / pristine | 2,915,532 | 12,653 | 6,475 | 16,377 | 93 | 15,429 / 12,610 | 44.37 | 1,335,264 |
| off / P1 | 2,879,012 | 12,653 | 6,475 | 16,377 | 93 | 14,114 / 11,930 | 47.85 | 1,357,284 |
| off / uniform | 6,996,688 | 40,067 | 21,014 | 40,609 | 93 | 14,686 / 32,435 | 48.24 | 1,467,080 |

The two smoothing inputs are different geometry: 2,254 versus 2,397 world hull-0
brushes, and 94 versus 93 emitted models. They are never used as interchangeable
controls. Both pristine and P1 fill hull 0 successfully. Uniform full-on leaks to
`light (-1408,-2080,208)`; uniform full-off's hull-0 occupant is
`ambient_swamp1 (-1408,-1810,194)`.

Full-off instrumented actor logs establish an additional distinction: uniform
hull 1 fills in both passes; hull 2 fills its FAST tree, rebuilds PRECISE, then
leaks to `light (-1232,-1520,232)`. Do not interpret the hull-0 leak as disabling
all actor filling. This pass-dependent hull-2 result is an unresolved occupancy /
portal consistency risk, not a certified second source opening.

## First meaningful divergence: actual split cap, before partition choice

Instrumentation runs inside the existing compiler, with one worker. It records
source/CSG spatial fingerprints, selected planes indexed by ancestor branch
path, targeted winding geometry and candidate extents. Paths use 0=front and
1=back. Addresses and allocation order do not participate in the fingerprints.
The source snapshot and instrumentation patches are preserved with the evidence.

For full-on hull 0:

1. Source construction is identical: 2,254 brushes, 13,317 sides, spatial
   fingerprint `8768995481860569871` in both builds.
2. Hull-0 CSG subtraction is not enabled by `-chopfragment`. Both post-CSG
   snapshots are unchanged. CSG cannot explain this first hull-0 divergence.
3. Both select root plane 2040, `Z=220`, from the brush beginning at MAP line
   4075. Root source windings are identical, checked side by side.
4. **Actual `SplitBrush` realization first differs at the generated cap for
   source brush whose first face is line 9169** (opening brace line 9168).
   Exactly one cap side differs in each child; brush counts and side identities
   remain the same. P1's cap uses X approximately 1116.0007–1116.0017 where the
   source intersection reaches X approximately 1116.0849.
5. An independent zero-epsilon polygon/halfspace intersection at Z=220 gives
   cap area 825.564594. Uniform agrees to about 2.5e-11 in vertex distance;
   P1 gives 819.457619 and misses up to 0.084197 units at the edge. The missing
   cap strip is source-supported, not a new numerical sliver introduced by
   uniform. P1's cap no longer completes the same boundary as its clipped sides.

This is a meaningful winding-geometry divergence at the very first partition,
not yet proof of a changed occupied halfspace set. The source-supported plane
sets remain identical at this event; a different vertex fingerprint alone is
not misreported as a changed solid region. The changed midwinding clipping
policy is responsible, rather than parsing, CSG or serialization.

[Root differences](thin_brush_phase3_evidence/root-diff.json),
[independent cap intersection](thin_brush_phase3_evidence/cap-oracle.json).

The first **different selected partition**, breadth-first over matching ancestor
partitions, is path `0101010`, depth 7. Input brush fingerprint is identical
(`16281214196375266472`, one brush, first face line 797). P1 chooses plane 396;
uniform chooses plane 404. For candidate 404 the node-volume extents are:

```
front = 1891.0093218925897
back  = -0.00020516824389460453
P1 admission = false; uniform admission = true
```

That is a thin ancestor-generated node-region slice bounded by an existing
source support. It is not evidence of a newly authored 0.000205-unit brush.
The partition data establish additional resolved subdivisions, not a blanket
classification of all later subdivisions as legitimate or erroneous.
[First partition divergences](thin_brush_phase3_evidence/first-partitions.json),
[targeted decisions](thin_brush_phase3_evidence/targeted-decisions.log).

Actor hulls diverge earlier in their own pipelines, at actual CSG subtraction:

| Input / hull | Constructed, both | Post-CSG P1 | Post-CSG uniform |
| --- | ---: | ---: | ---: |
| on / 0 | 2,254 | 2,254 | 2,254 |
| on / 1 | 2,306 | 7,793 | 8,405 |
| on / 2 | 2,306 | 7,789 | 8,396 |
| off / 0 | 2,397 | 2,397 | 2,397 |
| off / 1 | 2,306 | 7,846 | 8,214 |
| off / 2 | 2,306 | 7,836 | 8,223 |

Source fingerprints match separately for each input/hull; post-CSG fingerprints
change. The counts demonstrate changed retention, but do not certify each extra
actor fragment. Phase 2's traced overlap/near-coplanar subtraction defects remain
applicable. No claim that all extra CSG fragments are noise or necessary is made.
[On fingerprints](thin_brush_phase3_evidence/stage-fingerprints.json),
[off fingerprints](thin_brush_phase3_evidence/stage-fingerprints-off.json).

## Independent leak reconstruction and the false sealing boundary

The diagnostic full-on `.pts` has 17 distinct route points and 16 leak portals.
The route goes from the reported light through the roof region near
`(-1728,-1582,510)`, then outside below the map. Source sky brush first face
14278 has its right boundary at **X=-1728**. Roof brush first face 1867 has its
left boundary at **X=-1727.99987793**. Their source separation is
**0.00012207000008857**; the MAPs retain the same local opening in both modes.

The original route touches the roof support but has no positive-interior
intersection with source render brushes. A more useful independent witness
moves the two waypoints at X=-1727.99987793 to the gap midpoint
X=-1727.999938965 and extends the last point vertically to Z=-10000. Analytic double-precision
segment/convex-halfspace interval clipping finds **no solid intersection** on
any segment. Minimizing each brush's maximum signed plane distance along every
segment gives minimum source margin **0.0000610349998244**. This is a plane
margin, not a claimed Euclidean clearance radius. It is smaller than
DIST_EPSILON; these resolved decimal halfspaces do not establish a general
arbitrary-precision guarantee. No authored geometry was modified.

The oracle conservatively includes all non-CLIP/non-HINT brush halfspaces,
including detail, liquids and stationary brush-model geometry; additional
nonblocking geometry can only make this empty-route check harder. It does not
use BSP planes or compiled contents to establish source emptiness.

A parser error was caught during research: scanning every brace mishandled
texture-name braces and omitted later brushes. The initial half-unit detour
claim was withdrawn. The preserved final oracle recognizes standalone structural
brace lines, includes the sky wall, rejects the half-unit detour through that
wall, and certifies only the midpoint route above. Original Phase 1/2 oracles
and evidence were not rewritten.

P1's first tree routes the midpoint into leaf `01110101000111110`. Its sole
residual brush is the sky brush at first face 14278. At precisely that leaf:

```
candidate plane 4578: X=-1728
node-volume front = 0.00012207000008856994; back = -32
P1 CheckSplitBrush = false
uniform CheckSplitBrush = true
```

P1 exhausts candidates and `LeafNode` combines that residual SKY into the whole
region, including the source-empty gap. This seals its initial flood. Uniform
admits the sky boundary and exposes the real connection. Independent serialized
samples show P1-no-fill SKY (-6) and uniform EMPTY (-1) at the gap midpoint.
P1's final filled/rebuilt output differs again; do not infer the first fill's
seal from the final BSP alone. Nearby source-empty outside samples become
SOLID in the successfully filled P1 output but remain EMPTY under uniform.

**Leak classification: (1) genuine source opening newly exposed**, with a
separately demonstrated P1 false-SKY sealing region. No missing source blocker,
lost thin source brush, or diagnostic-created hole is required to explain it.
This is a point-space opening; it proves neither actor passage nor a useful
gameplay route. No native gameplay acceptance is claimed.

[Source route and interval results](thin_brush_phase3_evidence/leak-oracle.json),
[midpoint route including outside extension](thin_brush_phase3_evidence/leak-detour.json),
[BSP samples](thin_brush_phase3_evidence/leak-bsp.json),
[sky ancestors](thin_brush_phase3_evidence/sky-ancestors.json).

### Portal consistency remains a separate defect boundary

Uniform did not make portal clipping consistent with its new partition policy.
For 15 of the 16 full-on leak portals, the maximum violation of either incident
leaf's ancestor halfspaces is at most 2.3e-13. Portal index 9 violates one by
**0.00012207000008857**. The flood therefore does traverse a winding that is not
strictly contained in its declared leaf regions. The independent source route
still establishes a real opening; this portal error cannot turn that opening
into evidence of a source-sealed map.

Aggregate initial-tree winding measurements:

| Input / build | Portals | Vertices | Minimum area | Area < .01 | Ancestor violation > .0001 | Maximum violation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| on / P1 | 213,943 | 849,086 | .0088073 | 1 | 4,733 | 83.56425 |
| on / uniform | 218,610 | 867,412 | .0035555 | 3 | 11,456 | 83.56425 |
| off / P1 | 213,112 | 844,898 | .0088073 | 1 | 5,963 | 267.77009 |
| off / uniform | 218,129 | 864,695 | .0035555 | 3 | 12,938 | 765.93250 |

These are containment diagnostics, not counts of proven wrong graph edges.
Large errors already occur in P1. One-sided portal clipping retains the original
winding when its other clipped side is absent/tiny; `MakeNodePortal` still uses
0.1, and portal splitting/tiny tests retain their separate historical policies.
The mechanism can produce windings extending outside leaf halfspaces. This
assignment does not attribute every counted error to a particular branch, or
certify all portal occupancy. Portal code must be in the correction's invariant
boundary; merely lowering brush tolerances leaves it unresolved.

## BSP growth: partitioning versus fill and retention

| World hull-0 stage | P1 on | Uniform on | P1 off | Uniform off |
| --- | ---: | ---: | ---: | ---: |
| First BSP nodes | 57,486 | 61,532 | 57,129 | 61,510 |
| First BSP leaves | 57,487 | 61,533 | 57,130 | 61,511 |
| Tiny portals discarded | 2,762 | 8,614 | 3,042 | 8,894 |
| First fill outside leaves changed | 7,119 | no fill | 6,702 | no fill |
| Rebuilt PRECISE nodes | 37,531 | skipped | 40,425 | skipped |
| Second fill outside leaves changed | 3,627 | skipped | 3,627 | skipped |
| Final emitted nodes, all models | 13,364 | 42,458 | 12,653 | 40,067 |

The first-tree growth is 4,046 nodes (7.04%) on and 4,381 (7.67%) off. It is
already present before portals/fill, but is much smaller than the final node
increase. With successful fill, `ProcessEntity` marks outside brush sides
invisible, rebuilds PRECISE, fills again and prunes. With a leak it skips that
rebuild/fill path, preserving far more exterior geometry. Serialization emits
that different tree; it is not where the growth first originates.

The decisive bounded control compiles full-on hull 0 with actor generation
suppressed, keeping the same input and all other flags:

| Hull-0-only control | Bytes | Nodes | Faces |
| --- | ---: | ---: | ---: |
| P1, normal fill | 2,530,428 | 13,364 | 16,424 |
| P1, `-nofill` | 6,384,468 | 40,040 | 41,723 |
| Uniform, normal invocation but leaks | 6,641,008 | 42,458 | 42,664 |

Thus the controlled fill-path difference is **3,854,040 bytes (93.76%)** of the
4,110,580 hull-0-only increase. The residual unfilled comparison is **256,540
bytes**, 2,418 nodes and 941 faces. This is a path-dependent decomposition;
retention and partition changes interact, so it is not a uniquely additive
per-fragment causal allocation. It nevertheless directly disproves attributing
the entire 4.1 MB increase to thin-fragment proliferation.

In the matched complete outputs, uniform minus P1 is 4,157,428 bytes. Lump
contributions are:

| Lump | Additional bytes |
| --- | ---: |
| Nodes | 1,280,136 |
| Faces | 734,720 |
| Leaves | 689,348 |
| Edges | 453,208 |
| Surfedges | 440,420 |
| Vertices | 329,724 |
| Marksurfaces | 116,584 |
| Clipnodes | 40,068 |
| Texinfo | 37,240 |
| Planes | 35,980 |

Entities, textures, models, visibility and lighting do not grow. The additional
complete-output cost beyond hull-0-only is 46,848 bytes: 40,068 clipnode bytes
and 6,780 additional plane bytes associated with actor processing.

The full P1 `-nofill` control produces 21,317,268 bytes on and 20,909,692 off,
with respectively 1,202,515 and 1,200,370 clipnodes. This disables actor fills
and rebuilds too; it is **not** a valid direct numerical allocation of the
hull-0 leak's cost. The hull-0-only control avoids that confound.
[Growth receipts](thin_brush_phase3_evidence/growth.json).

Demonstrated causes: extra source-supported cap area, additional narrow
ancestor-region partitions, changed actor CSG retention, and predominantly the
skipped hull-0 fill/rebuild path. Tiny-portal rejection increases substantially,
showing the changed trees encounter historical portal heuristics more often.
There is no measured exhaustive split-fragment volume distribution, duplicate
plane contribution or certified degenerate-winding count. Therefore the residual
256 KB cannot responsibly be divided among valid fragments, repeated slivers,
redundancy and degeneracy. No evidence establishes an unavoidable 7 MB minimum
for correct thin geometry; nor is a 3 MB output required for a truly leaking map.

## Three compatibility witnesses and the gate

Recomputed from standalone-brace MAP parsing, conservatively including render
brushes and excluding CLIP, with the original unchanged witness coordinates:

| Point | Source margin, either input | Expected hull 0 | Pristine / P1, on and off | Uniform on | Uniform off |
| --- | ---: | --- | --- | --- | --- |
| (-1388,-233,8.778914155553586) | .13090506484354592 | EMPTY | EMPTY | EMPTY | SOLID |
| (-1376,-257,-12.914510661888684) | .8469610158824707 | EMPTY | EMPTY | EMPTY | SOLID |
| (-1364,-269,11.605075569064333) | .2612034930921254 | EMPTY | EMPTY | EMPTY | SOLID |

[Fresh witness receipt](thin_brush_phase3_evidence/witness-gate.json).
The Phase 2 witness files and source margins remain unchanged.

A premise needs clarification: the preserved Phase 2 false-SOLID full-off BSP
is **the diagnostic full-off output**, not the accepted historical P1 control.
Fresh pristine and P1 full-off are EMPTY at all three. The diagnostic introduces
these false solids in its leaking hull-0 output, where outside fill did not
legitimately create them. Calling all three differences harmless compatibility
changes would conceal an actual regression.

The current production gate remains byte-unchanged. Its equality assertion is
still too broad as a general invariant: different smoothing geometry can have
different source collision. Proposed replacement, for a separate reviewed phase:

1. Derive expectations independently for each frozen input, contents class and
   hull. Keep every original witness and its unmodified margin. Assert both
   source-SOLID retention and source-clear EMPTY where fill semantics permit it.
2. Keep equality only for source-certified unchanged occupied/clear regions;
   report historical differences separately from source correctness.
3. Add a leak witness for this source gap, with expected source connection;
   preserve genuine sealed-room negative controls and intentional-opening tests.
   Do not demand this source-open export fill successfully.
4. Keep actor-support/clearance checks, original thin matrix and P1 regression
   controls. Treat gameplay acceptance and normalized same-input repeated-build
   determinism as separate obligations.

This proposal is demonstrated to detect regressions without being installed:
requiring independent EMPTY for the three samples passes fresh pristine/P1 and
fails diagnostic full-off **3/3**. The preserved 42-compile matrix separately
continues to reject P1's thin hull-0 false solids and accepts the diagnostic's
reduced-case correction. Neither evidence set alone grants full-map acceptance.
No production gate, baseline, margin, sample or test expectation was changed.

## Invariants still violated; architectural assessment

The Phase 2 contract remains the appropriate target. Findings by boundary:

- **Source construction:** matched spatial products here; no parsing explanation
  for the Halloween diagnostic regression. The previously documented sub-plane-
  equivalence limitation remains outside any arbitrary-precision claim.
- **Admission versus realization:** P1 demonstrably suppresses a resolved gap
  boundary; uniform repairs that particular decision. They still use separately
  implemented predicates and realizers, without a shared accepted certificate.
- **Winding closure/dimensionality:** the first P1 split cap is source-incomplete.
  Uniform fixes that example but edge-length counts do not certify dimensionality,
  closure, conditioning or volume conservation for every generated fragment.
- **CSG/fragment occupancy:** actor fragment counts change; Phase 2 independently
  established lost slices under old policies. Uniform's extra fragments are not
  individually certified. Source identity exists (`mapbrush`, `original_ptr`,
  side source and plane identities), but that is not a geometric certificate.
- **Terminal occupancy:** uniform full-off still reports SOLID at three proven
  source-empty samples. Heuristic exhaustion followed by combining remaining
  brush contents is not proof of constant occupancy. P1's false-SKY gap leaf is
  a directly traced instance of that failure mode.
- **Portals:** windings can violate incident leaf halfspaces, including one
  portal on the diagnostic leak route. Policy consistency remains unproven.
- **Fill:** the hull-0 leak is source-supported, so no-fill there is correct.
  Uniform full-off hull 2's FAST-fill / PRECISE-leak disagreement is unresolved.
- **Serialization:** observed node/face growth follows the constructed/retained
  trees. No first fault was located in output plane deduplication or file format.

The evidence supports retaining the current brush-BSP architecture while testing
an **invariant-bound correction spanning its split and portal interfaces**.
It does not support a one-constant fix, and it does not demonstrate that a new
geometry kernel, fill algorithm or BSP representation is necessary.

A coherent localized design should use a shared split decision/certificate
carrying ancestor and source supports, child halfspaces and cut geometry; realize
exactly those admitted children; independently check conservation and supported
occupancy before CSG fragments or terminal leaves are accepted. Distinguish
source-supported boundaries from generated near-coincident intersections using
provenance and conditioning, not a thickness-only deletion rule. Numerically
uncertain pieces need an explicit diagnostic/failure policy or a justified robust
fallback, never automatic mostly-side assignment that silently changes occupancy.
Reliable winding rank/area and closure checks must replace edge counts as the
meaning of geometric validity. Portal clipping must stay inside both incident
regions and preserve real connections without inventing them.

Existing plane/brush ownership, source backreferences, BSP recursion and portal
endpoints provide useful integration points. Migration risks are actual CSG
subtraction semantics, shared fragment lifetimes, bevel/contents behavior, brush
ordering/FAST versus PRECISE selection, and fill-driven visibility/rebuild reuse.
A larger replacement would only be justified if these interfaces cannot express
and preserve certified child regions. Its precise potential boundary would be
convex halfspace intersection/split realization plus CSG fragment conservation,
with portal realization consuming the same partition contract; parsing, export
formats, VIS/LIGHT and the editor are not replacement targets.

## Experiments, limitations, and recommended Phase 4

No new correction candidate was created. Experiments were controls and read-only
instrumentation:

- Hypothesis: growth starts with many more partitions. Invariant: unchanged
  source geometry compared before fill. Result: about 7% more initial nodes;
  final growth is mainly later retention/rebuild behavior.
- Hypothesis: no-fill accounts for most visual growth. Invariant: identical P1
  geometry/flags except fill, with actor generation suppressed for isolation.
  Result: 93.76% controlled hull-0 byte difference; not a per-fragment proof.
- Hypothesis: diagnostic crosses a source blocker. Invariant: independent source
  halfspaces on unchanged MAPs. Result: original route avoids solid interiors;
  corrected midpoint route has positive source margin and reaches outside.
  The initial parser/detour error was detected and rejected.
- Hypothesis: portals match partition regions. Invariant: every winding vertex
  satisfies each incident leaf's ancestor halfspaces. Result: violations in P1
  and uniform, including one leak portal; topology is not certified.

The exact existing diagnostic's 42-compile thin matrix receipt remains valid;
its binary hash is unchanged. No candidate emerged to justify replaying that
matrix or performing native/VIS/LIGHT release work. Controls do not earn a new
thin-matrix PASS. No speculative tolerance substitutions were tested.

Recommended Phase 4 is a focused implementation/research boundary, not deployment:

1. Preserve minimal read-only witnesses for the first cap error, rejected sky
   boundary, source gap, three full-off false solids and the leak-portal violation.
2. Trace uniform full-off's false-SOLID leaves and hull-2 pass disagreement to
   their first occupancy/topology fault before choosing final fallback semantics.
3. Develop one shared certified convex split path covering volume admission,
   actual realization and CSG conservation; align portal clipping with those
   certified regions. Keep P1 and source identities intact.
4. Evaluate one isolated candidate with the unchanged 42-compilation matrix,
   original actor witnesses/P1 controls, both frozen full maps, source-derived
   witness assertions, portal containment/connectivity and pre/post-fill counts.
   Accept real source leaks; reject invented openings and false solids.
5. Only after correctness, assess residual fragment growth and representative
   gameplay/consumer/determinism risks. Propose the gate revision explicitly;
   obtain separate implementation/release acceptance before deployment.

The investigation resolves the primary hull-0 leak and most size growth. It
leaves a precise full-map correctness boundary: uniform full-off false solids,
actor pass-dependent fill and portal consistency. There is no manufactured
passing compiler and no accepted P3 correction.

## Production and repository status

Qartographer production, Qrucible, authored MAP/.qart files, VIS/LIGHT algorithms,
BSP/MAP formats, active compiler source, accepted P1, P2-unapplied.patch, installed
QQBSP and stock utilities were unchanged. No exporter compensation, installation,
deployment, baseline promotion, commit or remote push occurred. Existing untracked
Phase 1/2 research files were preserved. Only Phase 3 research documentation and
evidence were added. Large disposable trees/builds/BSPs remain in
`/tmp/qqbsp-phase3`; compact receipts, scripts, selected source/trace evidence and
logs are preserved alongside this report with a SHA-256 manifest.

Installed QQBSP SHA-256 remains
`49d766579a03701d6a5bb3560112bc756afdb8cf4488242e0b8db72668d8c8c0`.
Compiler source hashes remain brush.cc `e1b6fe03…` and brushbsp.cc `6baec9ac…`;
full identities and repository status are in
[status evidence](thin_brush_phase3_evidence/status.json).
