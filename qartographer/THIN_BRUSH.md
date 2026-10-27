# Thin-brush hull-0 false solids — findings, no accepted correction

2026-10-26. **Predates P1; reproduced in current upstream. No deployment.**

The original 64 × 64 × 0.008 world brush is parsed as valid, bounded geometry.
Its upper support remains available through brush construction but is rejected
as a BSP partition by the node-volume split-admission check. This creates an
unbounded false-solid region above the thin brush in hull 0. A local experimental
correction fixes the reduced Z-thin fixture but fails other requested geometry
cases, so it is **rejected**, not P3. No active compiler algorithm was changed.

Qartographer, Qrucible, VIS/LIGHT, authored maps, the installed compiler and stock
utilities were not modified. All builds and runtime inputs were disposable.
The only repository additions are this report, regression fixtures/probe and
preserved evidence. P1 remains intact; P2 remains unapplied.

## 1. Regression boundary

Identical reduced MAP bytes and flags were compiled under all three compilers.
Flags: `-bsp2 -notex -nopercent`, with and without `-chopfragment`.

| Compiler | Source identity | Thin hull 0 | 0.25-unit control |
| --- | --- | --- | --- |
| Pristine alpha10 | `ccaeb8457a1267860ebe99ed1df7394ebdd6b435` | FAIL | PASS |
| Installed P1-only QQBSP | downstream `a39a599d08967998d01e85d10ac356f823e27a35` | FAIL | PASS |
| Current upstream main | `36eec1da2a194467e6baac2f444c2dd04b57d266` | FAIL | PASS |

Upstream main was queried with `git ls-remote` during this assignment. Its
archive source was checked byte-for-byte against that revision: 491 regular
files, zero mismatches (exact count in the linked receipt is authoritative).
Its gitlink revisions were extracted independently, including current fmt and
JSONcpp; the alpha10 dependency setup was not silently substituted. GCC 13.3,
RelWithDebInfo and existing TBB/Embree provisioning were reused. Only QBSP and
required libraries were built. The upstream archive's banner has no Git version
string; its exact source check and binary SHA-256 identify it instead.

Original five witnesses, for **every compiler and both flag modes**:

| Point | Source hull 0 | Thin BSP hull 0 | Control BSP hull 0 |
| --- | --- | --- | --- |
| `(0,32,0)` | solid | solid | solid |
| `(0,32,1)` | empty | **solid** | empty |
| `(0,32,10)` | empty | **solid** | empty |
| `(0,32,-10)` | empty | empty | empty |
| `(40,32,0)` | empty | empty | empty |

All these witnesses are solid in actor hulls 1/2, as expected: the actor boxes
intersect the source even where a point does not. That is not a hull-1/2 failure.
The independent matrix below also checks actor-clear samples.

Pristine and P1 produce **byte-identical BSPs for every one of the 42 matrix
compiles**, as well as identical oracle failures. There is no evidence of a P1
regression. The initial reduced thin BSP SHA-256 is
`62fdabc9d97df450a1e15c1cc5287d7fda734fabde240d5070a98610fb75cf24`.
Pristine compiler SHA-256:
`b80a35bc57eee9906c259abf2aa30a475c6a3f0864b6e4f9c16f233f9658d880`.
Installed P1 compiler SHA-256:
`49d766579a03701d6a5bb3560112bc756afdb8cf4488242e0b8db72668d8c8c0`.

[Boundary results](thin_brush_evidence/boundary.json),
[upstream results](thin_brush_evidence/upstream.json),
[source verification](thin_brush_evidence/upstream-source-check.json),
[queried upstream SHA](thin_brush_evidence/upstream-head.txt).
Each boundary compile's log and actual BSP are preserved in that directory;
`.bsp.bin` files are unchanged raw BSP bytes, renamed to preserve evidence rather
than be mistaken for generated ignored build outputs. Results identify their hashes.

## 2. First incorrect stage

The defect is in **BSP split admission**, not MAP decimal parsing or BSP output
plane deduplication. Source line numbers below refer to unchanged pinned alpha10.

