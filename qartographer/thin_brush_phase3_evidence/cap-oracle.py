import json,pathlib,math
r=pathlib.Path('/tmp/qqbsp-phase3');sides=[]
import re,sys
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/warrenmarshall/dev/ericw-tools/qartographer');import spline_smooth_collision_compile as c
lines=pathlib.Path('/home/warrenmarshall/dev/ericw-tools/qartographer/fixtures/full-on.map').read_text().splitlines()
for line in lines[9168:]:
 if line.strip()=='}':break
 vs=[tuple(map(float,v.split())) for v in re.findall(r'\(([^()]*)\)',line)]
 if len(vs)==3:
  n=c.norm(c.cross(c.sub(vs[0],vs[1]),c.sub(vs[2],vs[1])));sides.append([*n,c.dot(n,vs[0])])
w=[[-1e5,-1e5,220],[1e5,-1e5,220],[1e5,1e5,220],[-1e5,1e5,220]]
for p in sides:
 out=[]
 for a,b in zip(w,w[1:]+w[:1]):
  da=sum(p[i]*a[i] for i in range(3))-p[3];db=sum(p[i]*b[i] for i in range(3))-p[3]
  if da<=0:out.append(a)
  if (da<0<db) or (db<0<da):out.append([a[i]+da/(da-db)*(b[i]-a[i]) for i in range(3)])
 w=out
area=lambda w:abs(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(w,w[1:]+w[:1])))/2
row=dict(source_line=9169,partition_z=220,independent_cap=w,independent_area=area(w))
d=json.load(open(r/'root-diff.json'))['root-front']['changes'][0]
for name in ['p1','uniform']:
 vs=d[name]['vertices'];row[name]=dict(area=area(vs),max_nearest_vertex_error=max(min(math.dist(v,x) for x in w) for v in vs),max_source_halfspace_violation=max(sum(p[i]*v[i] for i in range(3))-p[3] for p in sides for v in vs))
print(row);(r/'cap-oracle.json').write_text(json.dumps(row,indent=2))
