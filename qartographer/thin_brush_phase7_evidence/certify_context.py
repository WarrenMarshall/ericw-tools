from fractions import Fraction as Q
from pathlib import Path
import json,itertools
base=Path('/tmp/qqbsp-phase7/evidence')
d=json.loads((base/'halloween-off/node.json').read_text())
planes=lambda ps:[[Q(v) for v in p] for p in ps]
node=planes(d['node']);sources=[planes(s['planes']) for s in d['sources']]
res=lambda p,x:sum((p[i]*x[i] for i in range(3)),Q(0))-p[3]
rows=[]
for x in [(162,800,-46),(222,-864,-192),(-2500,-2800,-600),(0,0,0),(2500,1000,-500)]:
 x=list(map(Q,x))
 if not all(res(p,x)<0 for p in node):continue
 hits=[i for i,ps in enumerate(sources) if all(res(p,x)<=0 for p in ps)]
 row={'point':[str(v) for v in x],'strict_node_interior':True,'source_hits':[{k:d['sources'][i][k] for k in ['source','contents','solid']} for i in hits]}
 if not hits:
  # Every source has a strictly excluding support: a complete-union exclusion certificate.
  row['excluding_support_per_source']=[next(j for j,p in enumerate(ps) if res(p,x)>0) for ps in sources]
  row['minimum_exclusion']=str(min(max(res(p,x) for p in ps) for ps in sources))
 rows.append(row)
solid=any(any(h['solid'] for h in r['source_hits']) for r in rows)
empty=any(not r['source_hits'] for r in rows)
result={'model':'exact rational binary64 input coefficients; rational test coordinates','complete_source_count':len(sources),'witnesses':rows,'constant_contents_refuted':solid and empty,'decision':'Whole-node constant-contents divider removal is not certified: this actual parent has both SOLID and source-empty interiors. No external-port equivalence has been proved.'}
(base/'halloween-node-occupancy.json').write_text(json.dumps(result,indent=2)+'\n')
print([(r['point'],len(r['source_hits'])) for r in rows],result['constant_contents_refuted'])
