from pathlib import Path
import sys,json,struct
sys.dont_write_bytecode=True
sys.path.insert(0,'/tmp/qqbsp-phase7/phase6/component')
from oracle import analyze,range_on_plane
base=Path('/tmp/qqbsp-phase8/evidence');out=[]
paths=[('Halloween-original',base/'reproduction/halloween/node.json.fragment.json'),('P1-original-CSG',base/'reproduction/p1/node.json.fragment.json'),('rotated-original-node82',base/'reproduction/sealed-test/node.json.fragment.json'),('Halloween-final',base/'accepted-experiment-campaign/halloween-off-auto/node.json.fragment.json'),('P1-final-no-route',base/'accepted-experiment-campaign/p1-reduced/node.json.no-route.json'),('Roller-final',base/'roller-context/node.json.fragment.json')]
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
for name,p in paths:
 c=json.loads(p.read_text());c['planes']=list({tuple(ps) for ps in c['planes']});result=dict(name=name,path=str(p),constraints=len(c['planes']),query=c['query'])
 result['binary64']=analyze(c);result['float32']=analyze(dict(planes=[[f32(v) for v in ps] for ps in c['planes']],query=[f32(v) for v in c['query']]))
 if name!='P1-final-no-route':result['extent']=range_on_plane(c['planes'],c['query'])
 out.append(result);print(result,flush=True);(base/'remaining-oracle.json').write_text(json.dumps(out,indent=2))
