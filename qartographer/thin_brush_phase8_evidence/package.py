from pathlib import Path
import shutil,json,hashlib,difflib,subprocess
b=Path('/tmp/qqbsp-phase8');e=b/'evidence';pub=b/'publish';pub.mkdir(exist_ok=True);dest=pub/'thin_brush_phase8_evidence';dest.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selected=['reproduction','accepted-experiment-campaign','accepted-experiment-matrix','accepted-experiment-roller','roller-context','ordinary-comparison','ordinary-nofill','policy','rejected-reconstruction']
for name in selected:
 shutil.copytree(e/name,dest/name,dirs_exist_ok=True)
for d in ['native-ordinary-final']:
 target=dest/d;target.mkdir(exist_ok=True)
 for p in (e/d).iterdir():
  if p.is_file():shutil.copyfile(p,target/p.name)
 for name in ['start.sav','end.sav','acceptance.cfg']:
  shutil.copyfile(e/d/'game/id1'/name,target/name)
# Preserve PRECISE receipts without multiplying identical full-map copies/captures.
for name in ['halloween-off-precise','halloween-on-precise']:
 d=dest/'precise'/name;d.mkdir(parents=True,exist_ok=True)
 for n in ['stdout.log','time.txt']:shutil.copyfile(e/'final-campaign'/name/n,d/n)
shutil.copyfile(e/'final-campaign/results.json',dest/'precise/campaign-results.json')
# The full established campaign aborts on the final candidate's reduced compile.
for name in ['final-p1-regression.log','final-focused.log','final-focused.xml','route-verification.json','route-verification.log','portal-oracle.json','portal-oracle.log','remaining-oracle.json','remaining-oracle.log','rotated-render-faces.json','rotated-render-verification.json','mixed-context-replay.log','policy.log','ordinary-comparison.log','ordinary-nofill.log','native.log','native-validation.log','configure.log','build-final5.log','build-restored.log','reconstruction.log','reconstruction-roller.log']:
 shutil.copyfile(e/name,dest/name)
# Root failure driver and patched failure logs; earlier pristine results remain in /tmp.
shutil.copytree(e/'final-p1-regression/patched',dest/'p1-regression-patched',dirs_exist_ok=True)
shutil.copytree(e/'reconstruction-roller',dest/'rejected-reconstruction/roller',dirs_exist_ok=True)
shutil.copytree(e/'reconstruction',dest/'rejected-reconstruction/campaign',dirs_exist_ok=True)
for p in b.glob('*.py'):shutil.copyfile(p,dest/p.name)
# Frozen independent oracle/policy and original semantic witnesses.
shutil.copytree(Path('/tmp/qqbsp-phase7/phase6/component'),dest/'independent-component',dirs_exist_ok=True)
for name in ['new-blocker-oracle.json','halloween-node-occupancy.json','sealed-node.json.fragment.json']:
 shutil.copyfile(Path('/tmp/qqbsp-phase7/evidence')/name,dest/('phase7-'+name))
shutil.copyfile(Path('/tmp/qqbsp-phase7/evidence/phase7-unaccepted.patch'),dest/'phase7-unaccepted.patch')
# Reconstruct the exact incremental implementation without changing the baseline.
old=Path('/tmp/qqbsp-phase7/source');src=b/'source';changes=[];patch=''
for p in sorted(src.rglob('*')):
 if not p.is_file() or '.git' in p.parts:continue
 rel=p.relative_to(src);prior=old/rel
 if prior.exists() and sha(p)==sha(prior):continue
 changes.append(str(rel));snapshot=dest/'implementation'/rel;snapshot.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,snapshot)
 patch+=''.join(difflib.unified_diff(prior.read_text().splitlines(True) if prior.exists() else [],p.read_text().splitlines(True),fromfile='a/'+str(rel) if prior.exists() else '/dev/null',tofile='b/'+str(rel)))
(dest/'phase8-on-phase7.patch').write_text(patch)
manifest=dict(baseline='4b505ae25e508a8910b031e94d6f1ea60ac06a95 + phase7-unaccepted.patch',changes=changes,source={rel:sha(src/rel) for rel in changes},binary=str(b/'final-qqbsp'),binary_sha256=sha(b/'final-qqbsp'),rebuilt_binary_sha256=sha(b/'build/qbsp/qqbsp'),predicate_sha256=sha(src/'include/qbsp/halfspace.hh'),phase7_predicate_sha256=sha(old/'include/qbsp/halfspace.hh'),precise_binary_sha256=sha(b/'phase8-unaccepted-qqbsp'),rejected_reconstruction_binary_sha256=sha(b/'reconstruction-qqbsp'),installed_sha256=sha(Path('/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp')),status='PARTIAL, UNACCEPTED, NO PROMOTION')
(dest/'status.json').write_text(json.dumps(manifest,indent=2))
# Keep raw output bytes inert under the established evidence naming convention.
for p in list(dest.rglob('*.bsp')):p.rename(p.with_suffix('.bsp.bin'))
print(json.dumps(manifest,indent=2))
