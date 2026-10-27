# QQBSP Phase 7 — partial compiler integration; not production ready

2026-10-26. **Recommendation: retain the experiment and revise. Do not promote or deploy.**

The Phase 6 bounded-halfspace component is now linked into an actual QQBSP build,
and its decisions replace rounded-vertex extent tests in important compiler paths.
This fixes the captured P1 empty-child decision and the rotated portal's edge-only
classification. Local hull-2 and narrow-quadrilateral realization tests pass.
Forty of the 42 existing thin-brush matrix compilations pass all 47,378 unchanged
source-occupancy comparisons performed on those successful outputs. Two rotated
thin-brush compilations still fail construction. Halloween does not produce a BSP.
These are useful integration results, **not fulfillment of the Phase 7 mission**.

An ordinary BSP29 was consumed by stock VIS/LIGHT and exercised in native
QrustyQuake. Player movement and wall collision agree with the source-derived
configuration-space oracle. That evidence covers an ordinary room, not Halloween,
the microscopic case, the rotated thin brush, or native hull 2.

## Baseline, isolation and identities

Reviewed THIN_BRUSH.md and Phases 2–6, Phase 5's unaccepted patch/source, the Phase 6
component/oracle/policy and executable cases, and README, baseline.json, BOOTSTRAP,
NATIVE_ENGINE and repository instructions. The experiment starts from accepted P1
at `4b505ae25e508a8910b031e94d6f1ea60ac06a95`, with the Phase 5 slice reapplied privately.
P2 remains unapplied. No algorithms from the rejected uniform-epsilon experiment
were substituted for support-based decisions.

* Isolated source/build: `/tmp/qqbsp-phase7/{source,build}`.
* Final development ELF: `/tmp/qqbsp-phase7/phase7-unaccepted-qqbsp`, SHA-256
  `64d718230afa0b7b636968ea3fc32e250e503b0f6f6c2aaebd81ca8169c933c6`.
* Archived campaign ELF: `/tmp/qqbsp-phase7/campaign-qqbsp`, SHA-256
  `bf26e8178aaf7c0618f6b5f5e247698849d438e7bf4c8efad19c515b431298ca`.
* Installed P1 remains SHA-256
  `49d766579a03701d6a5bb3560112bc756afdb8cf4488242e0b8db72668d8c8c0`.
* [Status and complete source hashes](thin_brush_phase7_evidence/status.json),
  [recoverable patch](thin_brush_phase7_evidence/phase7-unaccepted.patch),
  [complete changed-file snapshots](thin_brush_phase7_evidence/implementation/).

Only the Phase 7 report/evidence are added to the active compiler repository.
Tracked compiler sources remain unchanged. A comparison of all tracked baseline
files against the isolated source finds only the eight existing files named below
changed; new headers and frozen test inputs are also in the patch. `qbsp/brush.cc`,
including P1, is unchanged. No installed executable, authored MAP/.qart, exporter,
collision workaround, VIS/LIGHT source, engine or game asset was modified.
No commit, push, deployment, or new execution/threading architecture was introduced.

## Implementation and data flow

The patch includes Phase 5's shared supported split and representation preparation,
with the following Phase 7 replacements. There is one active split implementation.

1. `include/qbsp/halfspace.hh` copies Phase 6's filtered/GMP decision component
   byte-for-byte. Its binary64 inputs retain their exact rational meaning.
   `supported_geometry.hh` adapts working planes without deriving constraints from
   winding vertices. GMP/GMPXX are now **experimental compiler link dependencies**;
   no package was installed. libqbsp and its test target disable fast math and
   contraction. Environment/nonfinite/unbounded/96-constraint limits remain explicit.
2. `BoxOnPlaneSide` uses the component's filtered/exact point signs on complete box
   corners; uncertain/contact returns BOTH. Bounds derived from approximate windings
   are **not** used to decide fragment routing: `TestBrushToPlanenum` uses the retained
   source/CSG/ancestor halfspaces through `SupportedBrushSide`.
3. `SupportedSplit`, `CheckSplitBrush` and `CheckPlaneAgainstVolume` share that child
   decision. A child is an interior child precisely when its closed halfspace region
   has dimension 3. Empty/contact-only children do not demand cap reconstruction;
   the unchanged positive parent routes to its supported side. Admission performs
   classification, while actual construction can separately fail with
   `CONSTRUCTION_UNSUPPORTED`. Numerical uncertainty remains a different diagnostic.
