from pathlib import Path
p=Path('/tmp/qqbsp-phase4/source/qbsp/brushbsp.cc');s=p.read_text()
a=s.index('static bool CheckSplitBrush(');b=s.index('static int p4mask(const node_t *);',a)
t=s[a:b];t=t.replace('    const qplane3d &split = map.planes[planenum];','    const qplane3d &split = map.planes[planenum];\n    bool trace=p3world && p3pass==1 && p3path=="11100001101010100010110001000";')
t=t.replace('return false;', 'if(trace)logging::print("P4 CHECK rejection line={}\\n",__LINE__);return false;')
t=t.replace('        w = w->clip_back(face.get_plane(), DIST_EPSILON);','        if(trace)logging::print("P4 CLIP plane={} before={}\\n",face.planenum,w->size());\n        w = w->clip_back(face.get_plane(), DIST_EPSILON);\n        if(trace)logging::print("P4 CLIPPED after={} area={}\\n",w?w->size():0,w?w->area():0);')
s=s[:a]+t+s[b:]
s=s.replace('    stats.leafstats.count_contents_in_stats(leafdata->contents);',r'''    if(p3world){std::ofstream f(qbsp_options.bsp_path.string()+".p4-contents.tsv",std::ios::app);f<<p3pass<<"\t"<<p3nodepath(leafnode)<<"\t"<<leafdata->contents.is_any_solid()<<"\t"<<leafdata->contents.is_sky()<<"\n";}
    stats.leafstats.count_contents_in_stats(leafdata->contents);''')
s=s.replace(' logging::print("P3 SNAP',r''' static int hull=-1;if(std::string(stage)=="source")hull++;
 if(std::string(stage)=="source" || std::string(stage)=="post-csg"){
 std::ofstream f(qbsp_options.bsp_path.string()+".p4-"+stage+std::to_string(hull)+".tsv");f.precision(17);int idx=0;
 for(auto &b:bs){for(auto &s:b->sides){const qplane3d &p=s.get_plane();f<<idx<<"\t"<<b->mapbrush->line.line_number.value_or(0)<<"\t"<<s.planenum<<"\t"<<p.normal[0]<<" "<<p.normal[1]<<" "<<p.normal[2]<<" "<<p.dist<<"\n";}idx++;}}
 logging::print("P3 SNAP''')
p.write_text(s)
