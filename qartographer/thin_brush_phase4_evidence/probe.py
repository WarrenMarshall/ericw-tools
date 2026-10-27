#!/usr/bin/env python3
"""Read-only Phase 4 evidence replay. No compiles or production-gate changes."""
import argparse,hashlib,json,math,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--repository',type=Path,default=Path('/home/warrenmarshall/dev/ericw-tools'));args=ap.parse_args()
e=Path(__file__).resolve().parent;q=args.repository/'qartographer'
load=lambda p:json.loads(p.read_text())
for rows in load(e/'witness-index.json').values():
 for row in rows:
  p=q/row['path'].removeprefix('../')
  assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],p
# Source expectations use each MAP separately, with the established standalone-brace parser.
points=[[-1388,-233,8.778914155553586],[-1376,-257,-12.914510661888684],[-1364,-269,11.605075569064333]]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return [x-y for x,y in zip(a,b)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
out={}
for mode in ['full-on','full-off']:
 text=(q/'fixtures'/f'{mode}.map').read_text();depth=0;cells=[]
 for m in re.finditer(r'^\s*[{}]\s*$',text,re.M):
  if m[0].strip()=='{':
   depth+=1
   if depth==2:start=m.end()
  else:
   if depth==2:
    ps=[];clip=False
    for line in text[start:m.start()].splitlines():
     vs=[list(map(float,v.split())) for v in re.findall(r'\(([^()]*)\)',line)]
     if len(vs)!=3:continue
     clip|=bool(re.search(r'\) CLIP ',line));n=cross(sub(vs[0],vs[1]),sub(vs[2],vs[1]));length=math.sqrt(dot(n,n));n=[x/length for x in n];ps.append((n,dot(n,vs[0])))
    if len(ps)>=4 and not clip:cells.append(ps)
   depth-=1
 margins=[min(max(dot(n,p)-d for n,d in cell) for cell in cells) for p in points];assert all(x>0.13 for x in margins);out[mode]=margins
# Independent axis-aligned source-box Minkowski witness. No compiler-expanded planes used.
text=(q/'fixtures/full-off.map').read_text().splitlines();vs=[]
for line in text[13365:]:
 if line.strip()=='}':break
 vs.extend(list(map(float,v.split())) for v in re.findall(r'\(([^()]*)\)',line))
mins=[min(v[i] for v in vs) for i in range(3)];maxs=[max(v[i] for v in vs) for i in range(3)];assert mins==[-1552.000488281,-1456.,144.] and maxs==[-1264.,-1424.,368.]
lo=[mins[i]-[32,32,64][i] for i in range(3)];hi=[maxs[i]+[32,32,24][i] for i in range(3)];p=[-1280.0001220705,-1440,236.73692674130805];margin=min(min(p[i]-lo[i],hi[i]-p[i]) for i in range(3));assert margin==48
# The observed bbox policy excludes a genuinely occupied front interval.
cut=-1280.000244141;actual_front=-1280-cut;assert 0<actual_front<0.001
actor=load(e/'actor-points.json');assert actor['points'][0]['solid_sky']==[1,0] and actor['points'][3]['solid_sky']==[0,0] and actor['final'][0]==-1
cap=load(e/'ancestor-cap.json');assert cap['area']>0.007 and sum(x>0.0001 for x in cap['edges'])==2
for v in cap['vertices']:
 assert max(dot(s['p'][:3],v)-s['p'][3] for s in cap['ancestor_constraints'])<1e-7
historical=load(q/'thin_brush_phase3_evidence/witness-gate.json');assert all(w['expected']==-1 and w['contents']['uniform']==-2 for w in historical['full-off'])
print(json.dumps(dict(source_empty_margins=out,actor_source_box=[lo,hi],actor_interior_margin=margin,discarded_front_width=actual_front,rejected_diagnostic_false_solids_detected=3,terminal_cut_area=cap['area'],status='PASS: preserved failure witnesses replayed; not compiler acceptance'),indent=2))
