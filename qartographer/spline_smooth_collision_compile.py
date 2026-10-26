#!/usr/bin/env python3
"""Compile exports from spline_smooth_collision_test.gd and inspect actual BSP hulls.
Usage: python3 tests/helpers/spline_smooth_collision_compile.py /path/to/qbsp [export-directory]
"""
import struct,json,math,subprocess,time,pathlib,re

def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):
 l=math.sqrt(dot(a,a));return tuple(x/l for x in a) if l>1e-8 else None
def quake(p):return (p[0],-p[2],p[1])
class BSP:
 def __init__(self,path):
  self.b=pathlib.Path(path).read_bytes();assert self.b[:4]==b'BSP2'
  self.l=[struct.unpack_from('<ii',self.b,4+i*8) for i in range(15)]
 def i(self,at):return struct.unpack_from('<i',self.b,at)[0]
 def head(self,model,hull):return self.i(self.l[14][0]+64*model+36+4*hull)
 def contents(self,p,model=0,hull=1):
  n=self.head(model,hull)
  while n>=0:
   at=self.l[5 if hull==0 else 9][0]+n*(44 if hull==0 else 12)
   plane=self.l[1][0]+self.i(at)*20
   a,b,c,d=struct.unpack_from('<4f',self.b,plane)
   n=self.i(at+(4 if a*p[0]+b*p[1]+c*p[2]>=d else 8))
  return self.i(self.l[10][0]+(-1-n)*44) if hull==0 else n
 def models(self):return self.l[14][1]//64

