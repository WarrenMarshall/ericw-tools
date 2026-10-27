import pathlib,json
r=pathlib.Path('/tmp/qqbsp-phase3')
def read(p):
 d={}
 for l in p.read_text().splitlines():
  a=l.split('\t')
  if len(a)==6:d[a[0]]=a[1:]
 return d
p=read(r/'trace-p1/full-on.bsp.tree1.tsv');q=read(r/'trace-uniform/full-on.bsp.tree1.tsv')
shared=[''];diffs=[];same=0
while shared:
 path=shared.pop(0)
 if path not in p or path not in q:continue
 a=p[path];b=q[path]
 if a!=b:
  diffs.append(dict(path=path,p1=a,uniform=b));continue
 same+=1
 if a[2]!='L':shared.extend([path+'0',path+'1'])
print('nodes',len(p),len(q),'equal prefixes',same,'divergences',len(diffs));print(json.dumps(diffs[:5],indent=2))
(r/'first-divergences.json').write_text(json.dumps(dict(p1_records=len(p),uniform_records=len(q),equal_prefix_nodes=same,divergences=diffs),indent=2))
