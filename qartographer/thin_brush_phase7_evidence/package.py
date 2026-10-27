from pathlib import Path
import json,hashlib,subprocess,difflib,shutil,struct,re
base=Path('/tmp/qqbsp-phase7');s=base/'source';r=Path('/home/warrenmarshall/dev/ericw-tools');e=base/'evidence';pub=base/'publish';pub.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changed=['include/qbsp/halfspace.hh','include/qbsp/supported_geometry.hh','include/qbsp/brushbsp.hh','include/qbsp/portals.hh','qbsp/brushbsp.cc','qbsp/portals.cc','qbsp/prtfile.cc','qbsp/CMakeLists.txt','qartographer/CMakeLists.txt','tests/test_qbsp.cc','qartographer/phase5-witness.json','qartographer/phase7-cases.json']
patch='';snapshot=e/'implementation';snapshot.mkdir(exist_ok=True)
for n in changed:
 old=subprocess.run(['git','show','HEAD:'+n],cwd=r,capture_output=True,text=True)
 oldtext=old.stdout if old.returncode==0 else '';new=(s/n).read_text()
 for line in difflib.unified_diff(oldtext.splitlines(True),new.splitlines(True),fromfile='a/'+n if old.returncode==0 else '/dev/null',tofile='b/'+n):
  patch+=line if line.endswith('\n') else line+'\n\\ No newline at end of file\n'
 target=snapshot/(n+'.txt');target.parent.mkdir(exist_ok=True,parents=True);target.write_text(new)
(e/'phase7-unaccepted.patch').write_text(patch)
# Preserve exact final build and the earlier campaign ELF separately.
shutil.copy2(base/'build/qbsp/qqbsp',base/'phase7-unaccepted-qqbsp')
for p in (base/'build/qbsp').glob('libtbb*'):shutil.copy2(p,base/p.name)
rows=json.loads((e/'campaign/results.json').read_text());shutil.copy2(e/'campaign/results.json',e/'campaign/results-unannotated.json')
for row in rows:
 if row['exit']=='timeout':
  row['postprocess_path_sha256']=row.pop('binary_sha256')
  row['launch_identity_note']='The runner hashed the executable path after exit; rebuilds occurred during these incomplete runs. That postprocess hash does not identify the loaded ELF. No precise-run acceptance or exact artifact binding is claimed.'
(e/'campaign/results.json').write_text(json.dumps(rows,indent=2)+'\n')
for row in rows:
 d=e/'campaign'/row['name'];timing=(d/'time.txt').read_text();rss=re.search(r'Maximum resident set size \(kbytes\): (\d+)',timing);row['peak_rss_kib']=int(rss[1]) if rss else None
 if row['bsp_sha256']:
  raw=(d/'input.bsp').read_bytes();lumps=[struct.unpack_from('<ii',raw,4+8*i) for i in range(15)]
  row['output']=dict(bytes=len(raw),planes=lumps[1][1]//20,nodes=lumps[5][1]//24,clipnodes=lumps[9][1]//8,leaves=lumps[10][1]//28,faces=lumps[7][1]//20,models=lumps[14][1]//64,lump_bytes=[n for _,n in lumps])
(e/'campaign/summary.json').write_text(json.dumps(rows,indent=2)+'\n')
mat=json.loads((e/'thin-matrix/results.json').read_text());sup=json.loads((e/'matrix-supplement/results.json').read_text());allcases=mat|sup
allcases['rotated-default']={'compile_exit':1,'failures':[{'kind':'compile failure','log':'thin-matrix/rotated-default/compile.log'}]}
(e/'matrix-summary.json').write_text(json.dumps(dict(cases=allcases,compile_pass=sum('compile_exit' not in x for x in allcases.values()),compile_fail=sum('compile_exit' in x for x in allcases.values()),source_checks=sum(sum(x.get('counts',{}).values()) for x in allcases.values()),passing_cases=sum(not x['failures'] for x in allcases.values()),note='Original oracle and samples unchanged. Supplement aggregates compile failures instead of aborting; no failed case is skipped or accepted. Initial matrix ELF was not archived before subsequent guard edits, so these are development evidence rather than final-artifact acceptance.'),indent=2)+'\n')
installed=Path('/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp')
status=dict(base_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),final_executable=str(base/'phase7-unaccepted-qqbsp'),final_sha256=sha(base/'phase7-unaccepted-qqbsp'),campaign_executable=str(base/'campaign-qqbsp'),campaign_sha256=sha(base/'campaign-qqbsp'),tests_sha256=sha(base/'build/qartographer/qqbsp_tests'),installed_sha256=sha(installed),source_files={n:sha(s/n) for n in changed},phase6_header_original_sha256=sha(base/'phase6/component/halfspace.hpp'),source_brush_cc_unchanged=sha(s/'qbsp/brush.cc')==sha(r/'qbsp/brush.cc'),active_compiler_diff=subprocess.check_output(['git','diff','--stat'],cwd=r,text=True),p1_sha256=sha(r/'qartographer/P1.patch'),p2_sha256=sha(r/'qartographer/P2-unapplied.patch'),commit=False,push=False,deployment=False,accepted=False)
(e/'status.json').write_text(json.dumps(status,indent=2)+'\n')
for p in base.glob('*.py'):shutil.copy2(p,e/p.name)
for p in e.rglob('*.bsp'):
 shutil.copyfile(p,p.with_suffix('.bsp.bin'))
(pub/'thin_brush_phase7_evidence').mkdir(exist_ok=True)
# Only portable evidence: no PAKs/symlinks, runtime config installs, or raw debug ELF.
for p in e.rglob('*'):
 if not p.is_file() or p.is_symlink() or p.suffix in ['.bsp','.map','.wad','.pak']:continue
 dst=pub/'thin_brush_phase7_evidence'/p.relative_to(e);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
manifest={str(p.relative_to(pub)):sha(p) for p in pub.rglob('*') if p.is_file()}
(pub/'thin_brush_phase7_evidence/SHA256SUMS.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(status=status,summary=[{k:row.get(k) for k in ['name','exit','seconds','peak_rss_kib','output']} for row in rows],matrix=dict(cases=len(allcases),passes=sum(not x['failures'] for x in allcases.values()))),indent=2))
