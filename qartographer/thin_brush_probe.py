#!/usr/bin/env python3
"""Independent thin-brush source/Minkowski oracle; nonzero means a real mismatch.
Usage: thin_brush_probe.py QBSP NEW_OUTPUT_DIRECTORY
The current pristine alpha10 and P1-only compiler fail. This is an unresolved
regression, not a Tier 3 passing fixture or an accepted P3 correction.
"""
import sys,re,json,subprocess,math,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import spline_smooth_collision_compile as c
from wildspline_bsp_collision_compile import brushes,expanded
q,out=Path(sys.argv[1]),Path(sys.argv[2]);out.mkdir(exist_ok=False)
identity=subprocess.run([str(q),'-help'],capture_output=True,text=True)
(out/'identity.txt').write_text(identity.stdout+identity.stderr)
assert identity.returncode==0
(out/'compiler.json').write_text(json.dumps({'path':str(q.resolve()),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()},indent=2)+'\n')
fixture=(Path(__file__).resolve().parent/'fixtures/thin-direct/original.map').read_text()
control=(Path(__file__).resolve().parent/'fixtures/thin-direct/control.map').read_text()
base=re.findall(r'^\{\n(\( .*?)^\}',fixture,re.M|re.S)[0]
def transform(body,fn):
 lines=[]
 for line in body.splitlines():
  points=[fn(tuple(map(float,v.split()))) for v in re.findall(r'\(([^()]+)\)',line)]
  lines.append(' '.join('( '+' '.join(format(v,'.15g') for v in p)+' )' for p in points)+' NO_TEXTURE 0 0 0 1 1')
 return '\n'.join(lines)+'\n'
def world(bodies):return '{\n"classname" "worldspawn"\n'+''.join('{\n'+b+'}\n' for b in bodies)+'}\n'
cases={'original':fixture,'control':control}
for t in [.0005,.002,.008,.015625,.02,.05,.099,.1,.101,.25,1,16]:
 cases['thickness-'+str(t)]=world([transform(base,lambda p:(p[0],p[1],p[2]*t/.008))])
for axis in [0,1]:
 cases['axis-'+str(axis)]=world([transform(base,lambda p:tuple(p[(i+axis+1)%3] for i in range(3)))])
cases['translated']=world([transform(base,lambda p:(p[0]+512.125,p[1]-256.25,p[2]+128.5))])
def rot(p):
 a=.37;b=.23;x,y,z=p
 x,y=math.cos(a)*x-math.sin(a)*y,math.sin(a)*x+math.cos(a)*y
 return math.cos(b)*x+math.sin(b)*z,y,-math.sin(b)*x+math.cos(b)*z
cases['rotated']=world([transform(base,rot)])
cases['adjacent']=world([base,transform(base,lambda p:(p[0],p[1]+64,p[2]))])
cases['overlap']=world([base,transform(base,lambda p:(p[0]+16,p[1]+32,p[2]+.002))])
cases['near-coplanar']=world([base,transform(base,lambda p:(p[0],p[1],p[2]+.0082))])
results={}
for name,text in cases.items():
 geometry=brushes(text);centers=[tuple(sum(v[i] for v in vs)/len(vs) for i in range(3)) for _,vs,_ in geometry]
 vertices=[v for _,vs,_ in geometry for v in vs]
 for mode,flags in [('default',[]),('chopfragment',['-chopfragment'])]:
  d=out/(name+'-'+mode);d.mkdir();p=d/'input.map';p.write_text(text)
  start=time.monotonic();r=subprocess.run([str(q),*flags,'-bsp2','-notex','-nopercent',str(p)],capture_output=True,text=True);elapsed=time.monotonic()-start
  (d/'compile.log').write_text(r.stdout+r.stderr);assert r.returncode==0,name
  b=c.BSP(p.with_suffix('.bsp'));fails=[];counts={}
  for hull,radius,offset in [(0,(0,0,0),0),(1,(16,16,28),4),(2,(32,32,44),20)]:
   cells=[expanded(g,radius) for g in geometry]
   lo=[min(v[i] for v in vertices)-radius[i]-4 for i in range(3)];hi=[max(v[i] for v in vertices)+radius[i]+4 for i in range(3)]
   points=centers+[tuple(lo[i]+c.halton(k,[2,3,5][i])*(hi[i]-lo[i]) for i in range(3)) for k in range(1,257)]
   for center,planes in zip(centers,cells):
    for n,distance in planes:
     span=min((d-c.dot(nn,center))/c.dot(nn,n) for nn,d in planes if c.dot(nn,n)>1e-8)
     for delta in [-.00015,.25]:points.append(tuple(center[i]+n[i]*(span+delta) for i in range(3)))
   checked=0
   for point in points:
    margin=c.margin(point,cells)
    if abs(margin)<1e-6:continue
    actual=b.contents((point[0],point[1],point[2]-offset),hull=hull);want=-2 if margin<0 else -1;checked+=1
    if actual!=want:fails.append({'hull':hull,'point':point,'margin':margin,'want':want,'actual':actual})
   counts[str(hull)]=checked
  results[d.name]={'failures':fails,'counts':counts,'seconds':elapsed,'map_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bsp_sha256':hashlib.sha256(b.b).hexdigest()}
  print(d.name,len(fails),fails[:1],flush=True)
  (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS' if not any(v['failures'] for v in results.values()) else 'FAIL')
sys.exit(int(any(v['failures'] for v in results.values())))
