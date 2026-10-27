from pathlib import Path
import json,collections
root=Path('/tmp/qqbsp-phase4');pts=json.load(open(root/'actor-route.json'))['points'];out={}
for stage in ['source','post-csg']:
 bs=collections.defaultdict(list);lines={}
 for l in (root/f'off-extended/input.bsp.p4-{stage}2.tsv').read_text().splitlines():
  a=l.split('\t');bs[int(a[0])].append(list(map(float,a[3].split())));lines[int(a[0])]=int(a[1])
 rows=[]
 for k,(a,b) in enumerate(zip(pts,pts[1:])):
  hits=[];minmargin=(1e99,None,None)
  for idx,ps in bs.items():
   ab=[(sum(p[i]*a[i] for i in range(3))-p[3],sum(p[i]*(b[i]-a[i]) for i in range(3))) for p in ps]
   ts=[0,1]
   for j,(x,y) in enumerate(ab):
    for xx,yy in ab[:j]:
     if abs(y-yy)>1e-14:
      t=(xx-x)/(y-yy)
      if 0<t<1:ts.append(t)
   mar,t=min((max(x+t*y for x,y in ab),t) for t in ts)
   if mar<minmargin[0]:minmargin=(mar,lines[idx],t)
   lo=0;hi=1
   for x,y in ab:
    if abs(y)<1e-14:
     if x>0:hi=-1;break
    elif y>0:hi=min(hi,-x/y)
    else:lo=max(lo,-x/y)
   if hi>lo+1e-10:
    t=(lo+hi)/2;depth=-max(x+t*y for x,y in ab)
    if depth>1e-7:hits.append(dict(index=idx,line=lines[idx],lo=lo,hi=hi,depth=depth,point=[a[i]+t*(b[i]-a[i]) for i in range(3)]))
  rows.append(dict(segment=k,minmargin=minmargin,hits=hits))
 out[stage]=rows
 print(stage,'hits',[(x['segment'],x['hits']) for x in rows if x['hits']],flush=True)
(root/'actor-source-route.json').write_text(json.dumps(out,indent=2))