4. Source fragment splitting, node-volume realization and CSG subtraction still use
   the one Phase 5 `SupportedSplit`. Every parent support survives even when its
   winding disappears. Child supports, ownership and original source pointers are
   retained. Existing long-double polylib reconstruction and backward residual
   checks remain construction tools; they are not advertised as exact reconstruction
   or complete topology certificates. No thickness threshold, hull replacement,
   welding, plane perturbation or silent one-sided construction fallback was added.
5. `LeafNode` uses `SupportedCoversRegion`: every contributing fragment must contain
   the entire positive-volume node according to support predicates. It cannot infer
   coverage from a centroid or rounded vertices. This is a sufficient single-convex
   contributor proof, not a general source-union coverage algorithm. Empty-list
   leaves still depend on upstream CSG/routing conservation; independent complete
   source-union exclusion at every terminal leaf remains unfinished.
6. BuildTree prepares its split before publishing children. On a representation
   failure, it may terminate a node only if an original SOLID source covers the
   **whole parent** in both binary64 and independently float32-rounded plane models.
   A lower-dimensional/empty target region does not satisfy that proof. Ancestor
   and root boundaries stay unchanged; a wholly solid parent has no traversable
   internal or external empty port to disconnect. Original contributor ownership
   is retained. Tests cover ordinary enclosure, mixed thin-wall rejection and
   float32-collapse refusal. This narrow rule has **not** been demonstrated to
   resolve Halloween or a representative failing real node; general union coverage,
   mixed-content precedence and broader port-preserving quotients are not implemented.
7. `buildportal_t` retains defining supports separately from its winding. Head
   portals carry root bounds; recursive portalization receives those root bounds
   even when its boundary-portal list is empty (including VIS portalization).
   `BaseWindingForNode` remains an approximate constructor; `MakeNodePortal` first
   certifies its root-plus-ancestor section. `SplitNodePortals` appends each
   directional constraint to the inherited portal region before testing section
   dimension. Contact cannot manufacture an area connection. A certified area
   with no usable winding is an explicit unsupported construction. The clipped
   remainder, rather than the old unclipped polygon, is retained on a surviving side.
   Incident-region residual checks remain enabled before publication.

Changed existing files: `brushbsp.hh`, `portals.hh`, `brushbsp.cc`, `portals.cc`,
`prtfile.cc`, `qbsp/CMakeLists.txt`, `qartographer/CMakeLists.txt`, `test_qbsp.cc`.
New files include the two geometry headers and frozen Phase 5/7 test inputs.
The banner explicitly identifies `experiment=phase7-unaccepted`.

## Stage A — actual pathways and independent decisions

Six focused test purposes pass across the retained XML receipts: local hull-2
split, narrow split, nine failure-site support decisions, complete-region coverage,
and upstream duplicate-plane/empty-brush behavior. The nine captured systems are
used by the linked classifier/portal helper, not a separately implemented test
classifier. The E test supplies no windings and confirms actual `SupportedSplit`
routes the same parent object back without reconstruction.

The independent Fraction/Fourier–Motzkin oracle was freshly replayed on all nine
systems and agrees with the frozen Phase 6 answers. Its implementation is unchanged.
The Phase 6 header itself is unchanged, so its 87-case standalone arithmetic suite
is reused rather than claimed as a new full compiler campaign.

Evidence: [fresh independent replay](thin_brush_phase7_evidence/integrated-oracle-replay.json),
[site/local tests](thin_brush_phase7_evidence/focused.xml),
[coverage/upstream tests](thin_brush_phase7_evidence/coverage-focused.xml),
[final two-model coverage guard](thin_brush_phase7_evidence/serialized-coverage.xml).
Initial failed coverage/test-setup and build receipts are retained separately.
The focused test initially tried to create a microscopic box through the existing
approximate plane registry; the corrected test supplies distinct exact supports,
and coverage now explicitly refuses a nonvolumetric parent.

