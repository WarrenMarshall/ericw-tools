from pathlib import Path
import sys,json,struct
sys.dont_write_bytecode=True
sys.path.insert(0,'/tmp/qqbsp-phase7/phase6/component')
from oracle import rows,dimension
base=Path('/tmp/qqbsp-phase8');out=[]
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
key=lambda ps:frozenset(tuple(p) for p in ps)
def dim(ps):return dimension(rows(list(key(ps))))
for file in sorted((base/'evidence/accepted-experiment-matrix').glob('*/node.json.portal-proofs.jsonl')):
 count=edges=0
 for line in file.read_text().splitlines():
  proof=json.loads(line);current=key(proof['omitted_regions'][1]);end=key(proof['omitted_regions'][0]);count+=1
  for edge in proof['path']:
   regions=edge['incident_regions'];a,b=map(key,regions);assert current in [a,b]
   current=b if current==a else a
   for conv in [lambda x:x,f32]:
    ps=[[conv(v) for v in p] for p in edge['planes']];q=list(map(conv,edge['query']))
    assert dim(ps+[q,[-v for v in q]])==2
    for r in regions:assert dim([[conv(v) for v in p] for p in r])==3
   edges+=1
  assert current==end
 out.append(dict(file=str(file),omitted_portals=count,alternative_edges_checked=edges,exact_and_float32_area_and_volumes=True,continuous_path_between_original_empty_endpoints=True))
 assert count==8
assert len(out)==2
matrix=json.loads((base/'evidence/accepted-experiment-matrix/results.json').read_text())
assert len(matrix)==42 and all(not r['failures'] for r in matrix.values())
result=dict(routes=out,compiles=len(matrix),occupancy_comparisons=sum(sum(r['counts'].values()) for r in matrix.values()),unchanged_oracle_failures=0)
(base/'evidence/route-verification.json').write_text(json.dumps(result,indent=2));print(result)
