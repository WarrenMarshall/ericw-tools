# QQBSP Phase 4 — fault boundaries and geometric contract

2026-10-26. **Findings-only checkpoint. No correction candidate accepted or
implemented. P1 preserved; P2 unapplied; uniform diagnostic remains rejected.**

Both unresolved boundaries now have concrete local causes. The three hull-0
false solids share one terminal leaf: a valid narrow cut is deleted by admission,
then residual contents are extended into source-empty space. Hull 2 has a
separate false opening: `BoxOnPlaneSide` suppresses a source-occupied 0.000244141
front slice under its remaining 0.001 cutoff. PRECISE loses the blocker during
BSP fragment routing, after CSG retained it. FAST is locally correct at the new
witness, but is not thereby globally certified.

These findings expand the necessary shared-split boundary to include brush-side
classification **before** `SplitBrush`. Replacing only `CheckSplitBrush` and
`SplitBrush` would leave a demonstrated path that bypasses both. This checkpoint
uses the assignment's findings-only option; it does not claim completion of the
implementation or candidate-validation phases.

## Scope and identities

Read root AGENTS.md, README.md, baseline.json, BOOTSTRAP.md, NATIVE_ENGINE.md,
THIN_BRUSH.md, THIN_BRUSH_PHASE2.md, THIN_BRUSH_PHASE3.md and their relevant
preserved instrumentation, source occupancy oracles, fixture/matrix manifests,
and rejected experiments. No editor or Qrucible work was performed.

Repository HEAD remains `4b505ae25e508a8910b031e94d6f1ea60ac06a95`, branch
`qartographer/qqbsp-alpha10`. P1 is commit
`7f2ef6f32ce16ffc5b9167a57f5c7adad0ccdf58`; pinned upstream is
`ccaeb8457a1267860ebe99ed1df7394ebdd6b435`.

Frozen original inputs, unchanged:

| Input | SHA-256 |
| --- | --- |
| full-on.map | `16250e50546f9d1c4654d75e0a6683f70f7eff332ec730793c5f836d39716318` |
| full-off.map | `d5f2ab2a0c5a22d2f0ecaecf77a1bbd72a3c2ce2e3c444fe0b4c517092e5986c` |

New compiler work is read-only instrumentation of the rejected uniform diagnostic
in `/tmp/qqbsp-phase4/source`, copied from the preserved Phase 3 disposable source.
It is not a patch to the active checkout. Build target: only `qqbsp` and its
required libraries, RelWithDebInfo, the existing pinned dependency directories.
The final instrumented executable SHA-256 is
`e2d97785ccf2b50b455624fb2430d626896667fe96385996ee89483cf95d06a3`.
Its inherited P1 banner is **not** an experimental algorithm identifier.
Final source snapshots, diffs, logs, commands and hashes accompany this report.
Earlier two instrumentation executables were rebuilt in place, not archived;
their construction scripts are preserved, but no invented binary hash is given.

Three successive full-off runs use identical copied bytes and flags:
`-bsp2 -notex -nopercent -chopfragment -threads 1 -loghulls`.
The second resolves the precise cap rejection and obtains pre/post-CSG supports;
the third targets the newly identified actor strip's actual routing decision.
These are adaptive fault traces, not three performance/determinism trials.

## A1. Three false-solid witnesses — one terminal occupancy failure

| Witness | Independent source margin, both MAPs | Residual-brush exclusion distance |
| --- | ---: | ---: |
| (-1388,-233,8.778914155553586) | 0.13090506484354592 | 13.857625445206395 |
| (-1376,-257,-12.914510661888684) | 0.8469610158824707 | 39.62245246175462 |
| (-1364,-269,11.605075569064333) | 0.2612034930921254 | 57.16717663963061 |

Source margins come from the standalone-structural-brace MAP reader over each
frozen input separately, conservatively including non-CLIP render brushes from
all entities. The replay reproduces the Phase 3 values exactly. No smoothing
assumption or cross-MAP equality is used to establish emptiness.

All three route to initial hull-0 leaf
`11100001101010100010110001000` (0=front, 1=back). Hull 0 leaks, so no rebuilt
hull-0 tree exists in this diagnostic run. Pruning/serialization maps them to
world leaf 0, contents SOLID (-2). [Final paths](thin_brush_phase4_evidence/final-ids.json)
retain the actual emitted node indices, plane IDs and branches.

