from pathlib import Path
import json
s=Path('/tmp/qqbsp-phase7/source')
p=s/'qbsp/brushbsp.cc';t=p.read_text().replace('static int SupportedSide(', 'int SupportedBrushSide(').replace('SupportedSide(', 'SupportedBrushSide(');p.write_text(t)
p=s/'include/qbsp/brushbsp.hh';t=p.read_text()+'\n// Phase 7 shared support classifier; returns PSIDE_FRONT/BACK/BOTH bit mask.\nint SupportedBrushSide(const bspbrush_t &brush, const qplane3d &plane);\n';p.write_text(t)
p=s/'include/qbsp/supported_geometry.hh';t=p.read_text();mark='struct distance_t';idx=t.index(mark);t=t[:idx]+'''inline bool portal_has_area(const std::vector<qplane3d> &supports, const qplane3d &plane) {
    std::vector<p6::Plane> region;
    for (auto &p : supports) region.push_back(coefficients(p));
    auto q = coefficients(plane);
    region.push_back(q); region.push_back(p6::opposite(q));
    return dimension(region) == 2;
}
'''+t[idx:];p.write_text(t)
p=s/'qbsp/portals.cc';t=p.read_text();a=t.index('    std::vector<p6::Plane> region;',t.index('static bool PortalHasArea'));b=t.index('\n}',a);t=t[:a]+'    return supported_geometry::portal_has_area(supports, plane);'+t[b:];p.write_text(t)
cases=json.loads(Path('/tmp/qqbsp-phase7/phase6/cases.json').read_text())
cases=[c for c in cases if c['name'][0] in 'ABCDEF' and 'established' in c]
(s/'qartographer/phase7-cases.json').write_text(json.dumps(cases,indent=2))
p=s/'tests/test_qbsp.cc';t=p.read_text()+'''
TEST(phase7, FailureSiteSupportDecisions)
{
    std::ifstream file("/tmp/qqbsp-phase7/source/qartographer/phase7-cases.json");
    nlohmann::json cases; file >> cases;
    auto plane = [](auto p) { return qplane3d{{p[0].template get<double>(),p[1].template get<double>(),p[2].template get<double>()},p[3].template get<double>()}; };
    for (const auto &c : cases) {
        SCOPED_TRACE(c["name"].get<std::string>());
        Phase5Reset();
        auto brush = bspbrush_t::make_ptr();
        std::vector<qplane3d> supports;
        std::vector<p6::Plane> coefficients;
        for (auto p : c["planes"]) {
            supports.push_back(plane(p));
            coefficients.push_back(supported_geometry::coefficients(plane(p)));
            brush->sides.emplace_back().planenum = Phase5Plane(plane(p));
        }
        auto expected = c["established"];
        EXPECT_EQ(supported_geometry::dimension(coefficients), expected["dimension"].get<int>());
        if (!c.contains("query")) continue;
        auto q = plane(c["query"]);
        auto front = coefficients; front.push_back(p6::opposite(supported_geometry::coefficients(q)));
        auto back = coefficients; back.push_back(supported_geometry::coefficients(q));
        if (expected.contains("front_dimension"))
            EXPECT_EQ(supported_geometry::dimension(front), expected["front_dimension"].get<int>());
        if (expected.contains("section_dimension"))
            EXPECT_EQ(supported_geometry::portal_has_area(supports,q),expected["section_dimension"].get<int>()==2);
        if (expected["dimension"].get<int>() != 3) continue;
        int side = SupportedBrushSide(*brush,q);
        EXPECT_EQ(side, (supported_geometry::dimension(front)==3 ? 1:0) | (supported_geometry::dimension(back)==3 ? 2:0));
        if (c["name"].get<std::string>() == "E-p1-reduced") {
            // No windings at all: exact empty-child routing must precede construction.
            auto result = SupportedSplit(brush,Phase5Plane(q));
            EXPECT_FALSE(result.front); EXPECT_EQ(result.back,brush);
        }
    }
}
''';p.write_text(t)
print([(c['name'],c['established']) for c in cases])
