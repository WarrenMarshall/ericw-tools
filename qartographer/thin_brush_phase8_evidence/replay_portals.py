from pathlib import Path
import json,sys,struct
sys.dont_write_bytecode=True
sys.path.insert(0,'/tmp/qqbsp-phase7/phase6/component')
from oracle import rows,dimension
out=[]
for name,path in [('p1',Path('/tmp/qqbsp-phase8/evidence/final-campaign/p1-reduced/node.json.portal.json')),('rotated-matrix',Path('/tmp/qqbsp-phase8/evidence/final-matrix/rotated-default/node.json.portal.json'))]:
 d=json.loads(path.read_text());q=d['query'];ps=d['planes']
 ps=list({tuple(p) for p in ps})
 f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
 r=dict(name=name,source=str(path),distinct_constraints=len(ps),contents=[n['contents'] for n in d['nodes']])
 for model,convert in [('binary64',lambda x:x),('float32',f32)]:
  p=[[convert(x) for x in p] for p in ps];plane=[convert(x) for x in q]
  r[model+'_section_dimension']=dimension(rows(p+[plane,[-x for x in plane]]))
 out.append(r);print(r,flush=True)
 Path('/tmp/qqbsp-phase8/evidence/portal-oracle.json').write_text(json.dumps(out,indent=2))
