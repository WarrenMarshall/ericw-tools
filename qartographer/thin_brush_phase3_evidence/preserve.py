from pathlib import Path
import shutil,json,hashlib,subprocess,re,difflib
r=Path('/tmp/qqbsp-phase3');repo=Path('/home/warrenmarshall/dev/ericw-tools');out=r/'deliverables/thin_brush_phase3_evidence';out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in ['reproduction.json','growth.json','root-diff.json','cap-oracle.json','first-divergences.json','first-partitions.json','leak-oracle.json','leak-detour.json','leak-bsp.json','sky-ancestors.json','witness-gate.json','stage-fingerprints.json','stage-fingerprints-off.json']:
 shutil.copyfile(r/name,out/name)
for p in r.glob('*.py'):shutil.copyfile(p,out/p.name)
shutil.copyfile(r/'configure.sh',out/'configure.sh');shutil.copyfile(r/'configure.log',out/'configure.log')
for n in ['stock','p1','p1-nofill','uniform']:
 for mode in ['full-on','full-off']:
  d=r/n/mode;dest=out/'compiles'/n/mode;dest.mkdir(parents=True,exist_ok=True)
  for f in ['stdout.log','time.txt',mode+'.pts',mode+'.leak.prt']:
   if (d/f).exists():shutil.copyfile(d/f,dest/f)
for n in ['trace-p1','trace-uniform','trace-off-p1','trace-off-uniform','nofill-hull0']:
 dest=out/'instrumented-logs'/n;dest.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/n/'stdout.log',dest/'stdout.log')
# bounded targeted evidence, all logs retained privately
with (out/'targeted-decisions.log').open('w') as f:
 for n in ['final-p1','final-uniform']:
  f.write(n+'\n')
  text=re.sub(r'\x1b\[[0-9;]*m','',(r/n/'stdout.log').read_text())
  for line in text.splitlines():
   if re.search(r'P3 CAND pass=1 path=(0101010|01110101000111110) ',line) or 'P3 LEAKPORTAL' in line or 'P3 LEAFBRUSH' in line:f.write(line+'\n')
# actual final logging-only source snapshot, uniform includes rejected diagnostic policies
source=out/'instrumentation-source';source.mkdir(exist_ok=True)
for n in ['brushbsp.cc','qbsp.cc','portals.cc','outside.cc']:shutil.copyfile(r/'source/qbsp'/n,source/n)
shutil.copyfile(r/'p1-target-brushbsp.cc',source/'p1-target-brushbsp.cc')
for name in ['pristine-manifest.json','patched-manifest.json']:shutil.copyfile(Path('/tmp/qqbsp-bootstrap/pinned')/name,out/name)
ids={}
for p in [repo/'qbsp/brush.cc',repo/'qbsp/brushbsp.cc',repo/'qartographer/P2-unapplied.patch',repo/'qartographer/fixtures/full-on.map',repo/'qartographer/fixtures/full-off.map',Path('/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp')]+list(r.glob('*qqbsp')):
 ids[str(p)]=sha(p)
status=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),initial_and_prepublication_status=subprocess.check_output(['git','status','--porcelain=v1'],cwd=repo,text=True),tracked_diff=subprocess.check_output(['git','diff','--stat'],cwd=repo,text=True),identities=ids,production_changes=False,deployment=False,commit=False,push=False,p2_applied=False)
(out/'status.json').write_text(json.dumps(status,indent=2)+'\n')
# Preserve full-map structural/flood/portal stage records without enormous node dumps.
allstages={}
for n in ['trace-p1','trace-uniform','trace-off-p1','trace-off-uniform']:
 text=re.sub(r'\x1b\[[0-9;]*m','',(r/n/'stdout.log').read_text());allstages[n]=[l for l in text.splitlines() if l.startswith('P3 SNAP') or l.startswith('P3 PORTALS') or 'outside leaves' in l or 'Reached occupant' in l or 'Processing hull' in l]
(out/'stage-summary.json').write_text(json.dumps(allstages,indent=2)+'\n')
# machine-readable residual source regression proof
w=json.load(open(out/'witness-gate.json'));gate={mode:{name:sum(row['contents'][name]!=row['expected'] for row in rows) for name in ['stock','p1','uniform']} for mode,rows in w.items()}
(out/'proposed-gate-demonstration.json').write_text(json.dumps(gate,indent=2)+'\n')
(out/'README.md').write_text('Research only; no production patch or acceptance receipt. Commands and artifact hashes are in reproduction.json. Scripts retain absolute paths to preserved frozen inputs and disposable builds. All MAP bytes reference the locked repository fixtures; no authored MAP is changed. Instrumentation source contains the rejected uniform diagnostic, never apply it to production. Full intermediate trees and BSPs remain in /tmp/qqbsp-phase3; bounded first-divergence, source occupancy, portal and compilation records are preserved here. Node fingerprints use source line / plane / ordered winding coordinate bytes, never pointers. Source-oracle segment minimization checks endpoints and all pairwise crossings of the affine plane-distance functions. See the report for the detected parser mistake and final corrected midpoint route.\n')
manifest={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json'}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
shutil.copyfile(r/'THIN_BRUSH_PHASE3.md',r/'deliverables/THIN_BRUSH_PHASE3.md')
print('files',len(manifest),'bytes',sum(p.stat().st_size for p in out.rglob('*') if p.is_file()))
