from pathlib import Path
import json,collections,math
r=Path('/tmp/qqbsp-phase4/off');pts=[(-1388,-233,8.778914155553586),(-1376,-257,-12.914510661888684),(-1364,-269,11.605075569064333)]
nodes={};cur=None
for l in (r/'input.bsp.p4.tsv').read_text().splitlines():
 a=l.split('\t')
 if a[0]=='NODE':
  cur=(int(a[1]),a[2],a[4]);nodes[cur]={'mask':int(a[3]),'count':int(a[5]),'sides':collections.defaultdict(list)}
 elif a[0]=='SIDE':
  nodes[cur]['sides'][int(a[3])].append({'plane':int(a[4]),'onnode':int(a[5]),'bevel':int(a[6]),'visible':int(a[7]),'p':list(map(float,a[8].split())),'w':[list(map(float,v.split())) for v in a[9].split(';') if v]})
rows=[]
for (ps,path,stage),n in nodes.items():
 if ps!=1:continue
 b=[]
 for line,ss in n['sides'].items():
  if line==-1:continue
  margins=[max(sum(s['p'][i]*p[i] for i in range(3))-s['p'][3] for s in ss) for p in pts]
  b.append(dict(line=line,margins=margins))
 if len(path)>19 or stage=='leaf':rows.append(dict(path=path,stage=stage,count=n['count'],brushes=b))
print(json.dumps(rows,indent=2));Path('/tmp/qqbsp-phase4/witness-paths.json').write_text(json.dumps(rows,indent=2))
Path('/tmp/qqbsp-phase4/nodes.json').write_text(json.dumps([dict(pass_=ps,path=path,stage=stage,**n) for (ps,path,stage),n in nodes.items()]))
