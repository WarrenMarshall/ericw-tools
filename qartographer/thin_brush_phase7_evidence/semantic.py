from pathlib import Path
s=Path('/tmp/qqbsp-phase7/source');p=s/'qbsp/brushbsp.cc';t=p.read_text().replace('#include <climits>','#include <climits>\n#include <nlohmann/json.hpp>\n#include <fstream>')
pos=t.index('static void LeafNode(')
t=t[:pos]+'''// Sufficient exact coverage certificate. Strict outside exists precisely when
// a full-dimensional node intersected with the opposite support is volumetric.
static bool CoversNode(const bspbrush_t &source, const bspbrush_t &region)
{
    for (auto &side : source.sides) {
        bool implied = false;
        for (auto &bound : region.sides) implied |= side.planenum == bound.planenum;
        if (implied) continue;
        auto outside = BrushSupports(region);
        outside.push_back(p6::opposite(supported_geometry::coefficients(side.get_plane())));
        if (supported_geometry::dimension(outside) == 3) return false;
    }
    return true;
}

static void CaptureResolution(const node_t *node, size_t partition,
    const bspbrush_t::container &sources, const std::string &failure)
{
    const char *path = std::getenv("QQBSP_PHASE7_CAPTURE");
    if (!path) return;
    nlohmann::json capture;
    capture["failure"] = failure;
    capture["partition_id"] = partition;
    capture["query"] = supported_geometry::coefficients(map.get_plane(partition));
    capture["node"] = BrushSupports(*node->volume);
    capture["sources"] = nlohmann::json::array();
    std::vector<const bspbrush_t *> seen;
    for (auto &b : sources) {
        auto *source = b->original_brush();
        if (std::find(seen.begin(),seen.end(),source) != seen.end()) continue;
        seen.push_back(source);
        capture["sources"].push_back({{"planes",BrushSupports(*source)},
            {"contents",fmt::format("{}",source->contents)},
            {"solid",source->contents.is_solid()},
            {"source",source->mapbrush ? fmt::format("{}",source->mapbrush->line) : "synthetic"}});
    }
    std::ofstream(path) << capture.dump(2) << '\\n';
}

'''+t[pos:]
t=t.replace('bspstats_t &stats, logging::percent_clock &clock)\n{\n    // find the best plane','bspstats_t &stats, logging::percent_clock &clock, const bspbrush_t::container &sources)\n{\n    // find the best plane',1)
a=t.index('    clock();\n\n    // this is a splitplane node',t.index('static void BuildTree_r'));b=t.index('    // allocate children before recursing',a)
t=t[:a]+'''    // Prepare both geometry and routing before publishing the node. If a
    // representation fails, only a complete-region coverage proof may remove it.
    size_t bestplane = bestside->planenum & ~1;
    std::array<bspbrush_t::container, 2> children;
    twosided<bspbrush_t::ptr> children_volumes;
    try {
        children_volumes = SupportedSplit(node->volume, bestplane);
        children = SplitBrushList(brushes, bestplane, stats);
    } catch (const std::exception &failure) {
        CaptureResolution(node,bestplane,sources,failure.what());
        for (auto &candidate : sources) {
            auto source = candidate->original_ptr ? candidate->original_ptr : candidate;
            if (!source->contents.is_solid() || !CoversNode(*source,*node->volume)) continue;
            // The whole node is SOLID: no traversable external connection or
            // separating empty interior exists. Ancestor/root boundaries stay.
            logging::print("PHASE7 CERTIFIED_CONSTANT_SOLID partition={} source={}\\n",
                bestplane, source->mapbrush ? fmt::format("{}",source->mapbrush->line) : "synthetic");
            stats.c_leafs++;
            LeafNode(node,{source},stats);
            clock();
            return;
        }
        throw;
    }

    clock();
    stats.c_nodes++;
    nodedata_t *nodedata = node->get_nodedata();
    nodedata->planenum = bestplane;
    auto &plane = map.get_plane(bestplane);

'''+t[b:]
t=t.replace('        auto children_volumes = SupportedSplit(std::move(node->volume), bestplane);\n','')
t=t.replace('std::move(children[0]), split_type, stats, clock);','std::move(children[0]), split_type, stats, clock, sources);').replace('std::move(children[1]), split_type, stats, clock);','std::move(children[1]), split_type, stats, clock, sources);')
t=t.replace('tree.headnode, brushlist, split_type, stats, clock);','tree.headnode, brushlist, split_type, stats, clock, brushlist);')
p.write_text(t)
