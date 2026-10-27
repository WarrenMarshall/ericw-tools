import json,sys,itertools
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/warrenmarshall/dev/ericw-tools/qartographer')
import spline_smooth_collision_compile as c
full=json.load(open('/home/warrenmarshall/dev/ericw-tools/qartographer/qartographer/fixtures/full-geometry.json'.replace('/qartographer/qartographer/','/qartographer/')))
# Direct source face halfspaces, no compiler-derived expected occupancy.
cells=[]
for r in full:
 vs=[c.quake(v) for f in r['faces'] for v in f['v']]; center=tuple(sum(v[i] for v in vs)/len(vs) for i in range(3));planes=[]
 for f in r['faces']:
  v=[c.quake(p) for p in f['v']]; n=next((n for a,b,d in itertools.combinations(v,3) if (n:=c.norm(c.cross(c.sub(b,a),c.sub(d,a)))) is not None),None)
  if n is None:continue
  if c.dot(n,c.sub(center,v[0]))>0:n=tuple(-x for x in n)
  planes.append((n,c.dot(n,v[0])))
 cells.append((r,planes))
root=Path('/tmp/qqbsp-phase2/uniform-regression/patched/full')
old,new=[c.BSP(root/(name+'.bsp')) for name in ['full-off','full-on']]
rows=[]
for _,p in json.load(open(root/'oracle-failures.json')):
 near=sorted([(max(c.dot(n,p)-d for n,d in planes),r['item'],r['spline'],r['world']) for r,planes in cells])[:5]
 rows.append(dict(point=p,off=old.contents(p,hull=0),on=new.contents(p,hull=0),source_nearest=near))
Path('/tmp/qqbsp-phase2/full-witnesses.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