1. The MAP defines six distinct planes and a bounded box
   `X=[-32,32], Y=[0,64], Z=[-0.004,0.004]`. Both Z distances survive as distinct
   double-precision working planes. Their float32 representability error is far
   smaller than the 0.008-unit thickness.
2. `brush.cc::CreateBrushWindings` constructs the upper and lower face windings.
   Both reach `brushbsp.cc::SelectSplitPlane` as eligible nonempty side windings;
   the debugger observes volume checks for both planes before either is selected.
   A one-brush world supplies no pairwise CSG subtraction that could remove them.
3. After the lower plane is selected, the next upper-plane test in
   `CheckSplitBrush` (brushbsp.cc:646–670) sees:

   ```text
   VOLUME_TEST n=(0,0,1) dist=0.004 front=24 back=-0.008
   ```

   `d_back > -0.1` is true, so the function returns false: the split is rejected because the thin
   back slice is below the hardcoded 0.1-unit cutoff. The points are not coplanar
   within the normal working epsilon; there is a real positive-volume slice.
4. Both `SelectSplitPlane` and `ChooseMidPlaneFromList` call
   `CheckPlaneAgainstVolume` before accepting a side. In this reproducer no
   remaining candidate can close the upper boundary. `BuildTree_r` receives no
   best side and calls `LeafNode`; that function combines the remaining brush
   contents into SOLID for the entire remaining node region. A support plane is
   thereby rendered ineffective even though it still exists in working geometry.
5. `writebsp.cc::ExportMapPlane` serializes selected plane identities without
   geometric merging. The absent `Z=+0.004` output plane is downstream evidence of
   the rejected partition. The tree is already wrong before serialization.

[Compact GDB trace](thin_brush_evidence/trace.log),
[trace commands](thin_brush_evidence/trace.gdb).
GDB used the original symbol-rich P1 executable and disposable MAPs. Sandbox
ptrace was unavailable; the trace ran with approved debugger access. No installed
binary, source, or authored input was patched during tracing.

Related policies matter to any correction:

- `SplitBrush` (brushbsp.cc:410–454) independently uses 0.1-unit one-sided tests
  and `WindingIsTiny(...,0.02)` when realizing splits.
- `CheckSplitBrush` repeats these policies for synthetic node-volume admission.
- `BuildTree_r` realizes child node volumes through `SplitBrush`. Changing only
  the admission test leaves the realized volume inconsistent.
- `TestBrushToPlanenum` and CSG splitting have additional numerical policies;
  preserving node-volume slices alone does not establish correct thin CSG.

The source contains an intentionally conservative tiny-split policy, but the
input is not rejected as unsupported. The default `microvolume` is zero, the box
has positive volume 32.768, and compilation succeeds without an explicit
unsupported-thickness diagnostic. Standard MAP halfspaces and BSP planes can
represent these boundaries; this is **not an inherent MAP/BSP format limit**.
The compiler loses an effective boundary while claiming a successful compile.
This establishes the implementation defect without claiming arbitrary precision
or support for every mathematically nonzero brush.

## 3. Rejected correction experiment

A private source snapshot under `/tmp/qqbsp-p3/source` tested a localized change:
use the existing `DIST_EPSILON` only for synthetic node-volume side/edge tests,
keep actual brush/CSG split tolerances unchanged, and keep admission and child
node-volume realization consistent. No coordinate, hull size, format, or global
plane tolerance changed. P1 remained present.

The original fixture and control pass with this prototype. So do the Z-thickness
sweep and translated case. But the correction is **insufficient**:

| Additional case | Prototype result |
| --- | --- |
| Thin in X or Y | Hull-0 false solids remain; e.g. source-clear points 0.25 units outside an end face |
| Rotated thin brush | Hull-0 false solids remain at 0.25-unit source clearance |
| Adjacent thin cells | Passes the sampled oracle |
| Overlapping thin cells | Missing source-solid hull-0 samples remain |
| Near-coplanar pair | Actor-hull boundary mismatches remain |