| Phase 5/6 witness | Integrated result | Final-output limitation |
| --- | --- | --- |
| A hull-2 front | Both children positive; actual local split preserves width `0.00024414099993919081`, ownership and the interior witness. Actual post-CSG/12-ancestor classifier replay agrees. | Halloween hull 2 is not reached; survival in its final collision hull is unproved. |
| B narrow quadrilateral | Area section survives all 29 ancestors. Actual cap area `0.0074346256473068455`; preserved independent reference `0.007434625516377664`. Existing conservation tolerance unchanged. | Not a general conditioned-construction proof. |
| C sky/roof gap | Both midpoint children positive in the binary64 model; source gap unchanged. | No Halloween BSP or portal route; source gap is not certified as preserved in output. |
| D Halloween micro front | Positive in binary64, empty in float32 model, exactly as Phase 6. Actual parent/source context is now captured. Whole-parent constant-contents removal is rejected. | Actual cap remains unsupported; no invented geometry or occupancy. |
| E P1 reduced old failure | Front empty, section empty; actual unchanged-parent routing succeeds without winding-based false extent. | Full P1 fixture reaches a different microscopic CSG cut and fails there. |
| F rotated portal | Incident section is edge-only. Shared portal logic emits no area connection; captured BaseWinding/MakeNodePortal sections remain area-bearing. | Rotated hull-0 MAP emits a BSP; complete rotated actor compile fails elsewhere. |

### D: actual node cannot use the proposed constant-contents collapse

The failing partition is X=`208.000061035`, MAP source opening brace line 6336,
after the initial world division at Z=220. The affected BSP parent has seven
retained supports and a large mixed interior. Capture includes all **2,397** input
source records, not just the tiny failing source fragment.

Using exact rational arithmetic on those binary64 coefficients:

* `(162,800,-46)` is strictly inside the BSP parent and inside a source SOLID.
* `(222,-864,-192)` is strictly inside the same parent and outside **every** source.
  The receipt retains one strictly excluding support for each source.

These are counterexamples to **constant** parent occupancy, not a sample-based
coverage certificate. They rule out the narrow whole-node collapse rule. They do
not prove that every possible coupled neighborhood representation is impossible.
A fragment's tiny extent or empty float32 child does not justify deleting the
actual node or its boundary. No affected external-port equivalence has been proved.

[Complete node/source capture](thin_brush_phase7_evidence/halloween-off/node.json),
[reduced fragment](thin_brush_phase7_evidence/halloween-off/node.json.fragment.json),
[exact mixed-occupancy certificate](thin_brush_phase7_evidence/halloween-node-occupancy.json).

### New construction blockers after correct classification

The next P1 failure is hull 1 CSG, source line 4, partition 278, with 24 constraints.
Its exact signed extent is approximately `[-1.7967265464261725e-13,0.9496631557675607]`.
Both children are real in binary64; the back child/section are empty after float32
plane serialization. The rotated room's next node-volume cut at partition 82 has
extent approximately `[-6.930295628411783e-14,200.28220944328072]`, with the same
binary64-positive/float32-empty back distinction. The independent oracle confirms
both cases. Neither is the old E false-positive decision.

[Exact new-blocker results](thin_brush_phase7_evidence/new-blocker-oracle.json),
[P1 witness](thin_brush_phase7_evidence/campaign/p1-reduced/node.json.fragment.json),
[rotated node witness](thin_brush_phase7_evidence/sealed-node.json.fragment.json).

## Stages B/C/E — reduced, real-world and regression results

The original matrix stops assertively at rotated-default. A supplementary driver
runs the remaining cases and records failed compilations as failures, preserving
all original samples, radii, coordinate offsets and tolerances. Aggregate: **40/42
compiles pass; 47,378/47,378 occupancy comparisons pass on emitted outputs**.
The rotated-default/chopfragment pair fail construction. Thin world brushes,
axial orientation/translation, thickness sweep, touching, overlapping and
near-coplanar/CSG pairs pass those existing checks. This is not 42/42 acceptance.
[Aggregate and provenance limits](thin_brush_phase7_evidence/matrix-summary.json).

| Invocation | Exit/result | Wall s | Peak RSS KiB | BSP bytes |
| --- | --- | ---: | ---: | ---: |
| P1 reduced | Unsupported CSG cap | 0.865 | 8,152 | none |
| Ordinary sealed | Success | 0.565 | 7,780 | 1,680 |
| Rotated sealed, hull 0 only | Success | 0.314 | 7,468 | 1,500 |
| Ordinary L-room | Success | 2.518 | 8,456 | 2,288 |
| Halloween off AUTO | Unsupported D cap, hull 0 | 3.470 | 49,340 | none |
| Halloween on AUTO | Unsupported D cap, hull 0 | 3.319 | 50,820 | none |
| Halloween off PRECISE | Incomplete at 180 s harness limit | ≥180 | unavailable | none |
| Halloween on PRECISE | Incomplete at 180 s harness limit | ≥180 | unavailable | none |

