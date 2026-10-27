from pathlib import Path
import subprocess,shutil,hashlib,json,os,time
base=Path('/tmp/qqbsp-phase8');s=base/'source';e=base/'evidence/revision3';e.mkdir(exist_ok=False)
r=Path('/home/warrenmarshall/dev/ericw-tools');binary=base/'revision3-qqbsp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cases=[('p1-reduced',r/'qartographer/fixtures/reduced.map',[]),('rotated-actors',s/'testmaps/qbsp_simple_sealed_rotated.map',[]),('ordinary',s/'testmaps/qbsp_simple_sealed.map',[]),('ordinary-rotated-hull0',s/'testmaps/qbsp_simple_sealed_rotated.map',['-noclip']),('ordinary-L-room',s/'testmaps/qbsp_simple_sealed2.map',[]),('halloween-off-auto',r/'qartographer/fixtures/full-off.map',[]),('halloween-on-auto',r/'qartographer/fixtures/full-on.map',[]),('halloween-off-precise',r/'qartographer/fixtures/full-off.map',['-forcegoodtree']),('halloween-on-precise',r/'qartographer/fixtures/full-on.map',['-forcegoodtree'])]
rows=[]
for name,source,flags in cases[:5]:
 d=e/name;d.mkdir();m=d/'input.map';shutil.copyfile(source,m)
 cmd=['/usr/bin/time','-v','-o',str(d/'time.txt'),str(binary),'-notex','-nopercent','-chopfragment','-threads','1',*flags,str(m)]
 env=os.environ.copy();env['QQBSP_PHASE7_CAPTURE']=str(d/'node.json')
 start=time.monotonic()
 with (d/'stdout.log').open('w') as f:
  try:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=900);rc=p.returncode
  except subprocess.TimeoutExpired:rc='timeout'
 row=dict(name=name,command=cmd,exit=rc,seconds=time.monotonic()-start,input_sha256=sha(m),source_sha256=sha(source),binary_sha256=sha(binary),bsp_sha256=sha(m.with_suffix('.bsp')) if m.with_suffix('.bsp').exists() else None)
 rows.append(row);(e/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(name,rc,row['seconds'],flush=True)
