from pathlib import Path
import json
r=Path('/tmp/qqbsp-phase4/off');out={};trees={}
for ps in [4,5]:
 t={}
 for l in (r/f'input.bsp.tree{ps}.tsv').read_text().splitlines():
  a=l.split('\t');t[a[0]]={'count':int(a[1]),'plane':None if a[3]=='L' else list(map(float,a[4].split())),'source':a[5]}
 trees[ps]=t
rows=[l.split('\t') for l in (r/'input.bsp.p4-leak2.tsv').read_text().splitlines()];pts=[list(map(float,rows[0][1].split()))]+[list(map(float,a[3].split())) for a in rows[1:]]
def dot(p,v):return sum(p[i]*v[i] for i in range(3))
def route(t,a,b):
 result=[];v=[b[i]-a[i] for i in range(3)]
 def rec(path,lo,hi):
  n=t[path];p=n['plane']
  if p is None:
   result.append(dict(path=path,lo=lo,hi=hi,count=n['count'],point=[a[i]+(lo+hi)/2*v[i] for i in range(3)]));return
  x=dot(p,a)-p[3];y=dot(p,v);cut=-x/y if y else -1
  if lo+1e-12<cut<hi-1e-12:rec(path+('1' if y>0 else '0'),lo,cut);rec(path+('0' if y>0 else '1'),cut,hi)
  else:rec(path+('0' if x+(lo+hi)/2*y>=0 else '1'),lo,hi)
 rec('',0,1);return result
for ps,t in trees.items():
 out[str(ps)]={'segments':[dict(segment=k,intervals=route(t,a,b)) for k,(a,b) in enumerate(zip(pts,pts[1:]))]}
# containment per route portal
portals=[]
for k,a in enumerate(rows[1:]):
 vs=[list(map(float,v.split())) for v in a[4].split(';') if v];err=[]
 for leaf in a[1:3]:
  for d,ch in enumerate(leaf):
   p=trees[5][leaf[:d]]['plane'];e=max((dot(p,v)-p[3])*(1 if ch=='1' else -1) for v in vs)
   if e>1e-7:err.append(dict(leaf=leaf,ancestor=leaf[:d],side=ch,plane=p,error=e))
 portals.append(dict(index=k,errors=err))
out['portals']=portals;out['points']=pts
Path('/tmp/qqbsp-phase4/actor-route.json').write_text(json.dumps(out,indent=2))
for ps in [4,5]:
 bad=[(s['segment'],i['path'],i['count'],i['point']) for s in out[str(ps)]['segments'] for i in s['intervals'] if i['count']]
 print(ps,'nonempty region intervals',len(bad),'first',bad[:4])
print('portal violations',[(p['index'],max(x['error'] for x in p['errors'])) for p in portals if p['errors']])
