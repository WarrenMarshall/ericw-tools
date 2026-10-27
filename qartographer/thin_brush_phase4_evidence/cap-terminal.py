exec(open('/tmp/qqbsp-phase4/terminal.py').read().split('r=dict(')[0])
cv=[]
for a,b in itertools.combinations([s['p'] for s in vol],2):
 det=dot(q[:3],cross(a[:3],b[:3]))
 if abs(det)<1e-12:continue
 v=[(q[3]*cross(a[:3],b[:3])[i]+a[3]*cross(b[:3],q[:3])[i]+b[3]*cross(q[:3],a[:3])[i])/det for i in range(3)]
 if max(dist(s['p'],v) for s in vol)<1e-7 and all(math.dist(v,x)>1e-7 for x in cv):cv.append(v)
c=[sum(v[i] for v in cv)/len(cv) for i in range(3)];u=[cv[0][i]-c[i] for i in range(3)];l=math.sqrt(dot(u,u));u=[x/l for x in u];v=cross(q[:3],u)
cv.sort(key=lambda x:math.atan2(dot([x[i]-c[i] for i in range(3)],v),dot([x[i]-c[i] for i in range(3)],u)))
area=abs(sum(dot(q[:3],cross([a[i]-c[i] for i in range(3)],[b[i]-c[i] for i in range(3)])) for a,b in zip(cv,cv[1:]+cv[:1])))/2
row=dict(vertices=cv,area=area,edges=[math.dist(a,b) for a,b in zip(cv,cv[1:]+cv[:1])],max_halfspace_residual=max(dist(s['p'],v) for s in vol for v in cv))
print(json.dumps(row,indent=2));open('/tmp/qqbsp-phase4/terminal-cap.json','w').write(json.dumps(row,indent=2))