The residual fragment belongs to the source brush whose first face is MAP line
15143 (opening brace 15142). Hull-0 CSG is disabled in this invocation; source
and post-CSG fingerprints are identical (2,397 brushes). The fragment remains
bounded by outward source plane 7275:

```
n=(0.5832227470883194,-0.8116464073772524,0.03288368395349463)
d=-633.9685024463479
```

Every witness is outside this retained support by the last table column.
Recorded fragment supports along the path continue to exclude the witnesses;
the compiler has not constructed a source brush that contains them. At the
terminal node the other sides are already `onnode`; 7275 is the remaining
eligible non-bevel, visible, nonempty side. Its positive partition is plane 7274.

Admission sees node-volume distances to 7274 from -80.2421196082704 to
+0.0012489560599533434, so the diagnostic's 0.0001 extent test is passed.
`CheckSplitBrush` constructs a cap, then clips against volume supports in order
6970, 7502, 7536, 7511, 7515, 7531. The winding has five vertices before 7515;
clipping against 7515 with epsilon 0.0001 removes it entirely. The subsequent
iteration returns false. No child realization occurs for this rejected candidate.
The target event log records each clipping count and area.

An independent double-precision plane-triple reconstruction using **all 29
ancestor constraints**, rather than trusting the stored volume alone, finds a
four-vertex cut on 7274:

* Area: **0.007434625516377664** square units.
* Cyclic edge lengths: approximately 0.0000674051594, 168.6055083,
  0.0000215929897, 168.6054979.
* Maximum ancestor halfspace residual at those vertices: 2.84e-14.

The stored-volume-only reconstruction yields the same vertices. The cut is a
long narrow quadrilateral supported by the actual ancestor region. Even if
clipping retained it, `WindingIsTiny(...,0.0001)` would reject it because only
two edges exceed the threshold. This is a second, logically independent barrier,
not a claim that this run reached that predicate with a nonempty cut.

After admission rejects the last candidate, `BuildTree_r` calls `LeafNode`.
`LeafNode` combines the residual brush's SOLID contents into the **entire** node
region, without proving coverage. **This is the first operation that assigns
SOLID occupancy to these source-empty points.** The causal trigger is the
rejected valid separating cut; serialization and fill are not its cause.
All three witnesses share this mechanism.

The stored volume also has a maximum internal support residual 4.08e-5 at the
last two path nodes. That is below the diagnostic clipping epsilon but is not a
proof of a sound error model. The all-ancestor reconstruction avoids treating
that imperfect winding representation as the source of geometric truth.
These are resolved double-precision witnesses, not interval-certified or
arbitrary-precision proofs for all nearby configurations.

Evidence: [path and fragments](thin_brush_phase4_evidence/hull0-path.json),
[terminal bounds](thin_brush_phase4_evidence/terminal.json),
[ancestor cut](thin_brush_phase4_evidence/ancestor-cap.json),
[exact rejection events](thin_brush_phase4_evidence/off-extended-events.log).

## A2. Hull-2 FAST/PRECISE — a false opening after CSG

Pass numbering for full-off world geometry is:

1. Hull 0 AUTO, leaks, no rebuild.
2. Hull 1 FAST; 3. hull 1 PRECISE; both fill.
4. Hull 2 FAST, fills; 5. hull 2 PRECISE, leaks.

All hull-2 passes use the same post-CSG spatial fingerprint:
8,223 fragments, `6181754968638279498`. Source construction has 2,306 brushes,
fingerprint `16083709081223970917`. The rebuilt tree changes splitter policy and
visibility, rather than regenerating source expansion or rerunning CSG.

The normal leak writer suppresses later route files once hull 0 has written one.
Read-only instrumentation captures the otherwise-hidden hull-2 route before
that guard. Its occupant is `light (-1232,-1520,232)`. The first two portals share
empty leaf `1100010010000`. That leaf includes the narrow interval

```
-1280.000244141 <= X <= -1280
```

between ancestor plane 9124 (X=-1280, back branch) and final plane 88776
(X=-1280.000244141, front branch). Width: **0.0002441409999391908**.
The route between these portals crosses a source-supported blocker.

### Independent, small configuration-space witness

The source brush at first face **13366** is an axis-aligned box:
X=[-1552.000488281,-1264], Y=[-1456,-1424], Z=[144,368].
It is an ordinary solid render brush. For the established hull-2 actor bounds
[-32,-32,-24] to [32,32,64], the origin-space collision box is source minus actor:

```
X=[-1584.000488281,-1232]
Y=[-1488,-1392]
Z=[80,392]
```

