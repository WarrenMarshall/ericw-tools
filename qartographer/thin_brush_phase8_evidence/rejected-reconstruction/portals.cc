/*
    Copyright (C) 1996-1997  Id Software, Inc.
    Copyright (C) 1997       Greg Lewis

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

    See file, 'COPYING', for details.
*/
// portals.c

#include <qbsp/brush.hh>
#include <qbsp/portals.hh>
#include <qbsp/supported_geometry.hh>

#include <qbsp/map.hh>
#include <qbsp/brushbsp.hh>
#include <qbsp/qbsp.hh>
#include <qbsp/outside.hh>
#include <qbsp/tree.hh>
#include <common/log.hh>
#include <atomic>
#include <fstream>
#include <unordered_map>
#include <nlohmann/json.hpp>
#include <common/prtfile.hh>

#include "tbb/task_group.h"
#include "common/vectorutils.hh"

contentflags_t ClusterContents(const node_t *node)
{
    /* Pass the leaf contents up the stack */
    if (auto *leafdata = node->get_leafdata())
        return leafdata->contents;

    auto *nodedata = node->get_nodedata();
    return ClusterContents(nodedata->children[0]).cluster_contents(ClusterContents(nodedata->children[1]));
}

/*
=============
Portal_VisFlood

Returns true if the portal is empty or translucent, allowing
the PVS calculation to see through it.
The nodes on either side of the portal may actually be clusters,
not leafs, so all contents should be ored together
=============
*/
bool Portal_VisFlood(const portal_t *p)
{
    if (!p->onnode) {
        return false; // to global outsideleaf
    }

    contentflags_t contents0 = ClusterContents(p->nodes[0]);
    contentflags_t contents1 = ClusterContents(p->nodes[1]);

    // Check per-game visibility
    return contentflags_t::portal_can_see_through(contents0, contents1);
}

/*
===============
Portal_EntityFlood

The entity flood determines which areas are
"outside" on the map, which are then filled in.
Flowing from side s to side !s
===============
*/
bool Portal_EntityFlood(const portal_t *p, int32_t s)
{
    if (!p->nodes[0]->is_leaf() || !p->nodes[1]->is_leaf()) {
        FError("Portal_EntityFlood: not a leaf");
    }

    // can never cross to a solid
    if (p->nodes[0]->get_leafdata()->contents.is_solid() || p->nodes[1]->get_leafdata()->contents.is_solid()) {
        return false;
    }

    // can flood through everything else
    return true;
}

/*
=============
AddPortalToNodes
=============
*/
static void AddPortalToNodes(portal_t *p, node_t *front, node_t *back)
{
    if (p->nodes[0] || p->nodes[1])
        FError("portal already included");

    p->nodes[0] = front;
    p->next[0] = front->portals;
    front->portals = p;

    p->nodes[1] = back;
    p->next[1] = back->portals;
    back->portals = p;
}

/*
================
MakeHeadnodePortals

The created portals will face the global outside_node
================
*/
std::list<buildportal_t> MakeHeadnodePortals(tree_t &tree)
{
    int i, j, n;
    std::array<buildportal_t, 6> portals{};
    qplane3d bplanes[6];

    // pad with some space so there will never be null volume leafs
    aabb3d bounds = tree.bounds.grow(SIDESPACE);

    tree.outside_node.make_leaf();
    tree.outside_node.get_leafdata()->contents = contentflags_t::make(EWT_VISCONTENTS_SOLID);
    tree.outside_node.portals = nullptr;

    // create 6 portals forming a cube around the bounds of the map.
    // these portals will have `outside_node` on one side, and headnode on the other.
    for (i = 0; i < 3; i++)
        for (j = 0; j < 2; j++) {
            n = j * 3 + i;

            auto &p = portals[n];

            qplane3d &pl = bplanes[n] = {};

            if (j) {
                pl.normal[i] = -1;
                pl.dist = -bounds[j][i];
            } else {
                pl.normal[i] = 1;
                pl.dist = bounds[j][i];
            }
            bool side = p.plane.set_plane(pl, true);

            p.winding = BaseWindingForPlane<winding_t>(pl);
            if (side) {
                p.nodes = {&tree.outside_node, tree.headnode};
            } else {
                p.nodes = {tree.headnode, &tree.outside_node};
            }
        }

    // clip the basewindings by all the other planes
    for (i = 0; i < 6; i++) {
        winding_t &w = portals[i].winding;

        for (j = 0; j < 6; j++) {
            if (j == i)
                continue;

            if (auto w2 = w.clip_front(bplanes[j], qbsp_options.epsilon.value(), true)) {
                w = std::move(*w2);
            } else {
                FError("portal winding clipped away");
            }
        }
    }

    for (auto &p : portals) for (auto &bound : bplanes) {
        p.supports.push_back(-bound);
    }

    // move into std::list
    return {std::make_move_iterator(portals.begin()), std::make_move_iterator(portals.end())};
}

//============================================================================

/*
================
BaseWindingForNode

Creates a winding from the given node plane, clipped by all parent nodes.
================
*/
static std::vector<qplane3d> NodeSupports(const node_t *node, std::vector<qplane3d> supports)
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
    return supported_geometry::portal_has_area(supports, plane);
}