All campaign invocations use unchanged input copies, `-notex -nopercent
-chopfragment -threads 1`. The ordinary outputs are BSP29. PRECISE adds
`-forcegoodtree`; AUTO uses the established FAST/AUTO choices. The separate thin
matrix uses BSP2 and both chop modes. Timeouts are incomplete evidence, not
geometric rejection, a correctness acceptance gate, or a reason to lower accuracy.
Memory for the interrupted runs was not recovered. Full-map early-abort timings
are not comparable to completed P1 compilation timings.

[Commands, input hashes, exits and timings](thin_brush_phase7_evidence/campaign/summary.json)
and per-case logs/time receipts retain the failures. Full Halloween actor hulls,
rebuild PRECISE paths, final collision points, false-SOLID source-empty witnesses,
sky/roof opening, flood/leak classification and final portal reachability remain
unvalidated. No genuine leak is declared fixed or hidden; no Halloween BSP exists.
The existing RollerSpline/P1 driver also aborts at a new cap construction (source
line 69, partition 54), before its final occupancy assertions. The full P1 suite
therefore does not pass. Deliberate-leak/full historical Phase 2–5 fixture expansion
was not pursued after these coherent integration blockers; it remains unrun.

### Actual BSP occupancy, geometry and comparison evidence

The three successful ordinary outputs have 6/6/10 nodes and 2/2/3 leaves. The
nonrotated/L-room outputs contain 12/22 clipnodes; the hull-0-only rotated output
contains none. Full counts and lump sizes are in the campaign summary.

Across ordinary, rotated hull 0 and L-room, **3,584 sampled contents comparisons
have zero differences from the unchanged installed P1 compiler**. A first attempt
to apply the raw brush-union oracle to normally filled sealed maps failed: that
expectation omits intentional exterior flood fill. Its failed receipt is preserved;
it is not asserted as source-occupancy PASS. A separate L-room `-nofill` comparison
removes that ambiguity: **1,536/1,536** source/Minkowski checks pass across hulls 0/1/2,
with zero differences from P1, including exterior samples.

The rotated hull-0 output has **7 render faces versus P1's 6**. The extra subdivision
has not been certified for rendering/texture correctness; sample contents equality
is insufficient to accept it. L-room has 22 clipnodes versus P1's 24; sampled
occupancy and native movement agree, but no byte-identity requirement is inferred.

[Filled-map comparison, including the invalid raw-source expectations](thin_brush_phase7_evidence/ordinary-comparison/results.json),
[unfilled source-occupancy check](thin_brush_phase7_evidence/ordinary-nofill/results.json).
Raw BSP bytes are retained as `.bsp.bin`; disposable MAP/BSP paths remain under
`/tmp/qqbsp-phase7/evidence`. The reduced hull-2 local test is not substituted for
an actual Halloween final-hull check.

## Stage D — native Quake and consumer evidence

Stock VIS and LIGHT consumed the emitted ordinary L-room BSP29, producing 2 VIS
bytes and 456 lighting bytes. Plane/node/clipnode/model lumps remain byte-identical
through consumption. No VIS/LIGHT code or installed utility changed.

Native extracted QrustyQuake completed normally, exit 0, in 3.070 s with the
completion marker, both saves and advancing server time (2.286111 → 4.286111).
The player stayed alive, grounded and in ordinary WALK:

* Start `(-56,-96,88.03125)`.
* End `(79.96875,-96,88.03125)` after the established 144 movement waits at speed 100.
* The independent source/Minkowski ray gives the first blocking boundary at X=80.
  Runtime stops 1/32 unit before it; start/end are source-clear and X=80.1 is solid.

This demonstrates real player movement and an ordinary wall blocker. It does not
validate native larger actors, thin projectiles, Halloween traversal, a full
rendering pass, or the rotated extra face.

The installed AppImage could not mount FUSE inside the sandbox, so the already
extracted runtime documented in NATIVE_ENGINE.md was reused. No engine install or
new runtime workaround was developed. An initial handwritten native X expectation
belonged to another room; saved states were validated against the independently
derived L-room boundary without replaying the runtime. The missing-PRT first
consumer invocation and failed AppImage logs are retained as setup failures.

[Native/consumer result](thin_brush_phase7_evidence/native-ordinary-final/results.json),
[engine log](thin_brush_phase7_evidence/native-ordinary-final/engine.log).

## Limitations and narrow next corrective step

The remaining immediate blocker is **representation construction plus semantic
resolution**, not ambiguity about D/E/F classification. Do not build a general
exact reconstruction engine merely to emit these microscopic cells. Do not drop
them because the float32 child is empty.

