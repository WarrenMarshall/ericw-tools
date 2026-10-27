# Proposed geometric contract (research; not installed)

Let H(p)={x | n.p*x <= d.p}, using oriented, normalized working planes with
retained source identities. Let R be the bounded root region intersected with
all ancestor branch halfspaces. Let F_i be a source-supported brush fragment,
including its ordered CSG subtraction constraints. Windings describe boundaries;
they must not silently replace the authoritative intersection of halfspaces.

1. **Classification and admission.** A broad-phase box test must conservatively
   contain the true plane relation. It may over-report BOTH, never suppress a
   resolved side. A true one-sided return requires an enclosing interval proving
   the other open halfspace empty. ON/uncertain cannot mean drop a fragment.
   Admission and realization share the same parent, partition identity and
   computed child result; no independent smaller/larger geometry decision.
2. **Split certificate.** For accepted P and partition q, certify
   C_back=P intersect H(q), C_front=P intersect H(-q). Each child is bounded and
   closed, has consistent oriented faces and a resolved interior, or is certified
   empty/lower-dimensional. The common cut is P intersect boundary(H(q)). Its
   supports and incident edges agree with both children. Child interiors are
   disjoint and their union equals P under the stated error enclosure. Comparing
   approximate volumes alone cannot certify this equality. Check inclusion and
   complete boundary incidence as well. Preserve source and generated supports.
3. **Winding validity.** Check affine rank 2, resolved signed area, support-plane
   residuals, cyclic boundary closure, orientation, convexity, repeated vertices,
   and edge incidence in the closed solid. Report conditioning of plane solves
   and intersections. Three long edges are neither necessary nor sufficient.
   The 0.0074346-area terminal cut in this investigation has only two edges
   longer than 0.0001, yet has four distinct, supported vertices.
4. **CSG.** Certify A-minus-B as the disjoint-interior union of retained outside
   pieces; all removed interiors must be supported by the subtractor. Preserve
   source ownership, contents precedence, bevel semantics and hull expansion.
   An uncertain outside piece cannot be discarded. Empty result and uncertainty
   are different outcomes. The same split object must drive subtraction and BSP.
5. **Terminal occupancy.** A content label requires constancy throughout R under
   the contents/precedence rules. Nonempty residual lists and exhausted candidate
   selection do not establish it. Prove R covered by the corresponding fragment
   union, or split at unresolved boundaries. For mixed residual occupancy with
   no certifiable partition, stop that compile with source/ancestor diagnostics;
   do not emit a misleading successful collision result. One centroid test does
   not prove coverage; nor may the whole region simply be labelled EMPTY.
6. **Portals.** A portal between leaves A and B is the rank-2 intersection of
   their closures on the common separating support, restricted by every relevant
   ancestor halfspace on both sides. Certify winding inclusion, positive resolved
   area, and compatible adjacency. Keep a valid clipped remainder even when the
   opposite remainder is rejected: never substitute the original uncut winding.
   Degenerate contact is not a traversable area portal. Graph reachability alone
   does not certify source clearance; the new hull-2 witness proves this.
7. **Error and failure policy.** Separate floating arithmetic error, error in
   normalized source planes, ill-conditioned intersections, and intentional BSP
   float32 serialization. For dot products, use an enclosure derived from the
   sum of absolute products and floating-point error bounds; for solves, include
   conditioning and residual bounds. Do not rename DIST_EPSILON a certificate.
   Accept signs only when their enclosures separate from zero. Recompute with a
   justified stronger local predicate or report NUMERICAL_UNCERTAINTY. Distinguish
   certified empty, invalid input/result, unsupported representation and internal
   invariant failure. Ordinary doubles do not prove arbitrary precision.
8. **Output.** Recheck serialized planes against the certified occupancy where
   float32 conversion can affect a resolved separation. Preserve MAP/BSP semantics
   and engine limits; a working-double proof alone does not certify engine space.
   The demonstrated actor strip is two float32 ULPs wide at X=-1280 and survives
   serialization as a false EMPTY region; format collapse is not its cause.