static void RequirePortalWinding(std::optional<winding_t> &w, const qplane3d &plane,
    const std::vector<qplane3d> &supports)
{
    auto usable = [&]() {
        if (!w || supported_geometry::winding_rank(*w, plane) != supported_geometry::rank_t::area) return false;
        for (auto &point : *w) {
            if (!supported_geometry::boundary_residual_ok(point, plane, true)) return false;
            for (auto &bound : supports)
                if (!supported_geometry::boundary_residual_ok(point, bound, false)) return false;
        }
        return true;
    };
    if (usable()) return;
    w = supported_geometry::reconstruct_boundary(plane, supports, qbsp_options.worldextent.value());
    if (!usable()) w = supported_geometry::reconstruct_section(plane,supports);
    if (!usable())
        Error("PHASE8 UNREPRESENTABLE_PORTAL: certified area section cannot be constructed against retained supports");
}

constexpr double BASE_WINDING_EPSILON = 0;
constexpr double SPLIT_WINDING_EPSILON = 0;

static std::optional<winding_t> BaseWindingForNode(const node_t *node)
{
    std::optional<winding_t> w = BaseWindingForPlane<winding_t>(node->get_nodedata()->get_plane());

    // clip by all the parents
    for (auto *np = node->parent; np && w;) {

        if (np->get_nodedata()->children[0] == node) {
            w = w->clip_front(np->get_nodedata()->get_plane().get_plane(), BASE_WINDING_EPSILON, false);
        } else {
            w = w->clip_back(np->get_nodedata()->get_plane().get_plane(), BASE_WINDING_EPSILON, false);
        }

        node = np;
        np = np->parent;
    }

    return w;
}

/*
==================
MakeNodePortal

create the new portal by taking the full plane winding for the cutting plane
and clipping it by all of parents of this node, as well as all the other
portals in the node.
==================
*/
static std::optional<buildportal_t> MakeNodePortal(
    node_t *node, const std::list<buildportal_t> &boundary_portals, portalstats_t &stats, const std::vector<qplane3d> &root_supports)
{
    auto supports = NodeSupports(node, root_supports);
    if (!PortalHasArea(supports, node->get_nodedata()->get_plane())) {
        stats.c_tinyportals++;
        return std::nullopt;
    }
    auto w = BaseWindingForNode(node);

    // clip the portal by all the other portals in the node
    for (auto &p : boundary_portals) {
        if (!w) {
            break;
        }
        qplane3d plane;

        if (p.nodes[0] == node) {
            plane = p.plane;
        } else if (p.nodes[1] == node) {
            plane = -p.plane;
        } else {
            Error("CutNodePortals_r: mislinked portal");
        }

        // fixme-brushbsp: magic number
        w = w->clip_front(plane, 0, false);
    }

    // Realization may wait for incident leaf occupancy. Supports remain authoritative.

    auto *nodedata = node->get_nodedata();

    buildportal_t new_portal{};
    new_portal.supports = std::move(supports);
    new_portal.plane = nodedata->get_plane();
    new_portal.onnode = node;
    new_portal.winding = w ? std::move(*w) : winding_t{};
    new_portal.nodes = nodedata->children;
    return std::move(new_portal);
}

/*
==============
SplitNodePortals

Move or split the portals that bound node so that the node's
children have portals instead of node.
==============
*/
static twosided<std::list<buildportal_t>> SplitNodePortals(
    const node_t *node, std::list<buildportal_t> boundary_portals, portalstats_t &stats)
{
    auto *nodedata = node->get_nodedata();

    const auto &plane = nodedata->get_plane();
    node_t *f = nodedata->children[0];
    node_t *b = nodedata->children[1];

    twosided<std::list<buildportal_t>> result;

    for (auto &p : boundary_portals) {
        // which side of p `node` is on
        planeside_t side;
        if (p.nodes[SIDE_FRONT] == node)
            side = SIDE_FRONT;
        else if (p.nodes[SIDE_BACK] == node)
            side = SIDE_BACK;
        else
            FError("CutNodePortals_r: mislinked portal");

        node_t *other_node = p.nodes[!side];
        p.nodes = {nullptr, nullptr};

        //
        // cut the portal into two portals, one on each side of the cut plane
        //
        auto [frontwinding, backwinding] = p.winding.clip(plane, SPLIT_WINDING_EPSILON, true);

        auto front_supports = p.supports, back_supports = p.supports;
        front_supports.push_back(-plane.get_plane());
        back_supports.push_back(plane.get_plane());
        const bool front_area = PortalHasArea(front_supports, p.plane);
        const bool back_area = PortalHasArea(back_supports, p.plane);
        if (!front_area) { frontwinding = {}; stats.c_tinyportals++; }
        if (!back_area) { backwinding = {}; stats.c_tinyportals++; }

        if (!front_area && !back_area) { // tiny windings on both sides
            continue;
        }

        if (!front_area) {
            p.supports = std::move(back_supports);
            p.winding = backwinding ? std::move(*backwinding) : winding_t{};
            if (side == SIDE_FRONT)
                p.nodes = {b, other_node};
            else
                p.nodes = {other_node, b};

            result.back.push_back(std::move(p));
            continue;
        }
        if (!back_area) {
            p.supports = std::move(front_supports);
            p.winding = frontwinding ? std::move(*frontwinding) : winding_t{};
            if (side == SIDE_FRONT)
                p.nodes = {f, other_node};
            else
                p.nodes = {other_node, f};

            result.front.push_back(std::move(p));
            continue;
        }

        // the winding is split
        buildportal_t new_portal{};
        new_portal.supports = std::move(back_supports);
        p.supports = std::move(front_supports);
        new_portal.plane = p.plane;
        new_portal.onnode = p.onnode;
        new_portal.nodes[0] = p.nodes[0];
        new_portal.nodes[1] = p.nodes[1];
        new_portal.winding = backwinding ? std::move(*backwinding) : winding_t{};
        p.winding = frontwinding ? std::move(*frontwinding) : winding_t{};

        if (side == SIDE_FRONT) {
            p.nodes = {f, other_node};
            new_portal.nodes = {b, other_node};
        } else {
            p.nodes = {other_node, f};
            new_portal.nodes = {other_node, b};
        }

        result.front.push_back(std::move(p));
        result.back.push_back(std::move(new_portal));
    }

    return result;
}

