from pathlib import Path
s=Path('/tmp/qqbsp-phase7/source')
p=s/'include/qbsp/supported_geometry.hh'
t=p.read_text().replace('// Experimental Phase 5 predicates. This is not a production certificate.','// Experimental Phase 7: decisions use retained binary64 halfspaces.\n// Winding/residual helpers below validate approximate construction only.')
t=t.replace('#include <qbsp/winding.hh>','#include <qbsp/winding.hh>\n#include <qbsp/halfspace.hh>')
a=t.index('    qvec3d lo, hi;'); b=t.index('\n}\n',a)
t=t[:a]+'''    std::array<double,3> lo, hi;
    for (int i = 0; i < 3; ++i) {
        lo[i] = plane.normal[i] < 0 ? bounds.maxs()[i] : bounds.mins()[i];
        hi[i] = plane.normal[i] < 0 ? bounds.mins()[i] : bounds.maxs()[i];
    }
    p6::Stats stats;
    p6::Plane q{plane.normal[0],plane.normal[1],plane.normal[2],plane.dist};
    auto minimum = p6::point_side(q,lo,stats,p6::Mode::filtered);
    auto maximum = p6::point_side(q,hi,stats,p6::Mode::filtered);
    if (minimum && *minimum > 0) return 1;
    if (maximum && *maximum < 0) return 2;
    return 3;'''+t[b:]
t=t.replace('namespace supported_geometry {','''namespace supported_geometry {
inline p6::Plane coefficients(const qplane3d &p) { return {p.normal[0],p.normal[1],p.normal[2],p.dist}; }
// No caller may replace an unresolved result with SOLID/EMPTY or deletion.
inline p6::Result region(const std::vector<p6::Plane> &supports) {
    p6::Stats stats;
    return p6::analyze(supports, stats);
}
inline int dimension(const std::vector<p6::Plane> &supports) {
    auto r = region(supports);
    if (r.dimension == -2) throw std::runtime_error("PHASE7 NUMERICAL_UNCERTAINTY: " + r.reason);
    return r.dimension;
}
''')
p.write_text(t)
p=s/'qbsp/brushbsp.cc';t=p.read_text(); pos=t.index('static int TestBrushToPlanenum(')
t=t[:pos]+'''static std::vector<p6::Plane> BrushSupports(const bspbrush_t &brush)
{
    std::vector<p6::Plane> supports;
    for (const auto &side : brush.sides) supports.push_back(supported_geometry::coefficients(side.get_plane()));
    return supports;
}

// Classify closed children from supports, never from rounded boundary vertices.
// A full-dimensional parent has interior on a side iff that child has dimension 3.
static int SupportedSide(const bspbrush_t &brush, const qplane3d &plane)
{
    auto supports = BrushSupports(brush);
    auto q = supported_geometry::coefficients(plane);
    supports.push_back(p6::opposite(q));
    bool front = supported_geometry::dimension(supports) == 3;
    supports.back() = q;
    bool back = supported_geometry::dimension(supports) == 3;
    if (!front && !back) Error("PHASE7 INVALID_REGION: no positive-volume child");
    return (front ? PSIDE_FRONT : 0) | (back ? PSIDE_BACK : 0);
}

'''+t[pos:]
t=t.replace('int s = BoxOnPlaneSide(brush.bounds, plane);\n    if (s != PSIDE_BOTH)', 'int s = SupportedSide(brush, plane);\n    if (s != PSIDE_BOTH)')
a=t.index('    // Sufficient constancy proof:');b=t.index('\n    leafnode->make_leaf();',a)
t=t[:a]+'''    // Sufficient proof for each contents contributor: the entire convex node
    // satisfies every fragment support. Union-only coverage remains diagnostic.
    for (auto &brush : brushes) {
        if (!leafnode->volume) Error("PHASE7 UNCERTIFIED_OCCUPANCY: missing node region");
        for (auto &support : brush->sides) {
            bool implied = false;
            for (auto &bound : leafnode->volume->sides) implied |= bound.planenum == support.planenum;
            if (implied) continue;
            auto outside = BrushSupports(*leafnode->volume);
            outside.push_back(p6::opposite(supported_geometry::coefficients(support.get_plane())));
            if (supported_geometry::dimension(outside) == 3)
                Error("PHASE7 UNCERTIFIED_OCCUPANCY support={}: contributor does not cover complete node", support.planenum);
        }
    }
'''+t[b:]
a=t.index('    brush = SupportedBoundary(std::move(brush), planenum);');b=t.index('    // create a new winding',a)
t=t[:a]+'''    int side = SupportedSide(*brush, split);
    if (side == PSIDE_BACK) { result.back = std::move(brush); return result; }
    if (side == PSIDE_FRONT) { result.front = std::move(brush); return result; }
    brush = SupportedBoundary(std::move(brush), planenum);

'''+t[b:]
a=t.index('    auto children = SupportedSplit(brush, planenum);');b=t.index('\n}',a)
t=t[:a]+'''    return SupportedSide(*brush, map.get_plane(planenum)) == PSIDE_BOTH;'''+t[b:]
t=t.replace('PHASE5','PHASE7')
t=t.replace('two resolved extents but cut has no resolved rank-2 winding','UNREPRESENTABLE_BOUNDARY: support-certified positive children, approximate cap unavailable; semantic simplification not certified')
p.write_text(t)
p=s/'qbsp/CMakeLists.txt';t=p.read_text().replace('phase5','phase7');t=t.replace('add_library(libqbsp STATIC ${QBSP_SOURCES})','''add_library(libqbsp STATIC ${QBSP_SOURCES})
find_library(QQBSP_GMP gmp REQUIRED)
find_library(QQBSP_GMPXX gmpxx REQUIRED)
target_compile_options(libqbsp PRIVATE -fno-fast-math -ffp-contract=off)
target_link_libraries(libqbsp ${QQBSP_GMPXX} ${QQBSP_GMP})''');p.write_text(t)
p=s/'tests/test_qbsp.cc';t=p.read_text().replace('/tmp/qqbsp-phase5/source','/tmp/qqbsp-phase7/source');p.write_text(t)
