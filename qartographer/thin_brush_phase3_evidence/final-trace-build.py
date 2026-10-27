from pathlib import Path
r=Path('/tmp/qqbsp-phase3');p=r/'source/qbsp/brushbsp.cc'
s=(r/'p1-target-brushbsp.cc').read_text().replace('p3path==std::getenv("P3_PATH")','std::string(std::getenv("P3_PATH")).find(p3path)!=std::string::npos')
p.write_text(s)
p=r/'source/qbsp/outside.cc';s=Path('/home/warrenmarshall/dev/ericw-tools/qbsp/outside.cc').read_text()
s=s.replace('    if (leakentity) {',r'''
    if (leakentity) {
        size_t i=0;for(auto *p:leakline){double err=0;for(auto &v:p->winding)for(auto *n:p->nodes)while(n->parent){auto *par=n->parent;auto *nd=par->get_nodedata();double d=nd->get_plane().distance_to(v);if(nd->children[0]==n)d=-d;err=std::max(err,d);n=par;}
        logging::print("P3 LEAKPORTAL index={} area={} ancestor_error={}\n",i++,p->winding.area(),err);}
''')
p.write_text(s)