This analytic box needs no bevel approximation, compiler plane set, or full-map
expanded-hull oracle. Point
**(-1280.0001220705,-1440,236.73692674130805)** lies inside it with minimum
axis-plane margin **48 units**. It is inside the reported empty strip, not on
its boundary. Nearby serialization uncertainty cannot explain a 48-unit
source-box interior being EMPTY. The compiler's pre-CSG expanded support top
is 391.999969482 due to existing working-plane reuse; that small difference has
no bearing on this witness.

| Position X (same Y/Z) | FAST initial | PRECISE initial | Final serialized hull 2 |
| --- | --- | --- | --- |
| -1280.0001220705 | SOLID | **EMPTY** | **EMPTY** |
| -1280.0003 | SOLID | SOLID | SOLID |
| -1279.9999 | SOLID | SOLID | SOLID |

The offending PRECISE leaf has zero residual brushes. This differs from A1:
terminal classification of an empty list is consistent with the input it
received; the fragment was lost earlier.

### First occupancy-losing routing operation on this witness path

Immediately before partition 88776 at path `110001001000`, the source-13366
fragment still exists and covers the witness. Its recorded bounds are:

```
X=[-1360.000488281,-1280]
Y=[-1488,-1392]
Z=[172.03125,322.5093526806837]
```

`TestBrushToPlanenum` calls `BoxOnPlaneSide`. For the axial split, its front
predicate is `bounds.maxX > splitX + PLANESIDE_EPSILON`, with
`PLANESIDE_EPSILON=0.001`. Actual positive front extent is 0.000244141,
so it reports **BACK only (side=2)**. `SplitBrushList` transfers the whole brush
to the back without calling `SplitBrush`. All 38 input fragments go back or
face back; the front child receives none. That invents the empty strip.

This directly locates the first loss for the certified box witness: conservative
broad-phase classification is not conservative. It suppresses a resolved front
region despite admission permitting the partition. It also explains why simply
sharing `CheckSplitBrush`/`SplitBrush` would be insufficient.

The blocker survives CSG: independent interval clipping against pre-CSG expanded
supports and post-CSG fragments finds it on the route, including source line
13366 (and a second blocker at 13174). The compact source/post-CSG supports and
the actual pre-partition fragment-routing log are preserved. This is **BSP
fragment-routing loss**, not necessary blocker removal by CSG in this case.

For every recovered PRECISE hull-2 leak portal, significant ancestor-containment
violations (>1e-7) are absent; logged maximum residual is floating-point scale.
That does not make the connection valid: one incident region has already lost
its source occupancy. The portal graph propagates the false empty region.
Straight lines joining boundary portal centers can route to the solid side on
an exact BSP plane; the interior-strip witness above removes that ambiguity.

**Conclusion:** the reported PRECISE connection is invalid for the source-derived
actor geometry. FAST correctly retains this local blocker. We do not infer that
FAST globally seals correctly or that no other legitimate actor route exists.
An exhaustive full-map expanded-source union/connectivity oracle was not built;
the analytic box and exact routing witness distinguish the competing explanations
for this observed route without requiring one.

Evidence: [initial/final points](thin_brush_phase4_evidence/actor-points.json),
[fragment route](thin_brush_phase4_evidence/actor-blocker-route.log),
[source/CSG intersections](thin_brush_phase4_evidence/actor-source-route.json),
[portal/ancestor analysis](thin_brush_phase4_evidence/actor-route.json).

## A3. Reproducible witness preservation

[Witness index](thin_brush_phase4_evidence/witness-index.json) retains hashed
references to all original frozen maps and relevant Phase 1–3 evidence. It does
not replace or edit those artifacts. New compact data preserve hull-0 ancestors,
source ownership and fragment geometry; actor FAST/PRECISE paths, contents,
source/CSG blocker supports and leak portal vertices; and final serialized IDs.

The first bad P1 cap (source first face 9169, partition Z=220), rejected sky
boundary (plane 4578), genuine 0.00012207 source gap, all three false solids,
Phase 1/2 thin/CSG failures and full-on leak portal 9's 0.00012207 containment
violation remain retained. Prior MAPs and original matrix/oracles are unchanged.
No new authored MAP or .qart geometry was created or edited.

Run the compact **read-only** replay:

```sh
python3 qartographer/thin_brush_phase4_evidence/probe.py
```