/*
================
MakePortalsFromBuildportals
================
*/
static void CheckPortalRegion(const buildportal_t &portal, const node_t *node)
{
    for (auto *parent = node->parent; parent; node = parent, parent = parent->parent) {
        const auto *data = parent->get_nodedata();
        qplane3d support = data->get_plane();
        if (data->children[0] == node) support = -support;
        for (auto &point : portal.winding) {
            if (!supported_geometry::boundary_residual_ok(point, support, false))
                Error("PHASE7 UNCERTIFIED_PORTAL support={}: winding outside incident region", data->planenum);
        }
    }
}

void MakePortalsFromBuildportals(tree_t &tree, std::list<buildportal_t> &buildportals, bool collision_connectivity_only)
{
    tree.portals.reserve(buildportals.size());
    std::vector<buildportal_t *> accepted, deferred;
    auto empty = [](const node_t *node) {
        return node->is_leaf() && node->get_leafdata()->contents.is_empty();
    };

    for (auto &buildportal : buildportals) {
        // Internal SOLID/SOLID incidence cannot expose a face or carry an EMPTY
        // connection. Leaf occupancy is certified by the construction pipeline;
        // retain the leaves and collision BSP, omit only this derived portal.
        if (buildportal.nodes[0]->is_leaf() && buildportal.nodes[1]->is_leaf() &&
            buildportal.nodes[0]->get_leafdata()->contents.is_solid() &&
            buildportal.nodes[1]->get_leafdata()->contents.is_solid()) continue;
        auto supports = NodeSupports(buildportal.nodes[0], buildportal.supports);
        supports = NodeSupports(buildportal.nodes[1], std::move(supports));
        std::optional<winding_t> prepared = std::move(buildportal.winding);
        try {
            RequirePortalWinding(prepared, buildportal.plane, supports);
        } catch (const std::runtime_error &) {
            if (const char *path = std::getenv("QQBSP_PHASE7_CAPTURE")) {
                nlohmann::json capture;
                capture["query"] = supported_geometry::coefficients(buildportal.plane);
                capture["planes"] = nlohmann::json::array();
                for (auto &p : supports) capture["planes"].push_back(supported_geometry::coefficients(p));
                capture["nodes"] = nlohmann::json::array();
                for (auto *node : buildportal.nodes) {
                    nlohmann::json record;
                    record["contents"] = ClusterContents(node).to_string();
                    record["ancestors"] = nlohmann::json::array();
                    for (auto &p : NodeSupports(node, {})) record["ancestors"].push_back(supported_geometry::coefficients(p));
                    record["contributors"] = nlohmann::json::array();
                    if (auto *leaf = node->get_leafdata()) for (auto *brush : leaf->original_brushes) {
                        nlohmann::json source;
                        source["source"] = brush->mapbrush ? fmt::format("{}",brush->mapbrush->line) : "synthetic";
                        source["contents"] = brush->contents.to_string();
                        source["planes"] = nlohmann::json::array();
                        for (auto &side : brush->sides) source["planes"].push_back(supported_geometry::coefficients(side.get_plane()));
                        record["contributors"].push_back(std::move(source));
                    }
                    capture["nodes"].push_back(std::move(record));
                }
                std::ofstream(std::string(path)+".portal.json") << capture.dump(2) << '\n';
            }
            if (!collision_connectivity_only || !empty(buildportal.nodes[0]) || !empty(buildportal.nodes[1])) throw;
            deferred.push_back(&buildportal);
            continue;
        }
        accepted.push_back(&buildportal);
        buildportal.winding = std::move(*prepared);
        CheckPortalRegion(buildportal, buildportal.nodes[0]);
        CheckPortalRegion(buildportal, buildportal.nodes[1]);
        portal_t *new_portal = tree.create_portal();
        new_portal->plane = buildportal.plane;
        new_portal->onnode = buildportal.onnode;
        new_portal->winding = std::move(buildportal.winding);
        AddPortalToNodes(new_portal, buildportal.nodes[0], buildportal.nodes[1]);
    }
    if (deferred.empty()) return;
    // This graph is used only for collision-hull outside filling, never VIS or
    // rendering. An alternative chain of target-representable EMPTY ports proves
    // that removing an unconstructible redundant edge preserves all reachability.
    std::unordered_map<const node_t *, std::vector<const node_t *>> graph;
    std::unordered_map<const node_t *, std::vector<std::pair<const node_t *, buildportal_t *>>> proof_graph;

    auto target_planes = [](const std::vector<qplane3d> &planes) {
        std::vector<p6::Plane> result;
        for (auto &p : planes) {
            auto q = supported_geometry::coefficients(p);
            for (double &v : q) v = static_cast<float>(v);
            result.push_back(q);
        }
        return result;
    };
    for (auto *p : accepted) {
        if (!empty(p->nodes[0]) || !empty(p->nodes[1])) continue;
        auto supports = NodeSupports(p->nodes[1], NodeSupports(p->nodes[0], p->supports));
        auto region = target_planes(supports);
        auto q = supported_geometry::coefficients(p->plane);
        for (double &v : q) v = static_cast<float>(v);
        region.push_back(q); region.push_back(p6::opposite(q));
        if (supported_geometry::dimension(region) != 2) continue;
        bool volumetric = p->supports.size() >= 6;
        for (auto *node : p->nodes) {
            std::vector<qplane3d> root(p->supports.begin(), p->supports.begin()+std::min(size_t(6),p->supports.size()));
            volumetric &= supported_geometry::dimension(target_planes(NodeSupports(node, std::move(root)))) == 3;
        }
        if (!volumetric) continue;
        graph[p->nodes[0]].push_back(p->nodes[1]);
        graph[p->nodes[1]].push_back(p->nodes[0]);
        proof_graph[p->nodes[0]].push_back({p->nodes[1],p});
        proof_graph[p->nodes[1]].push_back({p->nodes[0],p});
    }
    for (auto *p : deferred) {
        std::vector<const node_t *> pending{p->nodes[0]};
        std::unordered_map<const node_t *, const node_t *> predecessor{{p->nodes[0],nullptr}};
        for (size_t i=0; i<pending.size() && !predecessor.count(p->nodes[1]); ++i)
            for (auto *next : graph[pending[i]])
                if (predecessor.emplace(next,pending[i]).second) pending.push_back(next);
        if (!predecessor.count(p->nodes[1])) {
            if (const char *path = std::getenv("QQBSP_PHASE7_CAPTURE")) {
                nlohmann::json failure;
                failure["query"] = supported_geometry::coefficients(p->plane);
                failure["planes"] = nlohmann::json::array();
                for (auto &bound : NodeSupports(p->nodes[1],NodeSupports(p->nodes[0],p->supports)))
                    failure["planes"].push_back(supported_geometry::coefficients(bound));
                failure["certified_graph_vertices"] = graph.size();
                failure["reachable_vertices"] = predecessor.size();
                std::ofstream(std::string(path)+".no-route.json") << failure.dump(2) << '\n';
            }
            Error("PHASE8 CONSTRUCTION_UNSUPPORTED: EMPTY portal has no certified target-representable alternative route");
        }
        size_t length = 0;
        nlohmann::json proof;
        proof["omitted_plane"] = supported_geometry::coefficients(p->plane);
        proof["purpose"] = "collision filling only; unchanged EMPTY reachability; never rendering/VIS";
        proof["omitted_regions"] = nlohmann::json::array();
        for (auto *node : p->nodes) {
            nlohmann::json region = nlohmann::json::array();
            std::vector<qplane3d> root(p->supports.begin(),p->supports.begin()+6);
            for (auto &bound : NodeSupports(node,std::move(root))) region.push_back(supported_geometry::coefficients(bound));
            proof["omitted_regions"].push_back(std::move(region));
        }
        proof["path"] = nlohmann::json::array();
        for (const node_t *n=p->nodes[1]; predecessor[n]; n=predecessor[n]) {
            ++length;
            auto &edges = proof_graph[n];
            auto *edge = std::find_if(edges.begin(),edges.end(),[&](auto &e) { return e.first == predecessor[n]; })->second;
            nlohmann::json record;
            record["query"] = supported_geometry::coefficients(edge->plane);
            record["planes"] = nlohmann::json::array();
            for (auto &bound : NodeSupports(edge->nodes[1],NodeSupports(edge->nodes[0],edge->supports)))
                record["planes"].push_back(supported_geometry::coefficients(bound));
            record["incident_regions"] = nlohmann::json::array();
            for (auto *node : edge->nodes) {
                nlohmann::json region = nlohmann::json::array();
                std::vector<qplane3d> root(edge->supports.begin(),edge->supports.begin()+6);
                for (auto &bound : NodeSupports(node,std::move(root))) region.push_back(supported_geometry::coefficients(bound));
                record["incident_regions"].push_back(std::move(region));
            }
            proof["path"].push_back(std::move(record));
        }
        if (const char *path = std::getenv("QQBSP_PHASE7_CAPTURE"))
            std::ofstream(std::string(path)+".portal-proofs.jsonl",std::ios::app) << proof.dump() << '\n';
        logging::print("PHASE8 CERTIFIED_REDUNDANT_COLLISION_PORTAL plane={} alternative_edges={}\n",p->plane.get_plane(),length);
    }

}

