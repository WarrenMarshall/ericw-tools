from pathlib import Path
import struct,json
out=[]
for label,p in [('P1',Path('/tmp/qqbsp-phase7/evidence/ordinary-comparison/ordinary-rotated-hull0/input.bsp')),('phase8',Path('/tmp/qqbsp-phase8/evidence/accepted-experiment-campaign/ordinary-rotated-hull0/input.bsp'))]:
 b=p.read_bytes();l=[struct.unpack_from('<ii',b,4+8*i) for i in range(15)];faces=[]
 for at in range(l[7][0],sum(l[7]),20):
  plane,side,first,count,tex=struct.unpack_from('<HHiHH',b,at);verts=[]
  for i in range(count):
   surf=struct.unpack_from('<i',b,l[13][0]+4*(first+i))[0];edge=struct.unpack_from('<HH',b,l[12][0]+4*abs(surf));v=edge[surf<0];verts.append(struct.unpack_from('<3f',b,l[3][0]+12*v))
  faces.append(dict(plane=struct.unpack_from('<4f',b,l[1][0]+20*plane),side=side,texture=struct.unpack_from('<8fii',b,l[6][0]+40*tex),vertices=verts))
 out.append(dict(name=label,faces=faces))
Path('/tmp/qqbsp-phase8/evidence/rotated-render-faces.json').write_text(json.dumps(out,indent=2))
for r in out:
 print(r['name'])
 for f in r['faces']: print(f['plane'],f['side'],f['vertices'])