These failures are not all attributed to the original node-volume guard without
further traces. In particular, the pair failures require investigating actual
brush splitting/CSG rather than applying the private node-volume change globally.
The actor-pair samples are only 0.00015 units inside their independently predicted
boundary; they remain recorded separately from the unambiguous 0.25-unit
hull-0 false solids. No test tolerance or fixture was relaxed.

[Rejected patch](thin_brush_evidence/node-volume-only-REJECTED.patch),
[prototype identity](thin_brush_evidence/prototype.json),
[all prototype results](thin_brush_evidence/rejected-prototype-matrix.json).
The patch is inert evidence, not applied to the repository, not named P3, and
not accepted for building or deployment. A second partial repair would leave
multiple known incorrect thin-geometry paths; no safe minimal correction has
been demonstrated in this investigation.

## 4. Independent regression coverage

Permanent fixtures: [original MAP](fixtures/thin-direct/original.map),
[thicker control](fixtures/thin-direct/control.map).
The original file retains the retirement gate's exact SHA-256
`dc3bd5aecde1e9bd502decc72b33f28f4ecff2c0712e1b4c5184f2b5ae3fad42`.

`thin_brush_probe.py` reuses the existing independent MAP halfspace reader,
polytope vertices, bevel-support Minkowski oracle and BSP reader. It compares
source union occupancy against hulls 0/1/2, including explicit interiors and
inside/outside support witnesses. Expected geometry never comes from stock BSPs.
Boundary exclusion is 1e-6; the inside support witness is 0.00015 units deep.
Original/control inputs are copied exactly; other cases derive coordinates from
the original and use ordinary MAP texture syntax. Both compilation flag modes
run in every case. A compiler mismatch produces nonzero exit, not a passing
research receipt.

```sh
python3 qartographer/thin_brush_probe.py \
  /path/to/compiler /tmp/qqbsp-thin-new
```

It covers 21 geometries × two modes = 42 compiles per compiler:

- Original and control.
- Z-thickness 0.0005, 0.002, 0.008, 0.015625, 0.02, 0.05, 0.099,
  0.1, 0.101, 0.25, 1 and 16 units.
- Each other axial orientation; translated and rotated geometry.
- Adjacent, overlapping and near-coplanar pairs.

Pristine/P1 Z-sweep: tested values below 0.1 fail; 0.1 and above pass. That finite
threshold observation agrees with the traced guard, not a general geometry limit.
All 42 baseline case results and both hull numbers are retained:
[pristine matrix](thin_brush_evidence/pristine-matrix.json),
[P1 matrix](thin_brush_evidence/p1-matrix.json).
The matrix's repeated equivalent support normals can yield repeated witnesses;
counts are raw checks, not a count of unique geometric defects.

No new passing-before/failing-after oracle expectation was blessed. The permanent
probe is a failing regression for the current compiler, not silently included as
a passing Tier 3 fixture. It should become a required passing release gate when
a complete correction is proposed.

## 5. Validation and release disposition

No correction passed the focused geometry gate. Therefore there was no reason to
run a new Tier 3 release, repeat the established P1 RollerSpline/Halloween runs,
or claim new native or stock VIS/LIGHT acceptance for this prototype. Existing
P1 evidence remains historical validation of the unchanged installed artifact;
it does not certify a fix for this defect. Native thin point/projectile behavior,
corrected large-actor cases, and corrected BSP consumer compatibility remain
acceptance work after a viable candidate exists.

No P3 identity, algorithm commit, build-identity change, stripped release,
installation, automatic branch push, or baseline promotion was made. The
symbol-rich and stripped **installed P1 artifacts remain unchanged**. No stock
utility was written. Development prototype and upstream binaries remain under
`/tmp/qqbsp-p3`; only evidence/fixtures and the regression probe are added here.

Recommended next investigation: trace the failed X/Y and rotated cases through
node-volume clipping and tiny-winding rejection, then the overlapping source
brushes through `SplitBrush`/CSG. Preserve this single-box first-divergence trace
and the P1 acceptance suite. Do not treat globally lowering the 0.1/0.02 policies
as a demonstrated fix, inflate geometry, or reintroduce exporter compensation.