/*
================
CalcNodeBounds
================
*/
inline void CalcNodeBounds(node_t *node)
{
    // calc mins/maxs for both leafs and nodes
    node->bounds = aabb3d{};

    for (portal_t *p = node->portals; p;) {
        int s = (p->nodes[1] == node);
        for (auto &point : p->winding) {
            node->bounds += point;
        }
        p = p->next[s];
    }
}

static void CalcTreeBounds_r(node_t *node, logging::percent_clock &clock)
{
    if (node->is_leaf()) {
        clock();
        CalcNodeBounds(node);
    } else {
        auto *nodedata = node->get_nodedata();

        tbb::task_group g;
        g.run([&]() { CalcTreeBounds_r(nodedata->children[0], clock); });
        g.run([&]() { CalcTreeBounds_r(nodedata->children[1], clock); });
        g.wait();

        node->bounds = nodedata->children[0]->bounds + nodedata->children[1]->bounds;
    }

    if (node->bounds.mins()[0] >= node->bounds.maxs()[0]) {
        // logging::print("WARNING: {} without a volume\n", node->is_leaf ? "leaf" : "node");

        // fixme-brushbsp: added this to work around leafs with no portals showing up in "qbspfeatures.map" among other
        // test maps. Not sure if correct or there's another underlying problem.
        node->bounds = {node->parent->bounds.mins(), node->parent->bounds.mins()};
    }

    for (auto &v : node->bounds.mins()) {
        if (fabs(v) > qbsp_options.worldextent.value()) {
            logging::print("WARNING: {} with unbounded volume\n", node->is_leaf() ? "leaf" : "node");
            break;
        }
    }
}

