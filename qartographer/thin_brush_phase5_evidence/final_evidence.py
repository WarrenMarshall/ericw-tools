from pathlib import Path
import subprocess,shutil,hashlib,json,sys,re,struct,difflib
r=Path('/home/warrenmarshall/dev/ericw-tools');base=Path('/tmp/qqbsp-phase5');e=base/'evidence';s=base/'source';binary=base/'build/qbsp/qqbsp'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Archive the exact final executable; no further source changes follow this receipt.
shutil.copy2(binary,base/'phase5-unaccepted-qqbsp')
rows=[]
for name,src in [('thin-original',r/'qartographer/fixtures/thin-direct/original.map'),('p1-reduced',r/'qartographer/fixtures/reduced.map'),('halloween-off',r/'qartographer/fixtures/full-off.map'),('halloween-on',r/'qartographer/fixtures/full-on.map')]:
 d=e/('candidate-'+name);d.mkdir();m=d/'input.map';shutil.copyfile(src,m)
 cmd=['/usr/bin/time','-v','-o',str(d/'time.txt'),str(binary),'-bsp2','-notex','-nopercent','-chopfragment','-threads','1',str(m)]
 with (d/'stdout.log').open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 text=(d/'stdout.log').read_text();timing=(d/'time.txt').read_text()
 row=dict(name=name,command=cmd,exit=p.returncode,map_sha256=sha(m),binary_sha256=sha(binary),bsp=None,errors=re.findall(r'PHASE5 (?:NUMERICAL_UNCERTAINTY|UNCERTIFIED_[A-Z]+)[^\n]*',text),time_receipt=timing)
 if m.with_suffix('.bsp').exists():
  raw=m.with_suffix('.bsp').read_bytes();lumps=[struct.unpack_from('<ii',raw,4+8*i) for i in range(15)]
  row['bsp']=dict(bytes=len(raw),sha256=sha(m.with_suffix('.bsp')),version=raw[:4].hex(),lump_bytes=[n for _,n in lumps]);shutil.copy2(m.with_suffix('.bsp'),d/'input.bsp.bin')
 rows.append(row)
(e/'candidate-compiles.json').write_text(json.dumps(rows,indent=2)+'\n')
# Independent source-occupancy checks on the successfully emitted original fixture.
sys.dont_write_bytecode=True;sys.path.insert(0,str(r/'qartographer'))
import spline_smooth_collision_compile as c
from wildspline_bsp_collision_compile import brushes,expanded
m=e/'candidate-thin-original/input.map';g=brushes(m.read_text());b=c.BSP(m.with_suffix('.bsp'));checks=[]
for hull,radius,offset in [(0,(0,0,0),0),(1,(16,16,28),4),(2,(32,32,44),20)]:
 cells=[expanded(v,radius) for v in g]
 for point in [(0,32,0),(0,32,1),(0,32,10),(0,32,-10),(40,32,0),(0,32,128)]:
  margin=c.margin(point,cells);expected=-2 if margin<0 else -1;actual=b.contents((point[0],point[1],point[2]-offset),hull=hull)
  checks.append(dict(hull=hull,point=point,source_margin=margin,expected=expected,actual=actual,pass_=actual==expected))
(e/'original-source-occupancy.json').write_text(json.dumps(dict(checks=checks,pass_=all(x['pass_'] for x in checks)),indent=2)+'\n')
# Exact inert patch and full changed source files for recovery, not applied to P1.
changed=['include/qbsp/supported_geometry.hh','include/qbsp/brushbsp.hh','qbsp/brushbsp.cc','qbsp/portals.cc','qbsp/CMakeLists.txt','tests/test_qbsp.cc']
patch='';snapshot=e/'implementation';snapshot.mkdir()
for n in changed:
 old=(r/n).read_text() if (r/n).exists() else '';new=(s/n).read_text()
 patch+=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+n if old else '/dev/null',tofile='b/'+n))
 target=snapshot/(n+'.txt');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(new)
(e/'phase5-unaccepted.patch').write_text(patch)
shutil.copy2(s/'qartographer/phase5-witness.json',e/'phase5-witness.json')
installed=Path('/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp')
status=dict(source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),candidate_sha256=sha(binary),tests_sha256=sha(base/'build/qartographer/qqbsp_tests'),source_files={n:sha(s/n) for n in changed},installed_sha256=sha(installed),active_diff=subprocess.check_output(['git','diff','--stat'],cwd=r,text=True),p1_sha256=sha(r/'qartographer/P1.patch'),p2_sha256=sha(r/'qartographer/P2-unapplied.patch'),commit=False,push=False,deployment=False,p2_applied=False,accepted=False,recommendation='revise',remaining='Halfspace extent certification, boundary closure/conditioning, terminal coverage, portal rank and full regression gates remain incomplete.')
(e/'candidate-status.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(dict(candidate=status['candidate_sha256'],compiles=[(x['name'],x['exit'],x['errors']) for x in rows],source_occupancy=all(x['pass_'] for x in checks)),indent=2))
