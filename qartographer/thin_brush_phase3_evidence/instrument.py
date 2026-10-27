from pathlib import Path
root=Path('/tmp/qqbsp-phase3/source');repo=Path('/home/warrenmarshall/dev/ericw-tools')
s=(repo/'qbsp/brushbsp.cc').read_text()
helper=r'''
#include <fstream>
#include <cstring>
static bool p3world=false;
static int p3pass=0;
static std::string p3path;
static std::ofstream p3nodes;
static uint64_t p3hash(const bspbrush_t::container &bs) {
 uint64_t h=1469598103934665603ULL;
 auto add=[&](uint64_t x){h^=x;h*=1099511628211ULL;};
 for(auto &b:bs){add(b->mapbrush->line.line_number.value_or(0));add(b->sides.size());
 for(auto &s:b->sides){add(s.planenum);add(s.w.size());for(auto &p:s.w)for(int i=0;i<3;i++){uint64_t x;double d=p[i];std::memcpy(&x,&d,8);add(x);}}} return h;
}
static void p3snap(const char *stage,const bspbrush_t::container &bs){
 if(!p3world)return;
 logging::print("P3 SNAP {} count={} hash={}\n",stage,bs.size(),p3hash(bs));
}
static std::string p3nodepath(const node_t *node){std::string s;while(node->parent){auto *p=node->parent;s+=p->get_nodedata()->children[0]==node?'0':'1';node=p;}std::reverse(s.begin(),s.end());return s;}
'''
pos=s.index('static void LeafNode');s=s[:pos]+helper+s[pos:]
s=s.replace('    logging::header(__func__);\n\n    // NOTE:', '''    p3world=map.is_world_entity(entity);
    if(p3world){++p3pass;p3nodes.close();p3nodes.open(fmt::format("{}.tree{}.tsv",qbsp_options.bsp_path.string(),p3pass));p3nodes.precision(17);}
    logging::header(__func__);
    p3snap("bsp-input",brushlist);

    // NOTE:''')
s=s.replace('    // find the best plane to use as a splitter\n    auto *bestside', '''    if(p3world)p3path=p3nodepath(node);
    auto inputhash=p3world?p3hash(brushes):0;
    // find the best plane to use as a splitter
    auto *bestside''')
s=s.replace('    if (!bestside) {\n        // this is a leaf node', '''    if(p3world){p3nodes<<p3nodepath(node)<<"\\t"<<brushes.size()<<"\\t"<<inputhash<<"\\t";
      if(bestside){const qplane3d &p=map.planes[bestside->planenum & ~1];p3nodes<<(bestside->planenum & ~1)<<"\\t"<<p.normal[0]<<" "<<p.normal[1]<<" "<<p.normal[2]<<" "<<p.dist<<"\\t";
      for(auto &b:brushes)for(auto &side:b->sides)if(&side==bestside)p3nodes<<b->mapbrush->line.line_number.value_or(0);}
      else p3nodes<<"L\\t-\\t-";
      p3nodes<<"\\n";}
    if (!bestside) {
        // this is a leaf node''')
s=s.replace('    bool valid = CheckSplitBrush(node->volume, planenum);', '''    bool valid = CheckSplitBrush(node->volume, planenum);
    if(p3world && std::getenv("P3_PATH") && p3path==std::getenv("P3_PATH")){
      const qplane3d &p=map.planes[planenum];double f=0,b=0;
      for(auto &s:node->volume->sides)for(auto &v:s.w){double d=qv::dot(v,p.normal)-p.dist;f=std::max(f,d);b=std::min(b,d);}
      logging::print("P3 CAND pass={} path={} plane={} n={} d={} f={} b={} valid={}\\n",p3pass,p3path,planenum,p.normal,p.dist,f,b,valid);
    }''')
s=s.replace('    stats.print_stats();\n\n    CountLeafs', '    if(p3world)p3nodes.flush();\n    stats.print_stats();\n\n    CountLeafs')
(root/'qbsp/brushbsp.cc').write_text(s)
# stage snapshots in qbsp.cc, helpers are separate TU so expose helper
s=s.replace('static void p3snap','void p3snap');(root/'qbsp/brushbsp.cc').write_text(s)
s=(repo/'qbsp/qbsp.cc').read_text();s=s.replace('    // always chop the other hulls', '''    extern void p3snap(const char *,const bspbrush_t::container &);
    // p3world is set by prior BrushBSP; world snapshot printed directly here instead below
    // always chop the other hulls''')
# count/log geometry fingerprints before CSG even for first world call using exposed setter
s=s.replace('    // sort by ascending (chop_index, line_number) pair', '''    extern void p3start(bool);
    extern void p3snap(const char *,const bspbrush_t::container &);
    p3start(map.is_world_entity(entity));p3snap("source",brushes);
    // sort by ascending (chop_index, line_number) pair''')
s=s.replace('    // we\'re discarding the brush','    p3snap("post-csg",brushes);\n    // we\'re discarding the brush')
(root/'qbsp/qbsp.cc').write_text(s)
s=(root/'qbsp/brushbsp.cc').read_text().replace('static int p3pass=0;','void p3start(bool b){p3world=b;}\nstatic int p3pass=0;');(root/'qbsp/brushbsp.cc').write_text(s)
# portal aggregate winding validation: distance to endpoints ancestor halfspaces
s=(repo/'qbsp/portals.cc').read_text();s=s.replace('    tree.portaltype = portaltype_t::TREE;',r'''
    size_t bad=0,small=0,points=0;double maxerr=0,minarea=1e100,maxarea=0;
    for(auto &pp:tree.portals){auto &p=*pp;double area=p.winding.area();minarea=std::min(minarea,area);maxarea=std::max(maxarea,area);if(area<0.01)small++;
      double err=0;points+=p.winding.size();
      for(auto &v:p.winding)for(auto *end:p.nodes){auto *n=end;while(n->parent){auto *parent=n->parent;auto *nd=parent->get_nodedata();double d=nd->get_plane().distance_to(v);if(nd->children[0]==n)d=-d;err=std::max(err,d);n=parent;}}
      maxerr=std::max(maxerr,err);if(err>0.0001)bad++;
    }
    if(map.is_world_entity(map.entities[0]))logging::print("P3 PORTALS count={} points={} area_min={} area_max={} area_lt_001={} ancestor_bad={} max_error={}\n",tree.portals.size(),points,minarea,maxarea,small,bad,maxerr);
    tree.portaltype = portaltype_t::TREE;''')
(root/'qbsp/portals.cc').write_text(s)