/*
==================
ClipNodePortalToTree_r

Given portals which are connected to `node` on one side,
descends the tree, splitting the portals as needed until they are connected to leaf nodes.

The other side of the portals will remain untouched.
==================
*/
static std::list<buildportal_t> ClipNodePortalsToTree_r(
    node_t *node, portaltype_t type, std::list<buildportal_t> portals, portalstats_t &stats)
{
    if (portals.empty()) {
        return portals;
    }
    if (node->is_leaf() || (type == portaltype_t::VIS && node->get_nodedata()->detail_separator)) {
        return portals;
    }
    auto *nodedata = node->get_nodedata();

    auto boundary_portals_split = SplitNodePortals(node, std::move(portals), stats);

    auto front_fragments =
        ClipNodePortalsToTree_r(nodedata->children[0], type, std::move(boundary_portals_split.front), stats);
    auto back_fragments =
        ClipNodePortalsToTree_r(nodedata->children[1], type, std::move(boundary_portals_split.back), stats);

    std::list<buildportal_t> merged_result = std::move(front_fragments);
    merged_result.splice(merged_result.end(), back_fragments);
    return merged_result;
}

/*
==================
MakeTreePortals_r

Given the list of portals bounding `node`, returns the portal list for a fully-portalized `node`.
==================
*/
std::list<buildportal_t> MakeTreePortals_r(node_t *node, portaltype_t type, std::list<buildportal_t> boundary_portals,
    portalstats_t &stats, logging::percent_clock &clock, const std::vector<qplane3d> &root_supports)
{
    clock();

    if (node->is_leaf() || (type == portaltype_t::VIS && node->get_nodedata()->detail_separator)) {
        return boundary_portals;
    }

    // make the node portal before we move out the boundary_portals
    std::optional<buildportal_t> nodeportal = MakeNodePortal(node, boundary_portals, stats, root_supports);

    // parallel part: split boundary_portals between the front and back, and obtain the fully
    // portalized front/back sides in parallel

    auto boundary_portals_split = SplitNodePortals(node, std::move(boundary_portals), stats);

    std::list<buildportal_t> result_portals_front, result_portals_back;

    auto *nodedata = node->get_nodedata();

    tbb::task_group g;
    g.run([&]() {
        result_portals_front =
            MakeTreePortals_r(nodedata->children[0], type, std::move(boundary_portals_split.front), stats, clock, root_supports);
    });
    g.run([&]() {
        result_portals_back =
            MakeTreePortals_r(nodedata->children[1], type, std::move(boundary_portals_split.back), stats, clock, root_supports);
    });
    g.wait();

    // sequential part: push the nodeportal down each side of the bsp so it connects leafs

    std::list<buildportal_t> result_portals_onnode;

    if (nodeportal) {
        // to start with, `nodeportal` is a portal between node->children[0] and node->children[1]

        // these portal fragments have node->children[1] on one side, and the leaf nodes from
        // node->children[0] on the other side
        std::list<buildportal_t> half_clipped =
            ClipNodePortalsToTree_r(nodedata->children[0], type, make_list(std::move(*nodeportal)), stats);

        result_portals_onnode = ClipNodePortalsToTree_r(nodedata->children[1], type, std::move(half_clipped), stats);
    }

    // all done, merge together the lists and return
    std::list<buildportal_t> merged_result = std::move(result_portals_front);
    merged_result.splice(merged_result.end(), result_portals_back);
    merged_result.splice(merged_result.end(), result_portals_onnode);
    return merged_result;
}

/*
==================
MakeTreePortals
==================
*/
void MakeTreePortals(tree_t &tree, bool collision_connectivity_only)
{
    logging::funcheader();

    FreeTreePortals(tree);

    auto headnodeportals = MakeHeadnodePortals(tree);
    auto root_supports = headnodeportals.front().supports;

    {
        logging::percent_clock clock(tree.nodes.size());

        portalstats_t stats{};

        auto buildportals =
            MakeTreePortals_r(tree.headnode, portaltype_t::TREE, std::move(headnodeportals), stats, clock, root_supports);

        MakePortalsFromBuildportals(tree, buildportals, collision_connectivity_only);
    }

    logging::header("CalcTreeBounds");

    logging::percent_clock clock;
    CalcTreeBounds_r(tree.headnode, clock);
    clock.print();

    struct tree_portal_stats_t : logging::stat_tracker_t
    {
        stat &portals = register_stat("tree portals");
    } stats;

    stats.portals.count = tree.portals.size();
    tree.portaltype = portaltype_t::TREE;
}

/*
=========================================================

FLOOD AREAS

=========================================================
*/

static void ApplyArea_r(node_t *node)
{
    if (auto *nodedata = node->get_nodedata()) {
        ApplyArea_r(nodedata->children[0]);
        ApplyArea_r(nodedata->children[1]);
        return;
    }

    node->get_leafdata()->area = map.c_areas;
}

static mapentity_t *AreanodeEntityForLeaf(node_t *node)
{
    // if detail cluster, search the children recursively
    if (auto *nodedata = node->get_nodedata()) {
        if (auto *child0result = AreanodeEntityForLeaf(nodedata->children[0]); child0result) {
            return child0result;
        }
        return AreanodeEntityForLeaf(nodedata->children[1]);
    }

    auto *leafdata = node->get_leafdata();
    for (auto &brush : leafdata->original_brushes) {
        if (brush->mapbrush->func_areaportal) {
            return brush->mapbrush->func_areaportal;
        }
    }
    return nullptr;
}