The narrow next implementation should operate at the failed source-fragment split
and its affected neighboring source union: establish whether a coupled representable
routing preserves the complete local occupied set and all relevant external empty
ports, then realize that certified routing in SplitBrushList/CSG. D's large mixed
parent cannot be replaced by a blanket SOLID/EMPTY leaf. P1's next CSG case needs
the analogous source-union preservation proof. Keep the supplied reduced supports
and complete node/source captures as acceptance inputs. If that narrower proof
fails, retain the diagnostic and partition the affected neighborhood; do not infer
permission from identical float32 planes.

Other unfinished obligations: conditioned approximate boundary incidence/closure;
complete terminal EMPTY/source-union certificates; general SOLID union coverage;
source distinctions lost before the authoritative working-plane model; exact
portal geometry containment beyond residual checks; serialized-model occupancy
and adjacency certification throughout the tree; rotated rendering; full-map
runtime and engine-limit acceptance. Unconditional O(n^4) region enumeration makes
PRECISE expensive; no performance target was traded against correctness, and no
cache/threading project was attempted.

The final guards are deliberately stricter than the campaign snapshot: coverage
requires a volumetric parent, and fallback collapse additionally requires the
float32 model and preserves all contributor ownership. Their focused tests pass.
No final-artifact Tier 3 acceptance is claimed: the matrix's early ELF was not
archived, the successful ordinary campaign uses the separately preserved ELF,
and timed-out PRECISE runs originally hashed the executable path after execution
while rebuilds occurred. Those hashes are explicitly labelled in the annotated
receipt; they do not identify a loaded timed-out ELF. Original receipts remain.
These provenance limits prevent promotion, independently of the geometric failures.

## Reproduction and retained artifacts

Apply only in an isolated archive at `/tmp/qqbsp-phase7/source` (the two direct
fixture tests currently name that exact path). The patch is relative to accepted
P1 HEAD and includes the Phase 5 changes once. Copy the baseline's pinned fmt,
nanobench and pareto submodule sources into the archive; do not apply P2.

```sh
cd /tmp/qqbsp-phase7/source
patch -p1 < /path/to/thin_brush_phase7_evidence/phase7-unaccepted.patch
cmake -S . -B ../build -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DQQBSP_BUILD_TESTS=ON \
  -DFETCHCONTENT_SOURCE_DIR_GOOGLETEST=/tmp/qqbsp-bootstrap/pinned/deps/googletest \
  -DFETCHCONTENT_SOURCE_DIR_JSON=/tmp/qqbsp-bootstrap/pinned/deps/json/json \
  -DTBB_DIR=/tmp/qqbsp-bootstrap/pinned/deps/tbb/oneapi-tbb-2021.11.0/lib/cmake/tbb \
  -Dembree_DIR=/tmp/qqbsp-bootstrap/pinned/deps/embree/lib/cmake/embree-4.4.0
cmake --build ../build --target qqbsp qqbsp_tests -j 4
../build/qartographer/qqbsp_tests \
  --gtest_filter='phase5.*:phase7.*:qbsp.duplicatePlanes:qbsp.emptyBrush'
QQBSP_PHASE7_CAPTURE=/tmp/phase7-node.json ../build/qbsp/qqbsp \
  -bsp2 -notex -nopercent -chopfragment -threads 1 /tmp/input-copy.map
```

Copy authored inputs to disposable output directories first. Do not patch the
already patched retained source again. Existing Phase 6 evidence supplies the
independent oracle; frozen numeric inputs also appear in `phase7-cases.json` in
the patch. `replay_oracle.py`, `certify_context.py`, `replay_new_blockers.py`, the
matrix supplement, ordinary/native drivers and all build/validation logs are in
the evidence directory. Drivers naming the original Phase 6 directory expect its
unchanged copied contents at `/tmp/qqbsp-phase7/phase6`. Campaign commands and
hashes are recorded per case. The original runner's timeout wrapped `/usr/bin/time`
rather than establishing child-process-group accounting; its interrupted time/RSS
receipts are incomplete and must not be used as precise resource measurements.
No two-clean-build reproducibility or package portability is claimed.

**Production assessment: not ready.** Criteria 1–7 are not collectively met.
Local reliable decisions, several actual thin outputs and one ordinary native run
are established; Halloween, complete P1 regressions, meaningful final hull-2 blocker
preservation, source opening/connectivity and general representation safety remain
unresolved. Preserve this smallest coherent experiment and its explicit failures.
