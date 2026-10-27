import pathlib,re,json,sys,math
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/warrenmarshall/dev/ericw-tools/qartographer')
import spline_smooth_collision_compile as c
root=pathlib.Path('/tmp/qqbsp-phase3'); old=pathlib.Path('/tmp/qqbsp-phase2/uniform-regression/patched/full')
rows={}
for mode in ['full-on','full-off']:
 text=(old/(mode+'.map')).read_text();cells=[]
 # explicit brace depth: restrict to worldspawn; bmodels do not seal world
 depth=0;start=0; entity=-1
 for match in re.finditer(r'[{}]',text):
  if match[0]=='{':
   depth+=1
   if depth==1:entity+=1
   if depth==2:start=match.end()
  else:
   if depth==2 and entity==0:
    body=text[start:match.start()];planes=[];textures=[]
    for line in body.splitlines():
     vs=[tuple(map(float,m.split())) for m in re.findall(r'\(([^()]*)\)',line)]
     if len(vs)!=3:continue
     n=c.norm(c.cross(c.sub(vs[0],vs[1]),c.sub(vs[2],vs[1])))
     planes.append((n,c.dot(n,vs[0])));textures.append(re.split(r'\)\s*',line)[-1].split()[0])
    if len(planes)>=4 and not any(t.upper() in ['CLIP','HINT','HINTSKIP'] or t.startswith('*') for t in textures):
     cells.append(dict(line=text.count('\n',0,start)+1,planes=planes,textures=textures))
   depth-=1
 pts=[tuple(map(float,l.split())) for l in (old/(mode+'.pts')).read_text().splitlines()];pts=[p for i,p in enumerate(pts) if i==0 or p!=pts[i-1]]
 if '--detour' in sys.argv:
  pts=[(p[0]-0.5,p[1],p[2]) if abs(p[0]+1727.99987793)<1e-6 else p for p in pts]
 hits=[];margins=[];segment_clearances=[]
 for k,(a,b) in enumerate(zip(pts,pts[1:])):
  v=c.sub(b,a)
  best=(1e99,None,None)
  for cell in cells:
   lines=[(c.dot(n,a)-d,c.dot(n,v)) for n,d in cell['planes']]
   ts=[0.,1.]
   for i,(x,y) in enumerate(lines):
    for xx,yy in lines[:i]:
     if abs(y-yy)>1e-14:
      t=(xx-x)/(y-yy)
      if 0<t<1:ts.append(t)
   mar,t=min((max(x+t*y for x,y in lines),t) for t in ts)
   if mar<best[0]:best=(mar,cell['line'],t)
   lo=0.;hi=1.
   for n,d in cell['planes']:
    x=c.dot(n,a)-d;y=c.dot(n,v)
    if abs(y)<1e-14:
     if x>0:hi=-1;break
    elif y>0:hi=min(hi,-x/y)
    else:lo=max(lo,-x/y)
   if hi>lo+1e-10:
    t=(lo+hi)/2;p=tuple(a[i]+t*v[i] for i in range(3));depth=-max(c.dot(n,p)-d for n,d in cell['planes'])
    if depth>1e-7:hits.append(dict(segment=k,line=cell['line'],lo=lo,hi=hi,point=p,depth=depth,textures=cell['textures']))
  segment_clearances.append(dict(segment=k,minimum_source_margin=best[0],nearest_line=best[1],t=best[2]))
  for t in [0,.25,.5,.75,1]:
   p=tuple(a[i]+t*v[i] for i in range(3));mar=min(max(c.dot(n,p)-d for n,d in cell['planes']) for cell in cells)
   margins.append(dict(segment=k,t=t,point=p,source_margin=mar))
 rows[mode]=dict(points=pts,source_cells=len(cells),solid_segment_intersections=hits,samples=margins,segment_clearances=segment_clearances)
(root/('leak-detour.json' if '--detour' in sys.argv else 'leak-oracle.json')).write_text(json.dumps(rows,indent=2));print({m:dict(points=len(v['points']),hits=v['solid_segment_intersections']) for m,v in rows.items()})
