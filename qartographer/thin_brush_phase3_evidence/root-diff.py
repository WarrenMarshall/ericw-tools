from pathlib import Path
import json,math
r=Path('/tmp/qqbsp-phase3')
def read(name,stage):
 d={}
 for l in (r/('target-'+name)/('full-on.bsp.'+stage+'.tsv')).read_text().splitlines():
  line,pl,p,vs=l.split('\t');d[(int(line),int(pl))]=dict(plane=list(map(float,p.split())),vertices=[list(map(float,v.split())) for v in vs.split(';') if v])
 return d
out={}
for st in ['root-input','root-front','root-back']:
 a=read('p1',st);b=read('uniform',st);changes=[]
 for k in a.keys()|b.keys():
  if a.get(k)!=b.get(k):
   x=a.get(k);y=b.get(k)
   changes.append(dict(line=k[0],plane=k[1],p1=x,uniform=y))
 out[st]=dict(p1_sides=len(a),uniform_sides=len(b),changed_sides=len(changes),changes=changes)
print({st:{k:v for k,v in row.items() if k!='changes'} for st,row in out.items()})
print(json.dumps(out['root-front']['changes'][:2],indent=2));(r/'root-diff.json').write_text(json.dumps(out,indent=2))
