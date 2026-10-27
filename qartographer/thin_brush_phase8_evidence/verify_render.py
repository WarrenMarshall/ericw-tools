from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import json,math
base=Path('/tmp/qqbsp-phase8/evidence');data=json.loads((base/'rotated-render-faces.json').read_text())
groups=[]
for r in data:
 g=defaultdict(list)
 for f in r['faces']:g[(tuple(f['plane']),f['side'],tuple(f['texture']))].append(f)
 groups.append(g)
results=[]
for k,old in groups[0].items():
 new=groups[1][k];axis=max(range(3),key=lambda i:abs(k[0][i]));project=lambda p:tuple(Q(v) for i,v in enumerate(p) if i!=axis)
 points=set(project(p) for f in old+new for p in f['vertices'])
 def edges(faces):
  result=Counter()
  for f in faces:
   ps=list(map(project,f['vertices']))
   for a,b in zip(ps,ps[1:]+ps[:1]):
    delta=tuple(b[i]-a[i] for i in range(2));j=max(range(2),key=lambda i:abs(delta[i]))
    if not delta[j]:continue
    ts={Q(0):a,Q(1):b}
    for p in points:
     t=(p[j]-a[j])/delta[j]
     if 0<t<1 and all(p[i]==a[i]+t*delta[i] for i in range(2)):ts[t]=p
    splits=[ts[t] for t in sorted(ts)]
    for x,y in zip(splits,splits[1:]):
     if result[(y,x)]:result[(y,x)]-=1
     else:result[(x,y)]+=1
  return +result
 same=edges(old)==edges(new)
 results.append(dict(plane=k[0],old_faces=len(old),new_faces=len(new),identical_texture_vectors_and_flags=True,exact_projected_boundary_edge_cancellation=same))
changed=[r for r in results if r['old_faces']!=r['new_faces']]
assert len(changed)==1 and changed[0]['exact_projected_boundary_edge_cancellation']
(base/'rotated-render-verification.json').write_text(json.dumps(dict(groups=results,extra_face_has_identical_projected_union_and_texture_mapping=True,limitation='One other floor boundary gains a float32-rounded T-junction vertex; no textured/native rendering acceptance is claimed.'),indent=2));print(results)