/*
=============
FloodAreas_r
=============
*/
static void FloodAreas_r(node_t *node)
{
    auto *leafdata = node->get_leafdata();
    Q_assert(leafdata);

    if (leafdata->contents.flags & EWT_INVISCONTENTS_AREAPORTAL) {
        // grab the func_areanode entity
        mapentity_t *entity = AreanodeEntityForLeaf(node);

        if (entity == nullptr) {
            logging::print("WARNING: areaportal contents in node, but no entity found {} -> {}\n", node->bounds.mins(),
                node->bounds.maxs());
            return;
        }

        // this node is part of an area portal;
        // if the current area has allready touched this
        // portal, we are done
        if (entity->portalareas[0] == map.c_areas || entity->portalareas[1] == map.c_areas)
            return;

        // note the current area as bounding the portal
        if (entity->portalareas[1]) {
            logging::print("WARNING: {}: areaportal touches > 2 areas\n  Entity Bounds: {} -> {}\n", entity->location,
                entity->bounds.mins(), entity->bounds.maxs());
            return;
        }

        if (entity->portalareas[0])
            entity->portalareas[1] = map.c_areas;
        else
            entity->portalareas[0] = map.c_areas;

        return;
    }

    if (leafdata->area)
        return; // already got it

    leafdata->area = map.c_areas;

    // propagate area assignment to descendants if we're a cluster
    // (unnecessary because we did a full tree portalization)
#if 0
    if (!node->is_leaf()) {
        ApplyArea_r(node);
    }
#endif

    int32_t s;

    for (portal_t *p = node->portals; p; p = p->next[s]) {
        s = (p->nodes[1] == node);
#if 0
		if (p->nodes[!s]->occupied)
			continue;
#endif
        if (!Portal_EntityFlood(p, s))
            continue;

        FloodAreas_r(p->nodes[!s]);
    }
}

/*
=============
FindAreas_r

Just decend the tree, and for each node that hasn't had an
area set, flood fill out from there
=============
*/
static void FindAreas_r(node_t *node)
{
    if (auto *nodedata = node->get_nodedata()) {
        FindAreas_r(nodedata->children[0]);
        FindAreas_r(nodedata->children[1]);
        return;
    }

    auto *leafdata = node->get_leafdata();

    if (leafdata->area)
        return; // already got it

    if (leafdata->contents.is_any_solid())
        return;

    if (!leafdata->occupied)
        return; // not reachable from an entity

    // area portals are always only flooded into, never
    // out of
    if (leafdata->contents.flags & EWT_INVISCONTENTS_AREAPORTAL)
        return;

    map.c_areas++;
    FloodAreas_r(node);
}

/**
 * Starting at `a`, find and return the shortest path to `b`.
 *
 * Reference:
 * https://en.wikipedia.org/wiki/Breadth-first_search#Pseudocode
 */
static std::list<node_t *> FindShortestPath(node_t *a, node_t *b, const std::function<bool(portal_t *)> &passable)
{
    std::list<node_t *> queue;
    std::unordered_set<node_t *> queue_set;
    std::unordered_map<node_t *, node_t *> parent;

    queue.push_back(a);
    queue_set.insert(a);

    while (!queue.empty()) {
        node_t *node = queue.front();
        queue.pop_front();

        if (node == b) {
            // reached target. now we just need to extract the path we took from the `parent` map.
            std::list<node_t *> result;
            for (node_t *n = b;; n = parent.at(n)) {
                result.push_front(n);
                if (n == a)
                    break;
            }
            return result;
        }

        // push neighbouring nodes onto the back of the queue,
        // if they're not already enqueued, and if the portal is passable
        int side;
        for (portal_t *portal = node->portals; portal; portal = portal->next[!side]) {
            side = (portal->nodes[0] == node);

            node_t *neighbour = portal->nodes[side];

            if (!passable(portal))
                continue;
            if (queue_set.find(neighbour) != queue_set.end())
                continue;

            // enqueue it
            queue.push_back(neighbour);
            queue_set.insert(neighbour);
            parent[neighbour] = node;
        }
    }

    // couldn't find a path
    return {};
}

using exit_t = std::tuple<portal_t *, node_t *>;

static void FindAreaPortalExits_R(node_t *n, std::unordered_set<node_t *> &visited, std::vector<exit_t> &exits)
{
    Q_assert(n->is_leaf());

    visited.insert(n);

    int s;
    for (portal_t *p = n->portals; p; p = p->next[!s]) {
        s = (p->nodes[0] == n);

        node_t *neighbour = p->nodes[s];

        // already visited?
        if (visited.find(neighbour) != visited.end())
            continue;

        // is this an exit?
        if (!(neighbour->get_leafdata()->contents.flags & EWT_INVISCONTENTS_AREAPORTAL) &&
            !neighbour->get_leafdata()->contents.is_solid()) {
            exits.emplace_back(p, neighbour);
            continue;
        }

        // valid edge to explore?
        // if this isn't an exit, don't leave AREAPORTAL
        if (!(neighbour->get_leafdata()->contents.flags & EWT_INVISCONTENTS_AREAPORTAL))
            continue;

        // continue exploding
        FindAreaPortalExits_R(neighbour, visited, exits);
    }
}

/**
 * DFS to find all portals leading out of the Q2_CONTENTS_AREAPORTAL leaf `n`, into non-solid leafs.
 * Returns all of the portals and corresponding "outside" leafs.
 */
static std::vector<exit_t> FindAreaPortalExits(node_t *n)
{
    std::unordered_set<node_t *> visited;
    std::vector<exit_t> exits;

    FindAreaPortalExits_R(n, visited, exits);

    return exits;
}

/**
 * Attempts to write a leak line showing how the two sides of the areaportal are reachable.
 */
