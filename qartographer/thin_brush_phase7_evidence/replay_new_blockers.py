from pathlib import Path
import sys,json,struct
sys.dont_write_bytecode=True
base=Path('/tmp/qqbsp-phase7');sys.path.insert(0,str(base/'phase6/component'))
from oracle import analyze,range_on_plane
rows=[]
for name,p in [('P1-next-CSG',base/'evidence/campaign/p1-reduced/node.json.fragment.json'),('rotated-room-next-node',base/'evidence/sealed-node.json.fragment.json')]:
 case=json.loads(p.read_text());out=analyze(case);extent=range_on_plane(case['planes'],case['query'])
 f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
 quant=dict(planes=[[f32(v) for v in p] for p in case['planes']],query=[f32(v) for v in case['query']])
 row=dict(name=name,source=str(p),binary64=out,extent=extent,binary32=analyze(quant));rows.append(row)
 (base/'evidence/new-blocker-oracle.json').write_text(json.dumps(rows,indent=2)+'\n');print(row,flush=True)
