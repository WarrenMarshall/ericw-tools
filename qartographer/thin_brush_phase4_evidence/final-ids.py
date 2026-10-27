import sys,json,struct
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/warrenmarshall/dev/ericw-tools/qartographer');from spline_smooth_collision_compile import BSP
pts=[[-1388,-233,8.778914155553586],[-1376,-257,-12.914510661888684],[-1364,-269,11.605075569064333]];b=BSP('/tmp/qqbsp-phase4/off-target/input.bsp');out=[]
for p in pts:
 n=b.head(0,0);path=[]
 while n>=0:
  at=b.l[5][0]+n*44;pn=b.i(at);plane=struct.unpack_from('<4f',b.b,b.l[1][0]+pn*20);ch=0 if sum(plane[i]*p[i] for i in range(3))>=plane[3] else 1;path.append(dict(node=n,plane=pn,branch=ch));n=b.i(at+4+4*ch)
 out.append(dict(point=p,leaf=-1-n,contents=b.i(b.l[10][0]+(-1-n)*44),path=path))
Path('/tmp/qqbsp-phase4/final-ids.json').write_text(json.dumps(out,indent=2));print([(x['leaf'],x['contents']) for x in out])
