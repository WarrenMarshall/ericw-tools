# QQBSP Phase 6 — robust bounded-halfspace decisions and practical resolution policy

2026-10-26. **Working standalone experiment; no compiler integration or deployment.**
The immediate Phase 5 predicate failures now have definitive answers. Halloween's
front extent is real in its supplied binary64 halfspaces, but much smaller than
the rounded-vertex claim; P1 reduced has no front child; the rejected rotated
portal is an edge contact. None of these results requires production reconstruction
of every mathematically distinguishable feature.

The bounded-region component passes **87 expected-result cases**: 86 definitive
classifications agree with an independent rational oracle, and one deliberately
unbounded case exercises a documented `Unresolved` limit. Seven additional
float32-plane cases also agree with that oracle. A separate executable policy
study demonstrates safe redundant-divider removal and rejects loss of meaningful
thin blockers. **This does not establish full compiler correctness.**

## 1. Mathematical precision, BSP representation and topology

The decision model is `P = intersection {x : n_i.x <= d_i}`, interpreting each
supplied finite binary64 coefficient as its **exact rational value**. Normals need
not have unit length. No approximate plane equivalence, welding, perturbation,
minimum thickness or winding-derived extremum is part of this model.

Four distinct representations remain separate:

1. Intended authored/decimal geometry, before parsing, normal calculation and
   working-plane deduplication. This experiment cannot recover discarded distinctions.
2. Authoritative supplied binary64 halfspaces, including actual ancestor/source
   constraints. Exact decisions below refer to this model.
3. Rounded compiler winding vertices. These may violate the authoritative supports;
   even an exact sign at such a vertex is not a region-extent certificate.
4. Target BSP planes: `ExportMapPlane` assigns the working normal/dist to float32
   fields. Their independently rounded coefficients define another geometric model.
   A sound binary64 predicate does not prove binary32 occupancy or connectivity.

**Practical production obligation:** preserve relevant source-supported occupancy,
collision blockers and connectivity in representable BSP geometry. It is not to
emit every infinitesimal positive-volume cell of model 2. Exact predicates are a
reference and selective decision tool; an insignificant internal separator may be
removed when its semantic redundancy is proved. Conversely, binary32 collapse,
small width or small volume alone never proves safe removal.

This separation materially simplifies the next construction phase: exact
classification need not imply exact coordinate reconstruction or an automatic
hard failure for a 1e-14-unit child. It instead identifies what must be resolved
by a **topology/occupancy-preserving representation decision**.

## 2. Implemented API and definitive-answer argument

[halfspace.hpp](thin_brush_phase6_evidence/component/halfspace.hpp) is independent
of libqbsp, qplane/winding classes, MAP parsing and BSP output. It accepts copied
four-double plane arrays. Main APIs are:

* `analyze(planes, stats, mode)`: `Empty`, `LowerDimensional` with affine dimension
  0/1/2, `PositiveVolume` with dimension 3, or `Unresolved` with a reason.
* Region plus `q` / `-q` gives back/front child classification. Adding both gives
  the section dimension. The CLI also reports **strict** directional existence,
  distinct from whether a closed child contains only contact.
* `point_side`: exact sign for a supplied binary point, or unresolved input/environment.
  Testing it against all constraints answers whether a constructed binary vertex
  is consistent. It does not claim that a nearby valid reconstructed point exists.
* `relation`: positive proportionality of all four exact coefficients means the
  same oriented halfspace; negative proportionality means opposing halfspaces on
  the same boundary. Different distances remain distinct. Zero normals have an
  explicit degenerate result; constant inequalities are handled by `analyze`.

For each independent triple, the component evaluates homogeneous Cramer
coordinates `(X,Y,Z,D)` **without dividing or rounding a constructed vertex**.
A support sign is `sign(n.X - d.D) * sign(D)`. Singular triples are ignored only
when their determinant is proved zero. Candidate feasibility uses every defining
halfspace. Affine dimension is projective matrix rank of feasible homogeneous
vertices, decided by filtered/exact minors, not edge length or polygon area.

The region must have a certified trivial recession cone. Six axial bounds provide
an inexpensive sufficient certificate. Otherwise the homogeneous recession cone
is intersected with a unit cube; a nonzero ray exists iff that bounded intersection
has a nonzero vertex. This cube bounds **directions**, never replaces the region.
A nonempty bounded polyhedron is the convex hull of its vertices; therefore empty
vertex enumeration means Empty, and their affine rank gives its dimension.
An independently known upper rank from exact opposite constraints permits early
termination. No geometry hull is constructed or substituted into the compiler.

