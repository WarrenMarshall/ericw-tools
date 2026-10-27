# Phase 2 geometric contract (before candidate algorithm changes)

A source brush denotes the intersection of its oriented halfspaces, not its
bounding box. Distinct source planes, bounded full-dimensional windings and a
positive, numerically resolvable interior describe a valid solid. A thin solid
is not degenerate merely because an edge or plane separation is below 0.1 or
0.02. Zero-dimensional/area/volume intersections, inconsistent halfspaces,
unbounded intersections, and unresolved numerical signs require separate handling.
A clipping sliver is not identified by thickness alone: its supporting planes,
consistent intersections, winding dimensionality, and relation to the parent
must establish whether it represents real occupancy or arithmetic error.

The BSP node region is the root region intersected with ancestor halfspaces.
Its synthetic volume must represent that region, independent of the order in
which the same planes are introduced. A selected partition must intersect the
region in a reliable two-dimensional polygon and produce two bounded,
full-dimensional child regions. Admission and realization must agree on those
facts and on plane-side decisions. No missing child volume may terminate a
nonempty region whose source occupancy remains heterogeneous.

Each source fragment represents the source intersected with ancestor halfspaces
(and any CSG subtraction). Splits must conserve occupancy on both sides;
subtraction must preserve A-minus-B and the final source union. A 'mostly on one
side' shortcut is not sound when a reliably represented fragment exists on the
other side. Terminal contents may combine remaining brushes only when their
contents are constant throughout the terminal region; exhausting heuristic
candidate selection does not establish this condition.

Tolerance policies must account for numerical conditioning/scale and source
support rather than silently deleting positive thickness. Existing plane
identification, winding construction and float output impose finite limits:
nonzero mathematical volume alone does not prove representability. Uncertain
geometry must not be silently compiled as unbounded SOLID or declared invalid
solely by heuristic thickness. Output float planes must retain the separation
required by the accepted working representation.
