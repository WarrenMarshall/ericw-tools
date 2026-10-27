import json,pathlib
r=pathlib.Path('/tmp/qqbsp-phase3');tree={}
for l in (r/'trace-p1/full-on.bsp.tree1.tsv').read_text().splitlines():
 a=l.split('\t');tree[a[0]]=a[1:]
rows=[];paths=set()
def rec(path,a,v,lo,hi,k):
 row=tree[path]
 if row[2]=='L':
  if hi-lo>1e-12:rows.append(dict(segment=k,path=path,lo=lo,hi=hi,brushes=int(row[0]),point=[a[i]+(lo+hi)/2*v[i] for i in range(3)]));paths.add(path)
  return
 p=list(map(float,row[3].split()));x=sum(p[i]*a[i] for i in range(3))-p[3];y=sum(p[i]*v[i] for i in range(3))
 if abs(y)<1e-16:rec(path+('0' if x>=0 else '1'),a,v,lo,hi,k);return
 t=-x/y
 if t<=lo or t>=hi:rec(path+('0' if x+(lo+hi)/2*y>=0 else '1'),a,v,lo,hi,k)
 else:rec(path+('0' if y<0 else '1'),a,v,lo,t,k);rec(path+('0' if y>0 else '1'),a,v,t,hi,k)
v=json.load(open(r/'leak-detour.json'))['full-on']
for k,(a,b) in enumerate(zip(v['points'],v['points'][1:])):rec('',a,[b[i]-a[i] for i in range(3)],0,1,k)
(r/'route-leaves.txt').write_text('\n'.join(sorted(paths))+'\n');(r/'route-tree.json').write_text(json.dumps(rows,indent=2));print(len(rows),len(paths),'nonzero brush leaves',sum(x['brushes']>0 for x in rows))