It checks referenced hashes, recomputes all three source margins independently
for both MAPs, derives the axis-box actor witness from original MAP coordinates,
checks preserved initial/final actor outcomes and the supported cap, and confirms
that per-input EMPTY assertions reject all three uniform false solids.
[Replay result](thin_brush_phase4_evidence/probe-result.json): PASS for reproducing
known failures, **not compiler acceptance**. Research scripts retain their explicit
/tmp paths for full instrumented reruns; see the evidence README.

## B/C. Geometric contract and implementation boundary

The [proposed contract](thin_brush_phase4_evidence/geometric-contract.md) formalizes
split classification/admission/realization, rank/area/closure/conditioning, CSG
conservation, constant terminal occupancy, portal containment/connectivity,
serialization and explicit numerical uncertainty. It is a design obligation,
not a claim that the current diagnostic satisfies it.

Use the existing brush-BSP architecture and source provenance. The smallest
coherent correction boundary now includes:

1. Conservative brush-to-plane classification: bbox fast paths may over-report
   BOTH; they may not erase a resolved side. Handle uncertain signs explicitly.
2. A shared convex split result derived from authoritative parent/source/ancestor
   halfspaces, consumed by admission, node-volume realization, fragment routing
   and CSG. Carry actual child boundaries/cut geometry, support identities,
   conditioning and a reasoned empty/valid/uncertain disposition.
3. Winding rank/area, support and closed-boundary checks, replacing edge counts
   as validity. Reconstruct supported local intersections where existing clipping
   loses narrow boundaries; do not make arbitrary welding or hull substitutions.
4. A terminal coverage check or further supported partition when residual
   occupancy is not constant. If that cannot be resolved safely, fail the compile
   with source/ancestor context. Neither blanket SOLID nor blanket EMPTY is safe.
5. Portal construction clipped to both certified incident regions, with consistent
   dimensionality and no reuse of the uncut winding after one side is rejected.
   Validate occupancy before trusting graph reachability.

Error bounds must follow actual arithmetic and conditioning. An ordinary epsilon
substitution is not certification. Source-plane approximate equivalence below
DIST_EPSILON, established in Phase 2, remains a separate admission/representation
limit. A correction must not claim to restore distinctions already discarded by
parsing without explicitly addressing that boundary.

No evidence yet requires a replacement geometry kernel, fill system, MAP/BSP
format or exporter. A pragmatic implementation should retain exact/conservative
fast paths and invoke supported reconstruction for uncertain local decisions,
with explicit failure when unresolved. Unconditional plane-triple reconstruction
at every split would need a cost review; this research oracle is not a production
algorithm or an arbitrary-precision robustness guarantee.

**No Phase C correction candidate was implemented.** The new evidence demonstrates
an additional upstream interface violation, and a safe shared operation requires
more work than fixing the two originally named functions. A partial constant
change would still knowingly violate A1 and portal invariants. The deliverable
is a bounded findings checkpoint, not a manufactured passing build.

Exact code scope: research instrumentation adds selected path/side/volume dumps,
initial leaf contents, pre/post-CSG supports, admission rejection logging and
otherwise-suppressed per-hull leak routes. It changes no geometry decisions.
All C++ changes are isolated under /tmp; inert diffs and full final source text
are retained as evidence. Active compiler code, P1 and P2 bytes are unchanged.

## D. Validation and portal evidence

The new read-only replay passes. The diagnostic continues to fail the three
source-empty hull-0 assertions and now has an additional independently demonstrated
source-solid hull-2 false-empty witness. The three instrumented full-off outputs
are byte-identical, SHA-256
`3e4f4119daecb56c37514ddb07196a975a5c33d7a9983bf0e2203c906982851f`.
This bounds instrumentation effects in these runs; it is not two-clean-build
reproducibility certification.

No new correction exists to run through the 42-compilation matrix, original P1
reduced/Roller tests, full-on candidate compile, upstream tiers, native collision,
consumer/VIS/LIGHT or release tests. Their prior receipts remain historical
controls, not new candidate PASSes. Full-on source margins are freshly replayed;
its old compile, real sky opening and portal traces remain preserved. Candidate
D1–D4 validation is **not performed**, not silently passed.

Phase 3 initial hull-0 portal measurements remain the before-state:

| Map/build | Violations >0.0001 | Max violation |
| --- | ---: | ---: |
| on/P1 | 4,733 | 83.56425 |
| on/uniform | 11,456 | 83.56425 |
| off/P1 | 5,963 | 267.77009 |
| off/uniform | 12,938 | 765.93250 |

