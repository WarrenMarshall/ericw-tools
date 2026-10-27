from pathlib import Path
import json,sys
from oracle import rows,feasible,dimension,range_on_plane
E=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/qqbsp-phase6/evidence');out=[]
for case in json.loads((E/'cases.json').read_text()):
    if case['name'] not in ['D-halloween-rounded-extent','E-p1-rounded-extent','F-rotated-portal']:continue
    ps=case['planes'];q=case['query'];target=range_on_plane(ps,q)['maximum']
    def retains(candidate):
        if case['name'].startswith('D-'):return range_on_plane(candidate,q)['maximum']==target
        rs=rows(candidate);a,b,_=rows([q])[0];front=(tuple(-v for v in a),-b,True)
        if case['name'].startswith('E-'):return feasible(rs) and not feasible(rs+[front])
        return dimension(rs+[(a,b,False),(tuple(-v for v in a),-b,False)])==1
    for p in list(ps):
        candidate=list(ps);candidate.remove(p)
        if retains(candidate):ps=candidate
    out.append(dict(name=case['name'],original_count=len(case['planes']),planes=ps,query=q,note='Oracle-minimized decision supports; may be unbounded without the original parent domain. Not substituted for the bounded API fixture.'))
(E/'minimized-blockers.json').write_text(json.dumps(out,indent=2)+'\n')
print([(r['name'],r['original_count'],len(r['planes'])) for r in out])
