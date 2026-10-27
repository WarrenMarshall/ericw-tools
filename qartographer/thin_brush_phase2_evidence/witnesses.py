import sys,json,struct
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/warrenmarshall/dev/ericw-tools/qartographer')
import spline_smooth_collision_compile as c
from wildspline_bsp_collision_compile import brushes,expanded
root=Path('/tmp/qqbsp-phase2')
rows=[]
for name in ['overlap','near-coplanar']:
 p=Path('/tmp/qqbsp-p3/prototype-matrix')/(name+'-default')/'input.map'
 gs=brushes(p.read_text())
 old=c.BSP(p.with_suffix('.bsp'));new=c.BSP(root/'uniform-epsilon-matrix'/(name+'-default')/'input.bsp')
 raw=json.load(open('/home/warrenmarshall/dev/ericw-tools/qartographer/thin_brush_evidence/rejected-prototype-matrix.json'))[name+'-default']['failures']
 for hull,rad,offset in [(1,(16,16,28),4),(2,(32,32,44),20)]:
  cells=[expanded(g,rad) for g in gs]
  witness=next(x for x in raw if x['hull']==hull)
  samples=[('original',witness['point'])]
  zlo=min(v[2] for _,vs,_ in gs for v in vs)-rad[2]
  for depth in [.00015,.001,.004]:samples.append(('lower-depth-'+str(depth),[0,32,zlo+depth]))
  for label,point in samples:
   engine=(point[0],point[1],point[2]-offset)
   rows.append(dict(case=name,hull=hull,label=label,original=witness if label=='original' else None,oracle_point=point,engine_point=engine,source_margin=c.margin(point,cells),expected=-2 if c.margin(point,cells)<0 else -1,prototype=old.contents(engine,hull=hull),diagnostic=new.contents(engine,hull=hull)))
(root/'actor-witnesses.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