The full-on route's portal 9 violates an incident ancestor by the actual gap
width, 0.00012207; other route residuals are floating-point scale. Large aggregate
errors are geometrically significant, not rounding noise. Existing one-sided
portal fallback can retain original windings outside their new declared regions.
Not every aggregate violation has been attributed to a specific branch or proven
wrong graph edge. There is **no corrected after-state** and no claim of portal
certification. Hull-2's newly traced route demonstrates the complementary failure:
portal containment can pass while source occupancy and therefore connectivity
are wrong. Both obligations are necessary.

## E. Practical cost — historical controls and instrumented observations

No candidate cost is available. Preserve the matched Phase 3 production/diagnostic
measurements rather than compare instrumented I/O overhead with production speed:

| Full-off | P1 | Rejected uniform |
| --- | ---: | ---: |
| BSP bytes | 2,879,012 | 6,996,688 |
| Emitted nodes / leaves | 12,653 / 6,475 | 40,067 / 21,014 |
| Faces | 16,377 | 40,609 |
| Hull-1 / hull-2 clipnodes | 14,114 / 11,930 | 14,686 / 32,435 |
| Phase 3 wall time, seconds | 47.85 | 48.24 |
| Phase 3 peak RSS, KiB | 1,357,284 | 1,467,080 |

New instrumentation retains the same diagnostic sizes and final geometry counts.
Its world tree counts before pruning/serialization are:

| Tree | Nodes | Leaves |
| --- | ---: | ---: |
| Hull 0 initial AUTO | 61,510 | 61,511 |
| Hull 1 initial FAST | 611,232 | 611,233 |
| Hull 1 rebuilt PRECISE | 260,621 | 260,622 |
| Hull 2 initial FAST | 709,968 | 709,969 |
| Hull 2 rebuilt PRECISE | 371,217 | 371,218 |

Full-off source/post-CSG fragment counts remain 2,397/2,397 for hull 0,
2,306/8,214 for hull 1 and 2,306/8,223 for hull 2. Node recursion has substantial
actor cost; these measurements neither excuse lost geometry nor establish which
extra fragments are necessary. New instrumented wall times are 65.88, 82.15 and
80.52 seconds (see raw time receipts); instrumentation writes large temporary
traces and is not suitable for production overhead comparison. Peak RSS remains
approximately 1.47 million KiB. Exact lump-byte arrays and tree counts are in
[trace receipts](thin_brush_phase4_evidence/trace-receipts.json).

Phase 3's controlled **93.76%** hull-0 growth attribution to fill/rebuild path
remains valid; it is not intrinsic thin-geometry complexity. This phase makes no
new allocation of growth or optimization claim. No native/format-limit acceptance
was reached for a corrected compiler.

## F. Separate production-gate proposal and next step

[Gate proposal](thin_brush_phase4_evidence/production-gate-proposal.md) distinguishes
per-source geometric correctness, legitimate distinct-input differences,
historical compatibility, engine/gameplay behavior and determinism/performance.
It retains every old witness, the 42 compilations and original P1 controls,
and adds the independent hull-2 box witness. The replay demonstrates rejection
of the uniform diagnostic's original **3/3 false-solid regressions** without
cross-MAP equality. No production assertion or baseline was changed.

Next: implement one isolated vertical correction across conservative plane
classification, shared supported split geometry and terminal occupancy, then
make portal realization consume the same region contract. Begin with the two
new compact witnesses and original cap/sky/CSG controls; run the unchanged matrix
and both frozen full maps only after that coherent slice exists. Report uncertainty
as such and keep the real source opening as an expected source fact. Do not
promote the uniform diagnostic or a single-cutoff substitute.

## Production, deployment, commit and repository status

Active compiler source and all tracked files remain unchanged. Only this report
and Phase 4 research evidence are added; existing untracked Phase 1–3 work is
preserved. No commit, remote push, production promotion, deployment, installed
replacement or acceptance-gate installation occurred. Qartographer, Qrucible,
authored MAP/.qart files, stock utilities, VIS/LIGHT and format semantics were
untouched. P2 remains unapplied.

Installed QQBSP SHA-256 remains
`49d766579a03701d6a5bb3560112bc756afdb8cf4488242e0b8db72668d8c8c0`.
[Status and identities](thin_brush_phase4_evidence/status.json) record repository,
source, gate and installed-artifact hashes. The evidence SHA-256 manifest covers
preserved files; large disposable trees, source/builds and BSPs remain under
`/tmp/qqbsp-phase4`. These findings justify continued implementation research,
not release acceptance.
