from pathlib import Path
s=Path('/tmp/qqbsp-phase7/source')
p=s/'include/qbsp/portals.hh';t=p.read_text().replace('    winding_t winding;\n};\n\nstruct portalstats_t', '''    winding_t winding;
    // Defining supports survive disappearance/rounding of winding vertices.
    std::vector<qplane3d> supports;
    std::vector<qplane3d> root_supports;
};

struct portalstats_t''');p.write_text(t)
p=s/'qbsp/portals.cc';t=p.read_text();t=t.replace('    // move into std::list','''    for (auto &p : portals) for (auto &bound : bplanes) {
        p.supports.push_back(-bound);
        p.root_supports.push_back(-bound);
    }

    // move into std::list''',1)
a=t.index('static bool PortalHasArea(');b=t.index('constexpr double BASE_WINDING_EPSILON',a)
t=t[:a]+'''static std::vector<qplane3d> NodeSupports(const node_t *node, std::vector<qplane3d> supports)
{
    for (auto *parent = node->parent; parent; node = parent, parent = parent->parent) {
        auto *data = parent->get_nodedata();
        qplane3d p = data->get_plane();
        supports.push_back(data->children[0] == node ? -p : p);
    }
    return supports;
}

static bool PortalHasArea(const std::vector<qplane3d> &supports, const qplane3d &plane)
{
    std::vector<p6::Plane> region;
    for (auto &p : supports) region.push_back(supported_geometry::coefficients(p));
    auto q = supported_geometry::coefficients(plane);
    region.push_back(q); region.push_back(p6::opposite(q));
    return supported_geometry::dimension(region) == 2;
}

static void RequirePortalWinding(const std::optional<winding_t> &w, const qplane3d &plane)
{
    if (!w || supported_geometry::winding_rank(*w, plane) != supported_geometry::rank_t::area)
        Error("PHASE7 UNREPRESENTABLE_PORTAL: certified area section has no usable winding");
}

'''+t[b:]
t=t.replace('    auto w = BaseWindingForNode(node);','''    if (boundary_portals.empty()) Error("PHASE7 UNCERTIFIED_PORTAL: missing root boundary");
    auto supports = NodeSupports(node, boundary_portals.front().root_supports);
    if (!PortalHasArea(supports, node->get_nodedata()->get_plane())) {
        stats.c_tinyportals++;
        return std::nullopt;
    }
    auto w = BaseWindingForNode(node);''',1)
a=t.index('    if (!w) {\n        return std::nullopt;',t.index('static std::optional<buildportal_t> MakeNodePortal'));b=t.index('    auto *nodedata = node->get_nodedata();',a)
t=t[:a]+'''    RequirePortalWinding(w, node->get_nodedata()->get_plane());

'''+t[b:]
t=t.replace('    new_portal.plane = nodedata->get_plane();','''    new_portal.supports = std::move(supports);
    new_portal.root_supports = boundary_portals.front().root_supports;
    new_portal.plane = nodedata->get_plane();''',1)
a=t.index('        if (frontwinding && !PortalHasArea');b=t.index('        if (!frontwinding && !backwinding)',a)
t=t[:a]+'''        auto front_supports = p.supports, back_supports = p.supports;
        front_supports.push_back(-plane.get_plane());
        back_supports.push_back(plane.get_plane());
        if (!PortalHasArea(front_supports, p.plane)) {
            frontwinding = {}; stats.c_tinyportals++;
        } else RequirePortalWinding(frontwinding, p.plane);
        if (!PortalHasArea(back_supports, p.plane)) {
            backwinding = {}; stats.c_tinyportals++;
        } else RequirePortalWinding(backwinding, p.plane);

'''+t[b:]
t=t.replace('            p.winding = std::move(*backwinding);','            p.supports = std::move(back_supports);\n            p.winding = std::move(*backwinding);',1)
t=t.replace('            p.winding = std::move(*frontwinding);','            p.supports = std::move(front_supports);\n            p.winding = std::move(*frontwinding);',1)
t=t.replace('        new_portal.plane = p.plane;','''        new_portal.supports = std::move(back_supports);
        new_portal.root_supports = p.root_supports;
        p.supports = std::move(front_supports);
        new_portal.plane = p.plane;''',1)
t=t.replace('PHASE5','PHASE7');p.write_text(t)