def compile(name,text):
 (D/(name+'.map')).write_text(text);t=time.monotonic()
 p=subprocess.run([QB,'-chopfragment','-bsp2','-notex','-nopercent',str(D/(name+'.map'))],capture_output=True,text=True)
 (D/(name+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
 return BSP(D/(name+'.bsp')),time.monotonic()-t

def supports(faces,extents=(0,0,0)):
 vertices=[quake(v) for f in faces for v in f['v']];center=tuple(sum(v[i] for v in vertices)/len(vertices) for i in range(3));ns=[]
 for f in faces:
  vs=[quake(v) for v in f['v']];n=norm(cross(sub(vs[1],vs[0]),sub(vs[2],vs[0])))
  if dot(n,sub(center,vs[0]))>0:n=tuple(-v for v in n)
  ns.append(n)
  for a,b in zip(vs,vs[1:]+vs[:1]):
   for axis in [(1,0,0),(0,1,0),(0,0,1)]:
    n=norm(cross(sub(b,a),axis))
    if n:
     ds=[dot(n,v) for v in vertices];d=dot(n,a)
     if max(ds)-d<.001:ns.append(n)
     if d-min(ds)<.001:ns.append(tuple(-v for v in n))
 ns.extend([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)])
 return [(n,max(dot(n,v) for v in vertices)+sum(abs(n[i])*extents[i] for i in range(3))) for n in ns]

def halton(index,base):
 value=0;fraction=1/base
 while index:
  value+=fraction*(index%base);index//=base;fraction/=base
 return value

def margin(point,cells):return min(max(dot(n,point)-d for n,d in cell) for cell in cells)

def run():
 global D,QB
 import sys
 QB=sys.argv[1];D=pathlib.Path(sys.argv[2] if len(sys.argv)>2 else '/tmp/qart-spline-smooth-test')
 geometry=json.loads((D/'geometry.json').read_text());results={}
 selected=set(sys.argv[3:])
 if selected and (D/'compiled-results.json').exists():results=json.loads((D/'compiled-results.json').read_text())
 for name,solids in geometry.items():
  if selected and name not in selected:continue
  text=(D/(name+'.map')).read_text();b,seconds=compile(name,text)
  vertices=[quake(v) for s in solids for f in s for v in f['v']]
  counts={};failures=[]
  # Interior samples and low-discrepancy samples surrounding the entire shape.
  points=[tuple(sum(quake(v)[i] for f in s for v in f['v'])/sum(len(f['v']) for f in s) for i in range(3)) for s in solids]
  lo=[min(v[i] for v in vertices)-48 for i in range(3)];hi=[max(v[i] for v in vertices)+48 for i in range(3)]
  points += [tuple(lo[i]+halton(k,[2,3,5][i])*(hi[i]-lo[i]) for i in range(3)) for k in range(1,1025)]
  for hull,radius,offset in [(0,(0,0,0),0),(1,(16,16,28),4),(2,(32,32,44),20)]:
   cells=[supports(s,radius) for s in solids];checked=0
   for p in points:
    q=(p[0],p[1],p[2]+offset);distance=margin(q,cells)
    if abs(distance)<.25:continue # Outside the proven 0.082-unit proxy envelope.
    wanted=distance<0
    got=any(b.contents(p,model=m,hull=hull)==-2 for m in range(b.models()))
    checked+=1
    if got!=wanted:failures.append({'hull':hull,'p':p,'margin':distance,'solid':got})
   counts[str(hull)]=checked
  # Compiled omission semantics must hold at every source-cell interior, and
  # world CLIP must contribute no point/projectile collision there.
  for p in points[:len(solids)]:
   assert b.contents(p,hull=0)==-1,(name,'CLIP unexpectedly blocks point trace')
   assert any(b.contents(p,model=m,hull=0)==-2 for m in range(1,b.models())),(name,'lost visual projectile collision')
   for m in range(1,b.models()):
    assert b.contents(p,model=m,hull=1)==-1 and b.contents(p,model=m,hull=2)==-1,(name,'visual player hull was not omitted')
  warnings=[l for l in (D/(name+'.log')).read_text().splitlines() if 'WARNING' in l and any(t in l for t in ['huge winding','degenerate','sides not found','crunched','invalid'])]
  assert not failures,(name,'compiled/source mismatch',failures[:5])
  inherited=[];cosmetic=[]
  if warnings:
   # Keep detailed visual/compiler defects distinct from generated collision.
   visual=text[text.index('"classname" "func_wall"')-2:]
   _,_=compile(name+'-visual-only','{\n"classname" "worldspawn"\n}\n'+visual)
   baseline=(D/(name+'-visual-only.log')).read_text()
   clean=lambda line:re.sub(r'\x1b\[[0-9;]*m','',line).strip()
   for warning in warnings:
    if clean(warning) in {clean(l) for l in baseline.splitlines()}:inherited.append(clean(warning));continue
    log=(D/(name+'.log')).read_text();at=log.find(warning)
    # Tiny cube-bevel faces can be discarded while building the intentionally
    # invisible CLIP hull 0. They are not faces of hulls 1/2 or visual geometry.
    if 'faces were crunched away' in warning and log.rfind('Processing hull 0',0,at)>log.rfind('Processing hull 1',0,at):cosmetic.append(clean(warning));continue
    raise AssertionError((name,'new collision warning',warning))
  results[name]={'source_brushes':len(solids),'export_brushes':sum(1 for l in text.splitlines() if l=='{')-text.count('"classname"'),'plane_lines':sum(l.startswith('(') for l in text.splitlines()),'compile_seconds':seconds,'samples':counts,'inherited_visual_warnings':inherited,'invisible_hull0_warnings':cosmetic}
  print(name,counts,'PASS',round(seconds,4),'seconds',flush=True)
 # Independently specified real-map support/clearance witnesses, including the
 # 32-unit player box that intersects the actual deck below its origin.
 b=BSP(D/'halloween.bsp')
 assert b.contents((-1400,-1664,150))==-2
 assert b.contents((-1400,-1664,200))==-1
 assert b.contents((-1400,-1664,70))==-1
 if selected:
  original=BSP(D/'halloween-original.bsp');seconds=results['original']['compile_seconds']
 else:original,seconds=compile('halloween-original',(D/'halloween-original.map').read_text())
 # Record the historical compiler defect; requiring incorrect collision here
 # would reject a compiler that preserves the original floor correctly.
 original_missing_support=original.contents((-1400,-1664,150))==-1
 # Original visual surface remains solid to a point trace.
 assert original.contents((-1400,-1656,127),hull=0)==-2
 assert b.contents((-1400,-1656,127),model=1,hull=0)==-2
 for name,p in [('profiles-opening',(32,96,0)),('closed',(96,96,0))]:
  assert BSP(D/(name+'.bsp')).contents(p,hull=1)==-1,(name,'intentional opening obstructed')
 results['original']={'historical_missing_actor_support':original_missing_support,'compile_seconds':seconds,'plane_lines':sum(l.startswith('(') for l in (D/'halloween-original.map').read_text().splitlines())}
 (D/'compiled-results.json').write_text(json.dumps(results,indent=2)+'\n')
 print('Compiled Spline collision: PASS')
if __name__=='__main__':run()
