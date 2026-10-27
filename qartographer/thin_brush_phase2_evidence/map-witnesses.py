import re,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/warrenmarshall/dev/ericw-tools/qartographer')
import spline_smooth_collision_compile as c
root=Path('/tmp/qqbsp-phase2/uniform-regression/patched/full')
points=[p for _,p in json.load(open(root/'oracle-failures.json'))]
rows={}
for name in ['full-off','full-on']:
 cells=[]
 for body in re.findall(r'\{([^{}]+)\}',(root/(name+'.map')).read_text()):
  planes=[];clip=False
  for line in body.splitlines():
   vs=[tuple(map(float,m.split())) for m in re.findall(r'\(([^()]*)\)',line)]
   if len(vs)!=3:continue
   clip|=bool(re.search(r'\) CLIP ',line))
   n=c.norm(c.cross(c.sub(vs[0],vs[1]),c.sub(vs[2],vs[1])))
   assert n is not None
   planes.append((n,c.dot(n,vs[0])))
  if len(planes)>=4 and not clip:cells.append(planes)
 b=c.BSP(root/(name+'.bsp'))
 rows[name]=[dict(point=p,source_margin=c.margin(p,cells),expected=-2 if c.margin(p,cells)<0 else -1,actual=b.contents(p,hull=0)) for p in points]
Path('/tmp/qqbsp-phase2/map-witnesses.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