static void DebugAreaPortalBothSidesLeak(node_t *node)
{
    std::vector<exit_t> exits = FindAreaPortalExits(node);

    if (exits.size() < 2) {
        logging::funcprint("WARNING: only found {} exits\n", exits.size());
        return;
    }

    auto [exit_portal0, exit_leaf0] = exits[0];

    // look for the other exit `i`, such that the shortest path between exit 0 and `i` is the longest.
    // this is to avoid picking two exits on the same side of the areaportal, which would not help
    // track down the leak.
    size_t longest_length = 0;
    std::list<node_t *> longest_path;

    for (size_t i = 1; i < exits.size(); ++i) {
        auto [exit_portal_i, exit_leaf_i] = exits[i];

        auto path = FindShortestPath(exit_leaf0, exit_leaf_i, [](portal_t *p) -> bool {
            if (!Portal_EntityFlood(p, 0))
                return false;

            // don't go back into an areaportal
            if ((p->nodes[0]->get_leafdata()->contents.flags & EWT_INVISCONTENTS_AREAPORTAL) ||
                (p->nodes[1]->get_leafdata()->contents.flags & EWT_INVISCONTENTS_AREAPORTAL))
                return false;

            return true;
        });

        if (path.size() > longest_length) {
            longest_length = path.size();
            longest_path = path;
        }
    }

    // write `longest_path` as the leak

    fs::path name = qbsp_options.bsp_path;
    name.replace_extension(fmt::format("areaportal_leak{}.pts", map.numareaportal_leaks));

    std::ofstream ptsfile(name);

    if (!ptsfile)
        FError("Failed to open {}: {}", name, strerror(errno));

    for (auto it = longest_path.begin();; ++it) {
        if (it == longest_path.end())
            break;

        auto next_it = it;
        next_it++;

        if (next_it == longest_path.end())
            break;

        WriteLeakTrail(ptsfile, (*it)->bounds.centroid(), (*next_it)->bounds.centroid());
    }

    logging::print("Wrote areaportal leak to {}\n", name);

    ++map.numareaportal_leaks;
}

/*
=============
SetAreaPortalAreas_r

Just decend the tree, and for each node that hasn't had an
area set, flood fill out from there
=============
*/
static void SetAreaPortalAreas_r(node_t *node)
{
    if (auto *nodedata = node->get_nodedata()) {
        SetAreaPortalAreas_r(nodedata->children[0]);
        SetAreaPortalAreas_r(nodedata->children[1]);
        return;
    }

    auto *leafdata = node->get_leafdata();

    if (leafdata->contents.flags != EWT_INVISCONTENTS_AREAPORTAL)
        return;

    if (leafdata->area)
        return; // already set

    // grab the func_areanode entity
    mapentity_t *entity = AreanodeEntityForLeaf(node);

    if (!entity) {
        logging::print("WARNING: areaportal missing for node: {} -> {}\n", node->bounds.mins(), node->bounds.maxs());
        return;
    }

    leafdata->area = entity->portalareas[0];
    if (!entity->portalareas[1]) {
        if (!entity->wrote_doesnt_touch_two_areas_warning) {
            entity->wrote_doesnt_touch_two_areas_warning = true;
            logging::print(
                "WARNING: {}: areaportal entity {} with targetname {} doesn't touch two areas\n  Node bounds: {} -> {}\n",
                entity->location, entity - map.entities.data(), entity->epairs.get("targetname"), node->bounds.mins(),
                node->bounds.maxs());
            DebugAreaPortalBothSidesLeak(node);
        }
        return;
    }
}

/*
=============
EmitAreaPortals

Mark each leaf with an area, bounded by CONTENTS_AREAPORTAL and
emit them.
=============
*/
void EmitAreaPortals(tree_t &tree)
{
    Q_assert(tree.portaltype == portaltype_t::TREE);

    logging::funcheader();

    map.bsp.dareaportals.emplace_back();
    map.bsp.dareas.emplace_back();

    // don't do anything else if we've leaked
    if (map.leakfile || map.antiregions.size() || map.region) {

        map.bsp.dareas.emplace_back();

        for (auto &e : map.entities) {
            e.areaportalnum = 0;

            if (e.epairs.get("classname") == "func_areaportal") {
                e.epairs.remove("style");
            }
        }

        return;
    }

    FindAreas_r(tree.headnode);
    SetAreaPortalAreas_r(tree.headnode);

    for (size_t i = 1; i <= map.c_areas; i++) {
        darea_t &area = map.bsp.dareas.emplace_back();
        area.firstareaportal = map.bsp.dareaportals.size();

        for (auto &e : map.entities) {

            if (!e.areaportalnum)
                continue;
            dareaportal_t dp = {};

            if (e.portalareas[0] == i) {
                dp.portalnum = e.areaportalnum;
                dp.otherarea = e.portalareas[1];
            } else if (e.portalareas[1] == i) {
                dp.portalnum = e.areaportalnum;
                dp.otherarea = e.portalareas[0];
            }

            size_t j = 0;

            for (; j < map.bsp.dareaportals.size(); j++) {
                if (map.bsp.dareaportals[j] == dp)
                    break;
            }

            if (j == map.bsp.dareaportals.size())
                map.bsp.dareaportals.push_back(dp);
        }

        area.numareaportals = map.bsp.dareaportals.size() - area.firstareaportal;
    }

    logging::stat_tracker_t area_stats;
    area_stats.register_stat("areas").count += map.c_areas;
    area_stats.register_stat("area portals").count += map.bsp.dareaportals.size();
}

//==============================================================

