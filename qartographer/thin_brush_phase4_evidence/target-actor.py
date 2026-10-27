from pathlib import Path
p=Path('/tmp/qqbsp-phase4/source/qbsp/brushbsp.cc');s=p.read_text();s=s.replace('{-1364,-269,11.605075569064333}}','{-1364,-269,11.605075569064333},{-1280.0001220705,-1440,236.73692674130805}}');s=s.replace('for(int i=0;i<3;i++){auto *c=n;', 'for(int i=(p3pass>=4?3:0);i<(p3pass>=4?4:3);i++){auto *c=n;')
s=s.replace('    auto children = SplitBrushList(std::move(brushes), bestplane, stats);',r'''
    if(p3world && p3pass==5 && p4mask(node))for(auto &b:brushes){logging::print("P4 ROUTE path={} best={} line={} side={} xmin={} xmax={} ymin={} ymax={} zmin={} zmax={}\n",p3nodepath(node),bestplane,b->mapbrush->line.line_number.value_or(0),b->side,b->bounds.mins()[0],b->bounds.maxs()[0],b->bounds.mins()[1],b->bounds.maxs()[1],b->bounds.mins()[2],b->bounds.maxs()[2]);}
    auto children = SplitBrushList(std::move(brushes), bestplane, stats);''');p.write_text(s)
