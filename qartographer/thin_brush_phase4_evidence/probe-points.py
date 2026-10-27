from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/warrenmarshall/dev/ericw-tools/qartographer');from spline_smooth_collision_compile import BSP
r=Path('/tmp/qqbsp-phase4/off-extended');pts=[[-1280.0001220705,-1440,236.73692674130805],[-1280.0003,-1440,236.73692674130805],[-1279.9999,-1440,236.73692674130805]];out=[]
for ps in [4,5]:
 t={a[0]:a for l in (r/f'input.bsp.tree{ps}.tsv').read_text().splitlines() if (a:=l.split('\t'))};leaves={}
 for l in (r/'input.bsp.p4-contents.tsv').read_text().splitlines():
  a=l.split('\t')
  if int(a[0])==ps:leaves[a[1]]=list(map(int,a[2:]))
 for p in pts:
  path=''
  while t[path][3]!='L':
   q=list(map(float,t[path][4].split()));path+='0' if sum(q[i]*p[i] for i in range(3))>=q[3] else '1'
  out.append(dict(pass_=ps,point=p,path=path,count=int(t[path][1]),solid_sky=leaves[path]))
b=BSP(r/'input.bsp');print(json.dumps(out,indent=2));print('final',[b.contents(p,hull=2) for p in pts]);Path('/tmp/qqbsp-phase4/actor-points.json').write_text(json.dumps(dict(points=out,final=[b.contents(p,hull=2) for p in pts]),indent=2))
