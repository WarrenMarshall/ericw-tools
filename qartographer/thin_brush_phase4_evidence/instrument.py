from pathlib import Path
p=Path('/tmp/qqbsp-phase4/source/qbsp/brushbsp.cc');s=p.read_text()
a=s.index('static void LeafNode(')
s=s[:a]+r'''
static qvec3d p4pts[]={{-1388,-233,8.778914155553586},{-1376,-257,-12.914510661888684},{-1364,-269,11.605075569064333}};
static int p4mask(const node_t *n){int mask=0;for(int i=0;i<3;i++){auto *c=n;bool ok=true;while(c->parent){auto *p=c->parent;auto *d=p->get_nodedata();bool front=d->get_plane().distance_to(p4pts[i])>=0;if(d->children[front?0:1]!=c){ok=false;break;}c=p;}if(ok)mask|=1<<i;}return mask;}
static void p4dump(node_t *n,const bspbrush_t::container &bs,const char *stage){
 if(!p3world)return;int mask=p4mask(n);if(!mask)return;
 std::ofstream f(qbsp_options.bsp_path.string()+".p4.tsv",std::ios::app);f.precision(17);
 auto path=p3nodepath(n);f<<"NODE\t"<<p3pass<<"\t"<<path<<"\t"<<mask<<"\t"<<stage<<"\t"<<bs.size()<<"\n";
 auto dump=[&](const bspbrush_t &b,long line){
 for(auto &s:b.sides){auto &p=s.get_plane();f<<"SIDE\t"<<p3pass<<"\t"<<path<<"\t"<<line<<"\t"<<s.planenum<<"\t"<<s.onnode<<"\t"<<s.bevel<<"\t"<<s.is_visible()<<"\t"<<p.normal[0]<<" "<<p.normal[1]<<" "<<p.normal[2]<<" "<<p.dist<<"\t";for(auto &v:s.w)f<<v[0]<<" "<<v[1]<<" "<<v[2]<<";";f<<"\n";}
 };
 if(n->volume)dump(*n->volume,-1);
 for(auto &b:bs)dump(*b,b->mapbrush->line.line_number.value_or(0));
}
''' + s[a:]
s=s.replace('    // find the best plane to use as a splitter','    p4dump(node,brushes,"before");\n    // find the best plane to use as a splitter')
s=s.replace('    stats.leafstats.count_contents_in_stats(leafdata->contents);','    p4dump(leafnode,brushes,"leaf");\n    stats.leafstats.count_contents_in_stats(leafdata->contents);')
s=s.replace('p3pass<=2','p3pass<=9')
s=s.replace('    bool valid = CheckSplitBrush(node->volume, planenum);',r'''    bool valid = CheckSplitBrush(node->volume, planenum);
    if(p3world && p4mask(node)){logging::print("P4 ADMIT pass={} path={} plane={} valid={}\n",p3pass,p3nodepath(node),planenum,valid);}''') # p4mask declared later needs forward
s=s.replace('static bool CheckPlaneAgainstVolume(', 'static bool CheckPlaneAgainstVolume(') # forward before check
idx=s.index('inline bool CheckPlaneAgainstVolume')
s=s[:idx]+'static int p4mask(const node_t *);\n'+s[idx:]
p.write_text(s)