The experimental cap is 96 supplied constraints per `analyze` call (including
added query constraints). A nontrivial recession cone, unsupported arithmetic
environment, nonfinite coefficients or resource cap yields `Unresolved`.
Unbounded geometry is deliberately outside this smaller API, even when a broader
solver could decide it. Infeasible systems with nontrivial recession cones can
also hit that limitation. This is a bounded-region decision component, not a
general-purpose computational geometry engine.

## 3. Selected arithmetic strategy and alternatives

* **Tier 1:** double interval arithmetic. Each basic operation expands outward
  with `nextafter`, enclosing rounding error, including cancellation/underflow.
  Algebraic zeros, multiplication by ±1, and proved exact small-integer operations
  avoid unnecessary widening. Integer bounds follow significand capacity; they
  are arithmetic certificates, not geometric size thresholds.
* **Tier 2:** rebuild an ambiguous expression with long-double intervals. Extra
  precision is useful on this host, but never accepted merely because it is wider.
* **Tier 3:** GMP rational arithmetic on exact double values, computing the same
  determinant/minor expression. Zero is a mathematical answer, not an epsilon band.

`mpq_set_d` conversion is exact according to the [GMP conversion contract](https://gmplib.org/manual/Rational-Conversions).
GMP 6.3.0 was already installed; no package or runtime was installed or modified.
An initially attempted Boost include was unavailable; the preserved failed build
is an infrastructure receipt, not a geometry result. No new dependency enters QQBSP.

Long double alone fails to bound construction error, as Phase 5 demonstrated.
Decimal/high-precision floats without directed enclosures still cannot certify
zero. Expansion arithmetic/robust orientation predicates are viable alternatives,
but require more implementation work across determinant, feasibility and rank
questions. A robust LP implementation could improve scalability; exact
Fourier–Motzkin is useful as a different reference but can grow combinatorially.
CGAL's [filtered kernel pattern](https://doc.cgal.org/Manual/3.5/doc_html/cgal_manual/Kernel_23_ref/Class_Filtered_kernel.html)
also separates exact predicates from inexact constructions; it was considered,
not added as a dependency or copied into the compiler.

The standalone build disables fast math and contraction. The public predicates
check round-to-nearest and reject FTZ/DAZ; tests exercise these guards, nonfinite
inputs, size limits, huge cancellation, subnormal multiplication, and scaled
plane identity. The tested long double has 64 significand bits. There is no
arbitrary-precision reconstruction requirement. GMP out-of-memory is a fatal
resource failure, not a certified geometric answer.

## 4. Independent oracle and validation

[oracle.py](thin_brush_phase6_evidence/component/oracle.py) uses Python `Fraction`
and **strict Fourier–Motzkin inequality elimination**, not triple intersection,
Cramer coordinates, determinant filters or C++ rank logic. Closed feasibility is
checked first. Strict feasibility of all nonconstant constraints proves full
interior. Otherwise constraints that can never have strict slack define the
affine hull; rational row rank gives the remaining dimension. Strict query
inequalities distinguish directional existence from closed contact.

A separate projection introduces `t=n.x-d` and eliminates coordinates to obtain
exact extremal rational bounds. The oracle also checks exact point membership
and scaled plane relations. Constraint ordering/duplication is checked against
the same mathematical input set; mathematical expectations are retained even
when a documented API limitation requires Unresolved.

[oracle-results.json](thin_brush_phase6_evidence/oracle-results.json) and
[summary.json](thin_brush_phase6_evidence/summary.json) preserve **87/87 expected
results**, including the explicit unbounded limitation, and agreement of filtered,
double+exact and exact-only execution. There are **54** reverse/shuffled/duplicate
variants. Controls include face/edge/point contact, contradiction, zero normals,
redundancy, exact coincidence/opposition, nearly parallel planes, large translated
coordinates, transformed geometry, overflow, and positive widths down to binary64's
minimum subnormal. Those tiny mathematical controls validate decisions; they are
not proposed production geometry requirements.

## 5. Preserved witnesses and actual failure-site inputs

| Witness | Exact binary64-model result | Consequence |
| --- | --- | --- |
| A: hull-2 front | Parent and both children dimension 3; section dimension 2 | Front blocker survives; original interior witness is supported. |
| A: actual source route | Post-CSG fragment 4712, source first face 13366, plus all 12 ancestors: same result | This supplements the box control with actual defining supports, not just stored bounds. |
| B: narrow quadrilateral | Parent/front/back dimension 3; section dimension 2 | The long narrow cut is genuine, independently of short edge lengths. |
| C: sky/roof gap | Gap dimension 3, both midpoint children dimension 3 | Distinct boundaries and the empty connection remain. |
| D: Halloween | Front dimension 3; section dimension 2 | The binary64 geometry has a microscopic real front region. |
| E: P1 reduced | Front **Empty**, section **Empty**, back dimension 3 | The positive represented-vertex extent is an artifact. |
| F: rotated portal | Incident-region intersection and section dimension **1** | Edge-only contact; no area-bearing portal needs construction. |

A's exact front width is `1073743473/4398046511104`, approximately
**0.00024414099993919081**. B uses the stored terminal supports plus all 29 true
ancestors; its previously reconstructed area remains approximately 0.0074346255.
Rank is decided from supports, without using that approximate area as an oracle.

D's true positive extent is
`3942959254693559/115746439583400212034729541632`, approximately
**3.406549064390434e-14**, rather than its stored maximum's 1.71e-13.
E's true maximum query distance is approximately **-5.580333679588889e-12**,
not the stored positive 7.62e-12. Both stored extreme points violate at least one
authoritative support. Exact arithmetic at those rounded points cannot fix that.
[Exact projections](thin_brush_phase6_evidence/exact-extents.json) retain fractions.

The F probe captures the actual rejected `SplitNodePortals.front` winding,
separator, both incident ancestor paths and root portal bounds. Its winding has
duplicate/near-duplicate XY values and a different Z endpoint; the authoritative
intersection is an edge. Two opposing supports suffice in the minimized section
counterexample. Additional read-only probes at `BaseWindingForNode` and
`MakeNodePortal` find genuine dimension-2 sections in the rotated fixture.

The actual-site mapping is:

* `BoxOnPlaneSide`: A box control and the actual post-CSG/ancestor route.
* `CheckSplitBrush`, `CheckPlaneAgainstVolume`: B node-volume/29-ancestor replay.
* `SupportedSplit`, `ReconstructFace`: D/E captured source-supported failures.
* `winding_rank`, `SplitNodePortals`: F's rejected winding versus incident constraints.
* `BaseWindingForNode`, `MakeNodePortal`: new oblique-node snapshots, including
  boundary portal supports for the latter.

This is external predicate replay of actual site inputs. The component was
**not linked into QQBSP**, and no compiler decision was replaced. The disposable
Phase 5 probe adds logging and uses one existing worker; it still exits on its
original rank diagnostic. [Probe patch](thin_brush_phase6_evidence/read-only-probe.patch)
and complete probe source snapshots are retained.

Independent rational segment/support checks of the preserved source-opening
routes find **zero closed solid intersections**: 17 segments for full-on and 16
for full-off, each conservatively checked against 2,607 non-CLIP/HINT source-reader
brushes. These are exact decisions for the source reader's normalized binary
planes, not a claim of exact original decimal MAP geometry or native playability.

## 6. Practical resolution policy: what can safely disappear

[practical_policy.py](thin_brush_phase6_evidence/component/practical_policy.py)
is an executable **policy study**, not a compiler collapse implementation.
It separates geometry existence from permission to simplify its representation.

A safe narrow-feature decision can use one of these proofs:

1. **Certified empty child:** route the unchanged parent to its supported side.
   E needs no smaller epsilon, tiny cap reconstruction or production failure.
2. **Certified lower-dimensional portal section:** do not emit an area connection.
   F need not fail an ordinary map. This does not authorize deleting arbitrary
   source collision surfaces or ignoring boundary ownership.
3. **Redundant internal separator of the entire convex node region:** prove its
   contents constant from the complete relevant source union, then preserve all
   external supports and ports while merging the siblings. For EMPTY, the convex
   parent's interior remains connected; graph contraction must preserve external
   port reachability. For SOLID, covered occupancy remains covered. A positive
   child, however tiny, need not be reconstructed merely to retain a redundant cut.
4. **More general coupled target resolution:** require a separate source occupancy
   and adjacency equivalence certificate for the affected neighborhood. Neither
   coefficient proximity nor identical serialized planes is that certificate.

The study proves EMPTY by absence of closed source intersections, and SOLID by
exact coverage of the entire parent union, using strict-complement feasibility.
It does not use a centroid or samples. Coverage has an explicit work budget.
Tests accept empty/solid internal dividers and touching-brush union coverage,
withhold acceptance when external-port transport is unproved, and reject a thin
separating wall, the hull-2 blocker and the source gap. A graph example verifies
external-port reachability after a justified empty-parent contraction; deleting
a solid wall instead changes that reachability and is rejected.

An adversarial wall only **2.842170943040401e-14** units thick has identical
float32 boundary coordinates but separates a two-unit corridor. Its deletion is
**not** approved. This directly rules out both a blanket minimum thickness and
"same float32 plane therefore safe" policies.

The external-boundary/ports condition is a **required proof obligation**, supplied
as an explicit study assumption and verified in the toy graph; it is not a
boolean shortcut that production may assert without evidence. Proof scope is the
entire node and all affected sources/ports, not a single solid fragment. Merging
a source fragment's own split does not authorize losing its front occupancy from
a larger BSP node. For D, the complete node-level semantic/portal neighborhood has
not been certified here, so the study withholds collapse approval for missing
context, **not** because 3e-14 must be reconstructed at all costs.

### Target BSP representation experiment

Seven cases round plane coefficients exactly as float32 output fields and rerun
both independent decision procedures. These are separate model comparisons,
not replacements for the binary64 acceptance witnesses.

* A (including actual route) and B remain volumetric on both sides with area cuts.
* C's two gap boundary planes remain distinct and the gap remains volumetric.
  Its chosen midpoint separator rounds onto a boundary, producing contact on
  one side; that is not closure of the source opening.
* D's serialized-plane front child is Empty; its maximum query distance is about
  **-2.3912960009936347e-5**, versus +3.41e-14 in binary64.
* E remains front-empty, with maximum about **-0.0005141397010869492**.
* F remains an edge, not an area portal.

[Quantized-model results](thin_brush_phase6_evidence/bsp-quantized-oracle.json)
show why target precision deserves its own contract. Normal and distance rounding
can move an intersection much more than its original microscopic extent.
This is not permission to adopt every quantized occupancy change blindly. It
supports avoiding exact infinitesimal **construction**, conditional on semantic
certification of the chosen representable result. Full-map topology, engine
arithmetic, collision and serialization acceptance remain separate obligations.

## 7. Cost and practicality

Single sequential reference-host measurements; no statistical speed claim.
Each bundle includes parent/front/back/section, directional tests and optional
point/plane queries. [Raw measurements](thin_brush_phase6_evidence/summary.json)
separate primitive sign counts from region queries and exact construction work.

| Execution | Aggregate 87 bundles | Fast / adaptive / exact sign calls | Requested allocations | Cumulative bytes |
| --- | ---: | --- | ---: | ---: |
| Double + long-double + exact | 106.805 ms | 508,461 / 1,489 / 2,186 | 750,126 | 11,084,699 |
| Double + exact | 102.964 ms | 508,461 / 0 / 3,675 | 939,700 | 13,294,891 |
| Exact-only enumeration | 1,211.872 ms | 0 / 0 / 512,136 | 40,477,851 | 463,875,643 |

The three-tier path uses **99.282% fast**, **0.291% adaptive**, **0.427% exact**
primitive signs. Long-double filtering reduces exact signs and allocations but
did not improve total wall time in this single trial. The simpler double+exact
variant remains viable; no production strategy is chosen from noisy timings.

These percentages are **not** claims that only 0.427% of complete operations use
any exact work: 33/87 bundles have exact sign fallback; the filtered run builds
2,133 exact homogeneous candidates and processes 394 small exact equality-rank
rows. Those costs are separately exposed rather than hidden in filter statistics.
Ordinary axis and transformed box controls need no exact sign or homogeneous
fallback, although their section equality bookkeeping uses small rationals.

There are 345 region API calls, plus directional enumeration. Worst observed
region call: **4.029 ms**. Worst complete bundle: **23.423 ms**. A separate timed
sign run observes **89.661 microseconds** maximum including timer/scheduling
overhead; this is an observation, not a latency bound. Peak per-case live tracked
allocation increment is 22,016 bytes; process peak RSS is 4,876 KiB. Accounting
covers ordinary C++ heap allocations and GMP's custom allocator; stack and any
GMP alloca scratch are excluded, and JSON bookkeeping is included. GMP hooks
are installed only in the standalone measurement executable, not the header or
compiler; see the [allocator contract](https://gmplib.org/manual/Custom-Allocation).

Added redundant ancestor constraints at depths 0/8/16/32/64 take approximately
0.042/0.158/0.363/1.087/3.713 ms per bundle. Enumeration has worst-case O(n^4)
constraint work and substantial temporary allocation. This is plausible as an
experimental **rare fallback/reference**, not as an unconditional test at every
BSP candidate. Future integration should retain certified cheap separation and
reuse results keyed by effective support coefficients/query, independent of
presentation/source-owner metadata. No performance-critical cache or new async
path was introduced in this phase.

## 8. Representation boundary and next compiler phase

Existing `qplane3d` values can supply the coefficient model without public format
changes. Plane orientation and all source/ancestor/CSG inequalities must survive
independently of whether a boundary winding is active. A region/query plus a
parallel immutable mapping of plane IDs, source ownership and ancestor provenance
is sufficient; this experiment copies/sorts coefficients for decisions and leaves
caller identity records untouched. Exact duplicate coefficients may share a
calculation without merging authored identities. Approximate equivalence is never
an identity certificate.

The smallest interface changes for another experimental compiler phase are:

* Pass a complete support view into admission/realization, including inactive
  ancestors and CSG boundaries. `CheckPlaneAgainstVolume` already has node context;
  a disappearing winding must not erase its inequality.
* Pass both incident region views, root boundary and separator into portal rank
  decisions; winding vertices alone cannot answer F correctly.
* Keep the exact classification separate from a **chosen representable construction**.
  E can avoid a nonexistent split; F can avoid a nonexistent area portal. D may
  use a certified representational resolution rather than infinitesimal geometry.
* Before terminating or merging a node, prove source-union coverage/clearance and
  affected external connectivity. Preserve the Phase 1–5 meaningful witnesses;
  no smallness-based SOLID or EMPTY fallback is permitted.
* Retain a diagnostic when meaningful occupancy/topological consequences or a
  construction cannot be established, distinguishing that from predicate uncertainty.

**Recommendation:** accept this bounded standalone decision component for further
experimental work, not for production. Use it as an oracle/adaptive fallback while
designing conditioned approximate construction and semantic simplification. Do
not integrate the enumerator into every split or demand exact coordinates for
all microscopic cells. General unbounded feasibility, scalable LP-style decisions,
full-region union proofs, real-neighborhood portal transport, target-format
occupancy preservation and complete compiler integration remain unfinished.

## 9. Reproducibility, artifacts and production status

[run.sh](thin_brush_phase6_evidence/component/run.sh) builds only the standalone
component/guard tests into a **new** output directory, runs the frozen numerical
cases in all three modes and compares against the independent oracle. GMP headers
and libraries plus the pinned JSON include directory are required. No compiler
source patch or production build is part of that command. See the evidence README
for the separate policy, quantization and read-only probe receipts.

Final standalone executable SHA-256:
`3946ae579f07e9ae4051b9e16a779f2fc12aa169d6b8b07179a91db8b4ea7703`.
Sources, tests, binary64 hex coefficients, minimized D/E/F supports, snapshots,
logs, hashes and build instructions are preserved. Original source identities
and MAP hashes remain unchanged. No two-clean-build binary reproducibility claim.

Work is based on accepted P1 at HEAD
`4b505ae25e508a8910b031e94d6f1ea60ac06a95`; P2 remains unapplied and Phase 5
unaccepted. The active tracked compiler diff is empty. Only this report and
standalone experimental evidence are added. No full compiler acceptance campaign,
new Halloween compile, production integration, commit, push, deployment, installed
replacement, authored MAP/.qart edit, Qartographer/Qrucible change or VIS/LIGHT
change occurred. Installed QQBSP remains SHA-256
`49d766579a03701d6a5bb3560112bc756afdb8cf4488242e0b8db72668d8c8c0`.
