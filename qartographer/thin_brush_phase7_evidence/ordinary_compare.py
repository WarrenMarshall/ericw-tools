from pathlib import Path
import sys,subprocess,shutil,json,hashlib,struct
sys.dont_write_bytecode=True
base=Path('/tmp/qqbsp-phase7');e=base/'evidence/ordinary-comparison';e.mkdir(exist_ok=True)
sys.path.insert(0,str(base/'source/qartographer'))
import spline_smooth_collision_compile as c
from wildspline_bsp_collision_compile import brushes,expanded
class BSP29(c.BSP):
 def __init__(self,path):
  self.b=Path(path).read_bytes();assert struct.unpack_from('<i',self.b)[0]==29
  self.l=[struct.unpack_from('<ii',self.b,4+i*8) for i in range(15)]
 def contents(self,p,model=0,hull=1):
  n=self.head(model,hull)
  while n>=0:
   at=self.l[5 if hull==0 else 9][0]+n*(24 if hull==0 else 8)
   a,b,c,d=struct.unpack_from('<4f',self.b,self.l[1][0]+self.i(at)*20)
   n=struct.unpack_from('<h',self.b,at+(4 if a*p[0]+b*p[1]+c*p[2]>=d else 6))[0]
  return self.i(self.l[10][0]+(-1-n)*28) if hull==0 else n
installed=Path('/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp')
rows=[]
for label in ['ordinary','ordinary-rotated-hull0','ordinary-L-room']:
 source=base/'evidence/campaign'/label/'input.map';d=e/label;d.mkdir(exist_ok=True);m=d/'input.map';shutil.copyfile(source,m)
 cmd=[str(installed),'-notex','-nopercent','-chopfragment','-threads','1',*(['-noclip'] if 'hull0' in label else []),str(m)]
 if not m.with_suffix('.bsp').exists():
  with (d/'compile.log').open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=55)
  assert p.returncode==0
 baseline=BSP29(m.with_suffix('.bsp'));candidate=BSP29(source.with_suffix('.bsp'));geometry=brushes(m.read_text())
 vertices=[v for _,vs,_ in geometry for v in vs];report={}
 for hull,radius,offset in [(0,(0,0,0),0),(1,(16,16,28),4),(2,(32,32,44),20)]:
  if 'hull0' in label and hull:continue
  cells=[expanded(g,radius) for g in geometry];lo=[min(v[i] for v in vertices)-radius[i]-4 for i in range(3)];hi=[max(v[i] for v in vertices)+radius[i]+4 for i in range(3)]
  failures=[];different=[];count=0
  for k in range(1,513):
   point=tuple(lo[i]+c.halton(k,[2,3,5][i])*(hi[i]-lo[i]) for i in range(3));margin=c.margin(point,cells)
   if abs(margin)<1e-6:continue
   count+=1;want=-2 if margin<0 else -1;engine=(point[0],point[1],point[2]-offset)
   got=candidate.contents(engine,hull=hull);old=baseline.contents(engine,hull=hull)
   if got!=want:failures.append(dict(point=point,margin=margin,want=want,actual=got))
   if got!=old:different.append(dict(point=point,candidate=got,baseline=old))
  report[str(hull)]=dict(samples=count,failures=failures,differences=different)
 rows.append(dict(name=label,hulls=report,accepted_compiler_sha256=hashlib.sha256(installed.read_bytes()).hexdigest(),candidate_bsp_sha256=hashlib.sha256(candidate.b).hexdigest(),accepted_bsp_sha256=hashlib.sha256(baseline.b).hexdigest()))
(e/'results.json').write_text(json.dumps(rows,indent=2)+'\n');assert all(not h['failures'] and not h['differences'] for row in rows for h in row['hulls'].values());print('PASS',[(r['name'],{h:v['samples'] for h,v in r['hulls'].items()}) for r in rows])
