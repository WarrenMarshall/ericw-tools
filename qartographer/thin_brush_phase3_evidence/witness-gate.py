import pathlib,re,json,sys
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/warrenmarshall/dev/ericw-tools/qartographer');import spline_smooth_collision_compile as c
r=pathlib.Path('/tmp/qqbsp-phase3');repo=pathlib.Path('/home/warrenmarshall/dev/ericw-tools');pts=[x['point'] for x in json.load(open(repo/'qartographer/thin_brush_phase2_evidence/map-witnesses.json'))['full-on']];out={}
for mode in ['full-on','full-off']:
 text=(repo/'qartographer/fixtures'/(mode+'.map')).read_text();depth=0;cells=[]
 for m in re.finditer(r'^\s*[{}]\s*$',text,re.M):
  if m[0].strip()=='{':
   depth+=1
   if depth==2:start=m.end()
  else:
   if depth==2:
    body=text[start:m.start()];planes=[];clip=False
    for line in body.splitlines():
     vs=[tuple(map(float,s.split())) for s in re.findall(r'\(([^()]*)\)',line)]
     if len(vs)!=3:continue
     clip|=bool(re.search(r'\) CLIP ',line));n=c.norm(c.cross(c.sub(vs[0],vs[1]),c.sub(vs[2],vs[1])));planes.append((n,c.dot(n,vs[0])))
    if len(planes)>=4 and not clip:cells.append(planes)
   depth-=1
 bs={n:c.BSP(r/n/mode/(mode+'.bsp')) for n in ['stock','p1','uniform']}
 out[mode]=[dict(point=p,source_margin=c.margin(p,cells),expected=-1,contents={n:b.contents(p,hull=0) for n,b in bs.items()}) for p in pts]
print(out);(r/'witness-gate.json').write_text(json.dumps(out,indent=2))
