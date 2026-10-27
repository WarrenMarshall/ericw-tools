from pathlib import Path
p=Path('/tmp/qqbsp-p3/source/qbsp/brushbsp.cc')
s=Path('/tmp/qqbsp-phase2/rejected-brushbsp.cc').read_text()
s=s.replace('    const qplane3d &split = map.planes[planenum];','''    const qplane3d &split = map.planes[planenum];
    auto trace = [&](const char *stage) { fprintf(stderr, "TRACE %s %s plane=%zu n=%.12g,%.12g,%.12g d=%.12g sides=%zu\\n", __func__, stage, planenum, split.normal[0], split.normal[1], split.normal[2], split.dist, brush->sides.size()); };''')
s=s.replace('    if (d_front < side_epsilon)', '    fprintf(stderr, "EXTENT real volume=%d p=%zu front=%.12g back=%.12g\\n", node_volume, planenum, d_front, d_back);\n    if (d_front < side_epsilon)')
s=s.replace('    if (d_front < DIST_EPSILON)', '    fprintf(stderr, "EXTENT check p=%zu front=%.12g back=%.12g\\n", planenum, d_front, d_back);\n    if (d_front < DIST_EPSILON)')
s=s.replace('        w = w->clip_back(face.get_plane());','''        size_t oldsize = w->size();
        w = w->clip_back(face.get_plane());
        fprintf(stderr, "CLIP p=%zu by=%zu points=%zu->%zu\\n", planenum, face.planenum, oldsize, w ? w->size() : 0);''')
s=s.replace('    if (!w || WindingIsTiny(*w, edge_epsilon))', '    if (!w || WindingIsTiny(*w, edge_epsilon))')
s=s.replace(' { // the brush isn\'t really split',' { trace("tiny-or-null"); // the brush isn\'t really split')
s=s.replace('    if (!bestside) {\n        // this is a leaf node','''    if (!bestside) {
        fprintf(stderr, "LEAF level=%d brushes=%zu volume=%d\\n", level, brushes.size(), bool(node->volume));
        for (auto &b : brushes) for (auto &side : b->sides) fprintf(stderr, "REMAIN p=%zu w=%zu onnode=%d bevel=%d\\n", side.planenum, side.w.size(), side.onnode, side.bevel);
        // this is a leaf node''')
s=s.replace('    auto &plane = map.get_plane(bestplane);','    fprintf(stderr, "SELECT level=%d p=%zu brushes=%zu\\n", level, bestplane, brushes.size());\n    auto &plane = map.get_plane(bestplane);')
s=s.replace('        auto [front, back] = SplitBrush(in, side.planenum, std::nullopt);','''        fprintf(stderr, "SUBTRACT a=%p b=%p p=%zu\\n", (void*)a.get(), (void*)b.get(), side.planenum);
        auto [front, back] = SplitBrush(in, side.planenum, std::nullopt);
        fprintf(stderr, "SUBRESULT front=%d back=%d\\n", bool(front), bool(back));''')
p.write_text(s)
