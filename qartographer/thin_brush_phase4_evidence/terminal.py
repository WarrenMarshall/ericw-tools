import json,itertools,math
ns=json.load(open('/tmp/qqbsp-phase4/nodes.json'));pts=[(-1388,-233,8.778914155553586),(-1376,-257,-12.914510661888684),(-1364,-269,11.605075569064333)]
n=next(n for n in ns if n['pass_']==1 and n['stage']=='leaf');vol=n['sides']['-1'];q=next(s['p'] for s in n['sides']['15143'] if s['plane']==7275);q=[-x for x in q]
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
dist=lambda q,v:dot(q[:3],v)-q[3]
verts=[]
for a,b,c in itertools.combinations([s['p'] for s in vol],3):
 det=dot(a[:3],cross(b[:3],c[:3]))
 if abs(det)<1e-12:continue
 v=[(a[3]*cross(b[:3],c[:3])[i]+b[3]*cross(c[:3],a[:3])[i]+c[3]*cross(a[:3],b[:3])[i])/det for i in range(3)]
 if max(dist(s['p'],v) for s in vol)<1e-7:verts.append(v)
r=dict(path=n['path'],candidate=7274,plane=q,winding_extents=[min(dist(q,v) for s in vol for v in s['w']),max(dist(q,v) for s in vol for v in s['w'])],halfspace_vertices=verts,halfspace_extents=[min(dist(q,v) for v in verts),max(dist(q,v) for v in verts)],winding_halfspace_error=max(dist(t['p'],v) for s in vol for v in s['w'] for t in vol),point_distances=[dist(q,p) for p in pts])
# all node volume winding residuals at path; locate earliest disagreement
r['volume_path']=[]
for n in ns:
 if n['pass_']!=1 or n['stage']!='before':continue
 ss=n['sides'].get('-1',[])
 r['volume_path'].append(dict(path=n['path'],error=max(dist(t['p'],v) for s in ss for v in s['w'] for t in ss)))
print(json.dumps(r,indent=2));open('/tmp/qqbsp-phase4/terminal.json','w').write(json.dumps(r,indent=2))
