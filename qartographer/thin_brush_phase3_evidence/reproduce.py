import pathlib,subprocess,time,json,hashlib,struct,shutil
r=pathlib.Path('/tmp/qqbsp-phase3'); src=pathlib.Path('/home/warrenmarshall/dev/ericw-tools')
bins={'stock':'/tmp/qqbsp-bootstrap/pinned/pristine-build/qbsp/qbsp','p1':'/tmp/qqbsp-bootstrap/pinned/patched-build/qbsp/qqbsp','uniform':'/tmp/qqbsp-phase2/uniform-epsilon-qqbsp'}
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
rows=[]
for mode in ['full-on','full-off']:
 for name in bins:
  for nofill in ([False,True] if name=='p1' else [False]):
   out=r/(name+('-nofill' if nofill else ''))/mode;out.mkdir(parents=True,exist_ok=True)
   m=out/(mode+'.map');shutil.copyfile(src/'qartographer/fixtures'/(mode+'.map'),m)
   args=[bins[name],'-bsp2','-notex','-nopercent','-chopfragment','-threads','1']+(['-nofill'] if nofill else [])+[str(m)]
   t=time.monotonic()
   with (out/'stdout.log').open('w') as f: p=subprocess.run(['/usr/bin/time','-v','-o',str(out/'time.txt')]+args,stdout=f,stderr=subprocess.STDOUT)
   b=m.with_suffix('.bsp'); data=b.read_bytes(); lumps=[struct.unpack_from('<ii',data,4+8*i) for i in range(15)]
   row=dict(compiler=name,nofill=nofill,mode=mode,command=args,exit=p.returncode,elapsed=time.monotonic()-t,binary_sha256=sha(bins[name]),map_sha256=sha(m),bsp_sha256=sha(b),bytes=len(data),lump_bytes=[x[1] for x in lumps],nodes=lumps[5][1]//44,leaves=lumps[10][1]//44,clipnodes=lumps[9][1]//12,faces=lumps[7][1]//28,models=lumps[14][1]//64)
   rows.append(row);(r/'reproduction.json').write_text(json.dumps(rows,indent=2));print(name,mode,nofill,row['bytes'],flush=True)
