from pathlib import Path
import subprocess,json
out=Path('/tmp/qqbsp-phase2/traces');out.mkdir(exist_ok=True)
for name in ['axis-0','axis-1','rotated','overlap','adjacent','near-coplanar']:
 for mode in ['default','chopfragment'] if name in ['overlap','near-coplanar'] else ['default']:
  d=out/(name+'-'+mode);d.mkdir(exist_ok=True)
  p=d/'input.map';p.write_bytes((Path('/tmp/qqbsp-p3/prototype-matrix')/(name+'-'+mode)/'input.map').read_bytes())
  with (d/'trace.log').open('w') as f:
   r=subprocess.run(['/tmp/qqbsp-p3/build/qbsp/qqbsp','-threads','1',*(['-chopfragment'] if mode=='chopfragment' else []),'-bsp2','-notex','-nopercent',str(p)],stdout=f,stderr=subprocess.STDOUT)
  print(name,mode,r.returncode)