struct visible_faces_stats_t : logging::stat_tracker_t
{
    stat &sides_not_found = register_stat("sides not found (use -verbose to display)", false, true);
    stat &sides_visible = register_stat("sides visible");

    std::vector<polylib::winding_t> missing_portal_sides;
};

/*
============
FindPortalSide

Finds a brush side to use for texturing the given portal
============
*/
static void FindPortalSide(portal_t *p, visible_faces_stats_t &stats)
{
    // decide which content change is strongest
    // solid > lava > water, etc

    // if either is "_noclipfaces" then we don't require a content change
    contentflags_t viscontents = contentflags_t::portal_visible_contents(
        p->nodes[0]->get_leafdata()->contents, p->nodes[1]->get_leafdata()->contents);
    if (viscontents.is_empty())
        return;

    // bestside[0] is the brushside visible on portal side[0] which is the positive side of the plane, always
    side_t *bestside[2] = {nullptr, nullptr};
    side_t *exactside[2] = {nullptr, nullptr};
    float bestdot = 0;
    const qbsp_plane_t &p1 = p->onnode->get_nodedata()->get_plane();

    // check brushes on both sides of the portal
    for (int j = 0; j < 2; j++) {
        node_t *n = p->nodes[j];

        // iterate the n->original_brushes vector in reverse order, so later brushes
        // in the map file order are prioritized
        for (auto it = n->get_leafdata()->original_brushes.rbegin(); it != n->get_leafdata()->original_brushes.rend();
            ++it) {
            auto *brush = *it;
            const bool generate_outside_face =
                contentflags_t::portal_generates_face(viscontents, brush->contents, SIDE_FRONT);
            const bool generate_inside_face =
                contentflags_t::portal_generates_face(viscontents, brush->contents, SIDE_BACK);

            if (!(generate_outside_face || generate_inside_face)) {
                continue;
            }

            for (auto &side : brush->sides) {
                if (side.bevel)
                    continue;

                if (p->winding.max_dist_off_plane(side.get_plane()) > 0.1) {
                    continue;
                }

                if ((side.planenum & ~1) == p->onnode->get_nodedata()->planenum) {
                    // exact match (undirectional)

                    // because the brush is on j of the positive plane, the brushside must be facing away from j
                    Q_assert((side.planenum & 1) == !j);

                    // see which way(s) we want to generate faces - we could be a brush on either side of
                    // the portal, generating either a outward face (common case) or an inward face (liquids) or both.
                    if (generate_outside_face) {
                        // since we are iterating the brushes from highest priority (last) to lowest, take the first
                        // exactside we find
                        if (!exactside[!j]) {
                            exactside[!j] = &side;
                        }
                    }
                    if (generate_inside_face) {
                        if (!exactside[j]) {
                            exactside[j] = &side;
                        }
                    }

                    break;
                }
                // see how close the match is
                const auto &p2 = side.get_positive_plane();
                double dot = qv::dot(p1.get_normal(), p2.get_normal());

                // HACK: both the node plane and side.get_positive_plane() are supposed to be "positive", but the
                // which would imply dot >= 0, but the meaning of "positive" is ambiguous on 45 degree planes.
                // so take the absolute value to work around that case (this is an undirectional test anyway).
                dot = std::fabs(dot);

                if (dot > bestdot) {
                    bestdot = dot;
                    if (generate_outside_face) {
                        bestside[!j] = &side;
                    }
                    if (generate_inside_face) {
                        bestside[j] = &side;
                    }
                }
            }
        }
    }

    // take exact sides over best sides
    for (int i = 0; i < 2; ++i) {
        if (exactside[i]) {
            bestside[i] = exactside[i];
        }
    }

    if (!bestside[0] && !bestside[1]) {
        stats.sides_not_found++;
        logging::print(logging::flag::VERBOSE, "couldn't find portal side at {}\n", p->winding.center());
        stats.missing_portal_sides.push_back(p->winding.clone());
    }

    p->sidefound = true;

    for (int i = 0; i < 2; ++i) {
        p->sides[i] = bestside[i];
    }
}

/*
===============
MarkVisibleSides_r

===============
*/
static void MarkVisibleSides_r(node_t *node, visible_faces_stats_t &stats)
{
    if (auto *nodedata = node->get_nodedata()) {
        MarkVisibleSides_r(nodedata->children[0], stats);
        MarkVisibleSides_r(nodedata->children[1], stats);
        return;
    }

    auto *leafdata = node->get_leafdata();

    // empty leafs are never boundary leafs
    if (leafdata->contents.is_empty())
        return;

    // see if there is a visible face
    int s;
    for (portal_t *p = node->portals; p; p = p->next[!s]) {
        s = (p->nodes[0] == node);
        if (!p->onnode)
            continue; // edge of world
        if (!p->sidefound) {
            FindPortalSide(p, stats);
        }
        for (int i = 0; i < 2; ++i) {
            if (p->sides[i] && p->sides[i]->source) {
                p->sides[i]->source->visible = true;
                stats.sides_visible++;
            }
        }
    }
}

/*
=============
MarkVisibleSides

=============
*/
void MarkVisibleSides(tree_t &tree, bspbrush_t::container &brushes)
{
    logging::funcheader();

    // clear all the visible flags
    MarkBrushSidesInvisible(brushes);

    visible_faces_stats_t stats;
    // set visible flags on the sides that are used by portals
    MarkVisibleSides_r(tree.headnode, stats);

    if (!stats.missing_portal_sides.empty() && qbsp_options.debug_missing_portal_sides.value()) {
        fs::path name = qbsp_options.bsp_path;
        name.replace_extension("missing_portal_sides.prt");
        WriteDebugPortals(stats.missing_portal_sides, name);
    }
}
