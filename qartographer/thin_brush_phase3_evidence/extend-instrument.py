from pathlib import Path
r=Path('/tmp/qqbsp-phase3');src=r/'source/qbsp'
s=(src/'brushbsp.cc').read_text().replace('static std::string p3nodepath','std::string p3nodepath')
s=s.replace('    if(p3world){p3nodes<<', '    if(p3world && p3pass<=2){p3nodes<<')
s=s.replace('if(p3world){++p3pass;p3nodes.close();p3nodes.open', 'if(p3world){++p3pass;p3nodes.close();if(p3pass<=2)p3nodes.open')
# function for supported winding dump and root split snapshots
at=s.index('static void LeafNode')
s=s[:at]+r'''
static void p3dump(const char *tag,const bspbrush_t::container &bs){
 std::ofstream f(fmt::format("{}.{}.tsv",qbsp_options.bsp_path.string(),tag));f.precision(17);
 for(auto &b:bs){for(auto &s:b->sides){const qplane3d &p=s.get_plane();f<<b->mapbrush->line.line_number.value_or(0)<<"\t"<<s.planenum<<"\t"<<p.normal[0]<<" "<<p.normal[1]<<" "<<p.normal[2]<<" "<<p.dist<<"\t";for(auto &v:s.w)f<<v[0]<<" "<<v[1]<<" "<<v[2]<<";";f<<"\n";}}
}
'''+s[at:]
s=s.replace('    auto children = SplitBrushList(std::move(brushes), bestplane, stats);',r'''
    if(p3world && p3pass==1 && level==0)p3dump("root-input",brushes);
    if(p3world && p3pass==1 && p3nodepath(node)=="0101010")p3dump("choice-input",brushes);
    auto children = SplitBrushList(std::move(brushes), bestplane, stats);
    if(p3world && p3pass==1 && level==0){p3dump("root-front",children[0]);p3dump("root-back",children[1]);}
''')
(src/'brushbsp.cc').write_text(s)
s=(src/'portals.cc').read_text();s='#include <fstream>\n#include <set>\n'+s
s=s.replace('    tree.portaltype = portaltype_t::TREE;',r'''
    static int p3pc=0;
    if(++p3pc==1){
      extern std::string p3nodepath(const node_t *);
      std::set<std::string> wanted;std::ifstream inp("/tmp/qqbsp-phase3/route-leaves.txt");std::string line;while(std::getline(inp,line))wanted.insert(line);
      std::ofstream f(qbsp_options.bsp_path.string()+".route-portals.tsv");f.precision(17);
      for(auto &pp:tree.portals){auto &p=*pp;auto a=p3nodepath(p.nodes[0]),b=p3nodepath(p.nodes[1]);
       if(!wanted.count(a)||!wanted.count(b))continue;
       f<<a<<"\t"<<b<<"\t";for(auto &v:p.winding)f<<v[0]<<" "<<v[1]<<" "<<v[2]<<";";f<<"\n";
      }
    }
    tree.portaltype = portaltype_t::TREE;''')
(src/'portals.cc').write_text(s)
