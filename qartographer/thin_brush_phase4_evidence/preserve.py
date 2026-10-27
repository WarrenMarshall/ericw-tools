from pathlib import Path
import json,hashlib,shutil,subprocess,difflib
r=Path('/tmp/qqbsp-phase4');repo=Path('/home/warrenmarshall/dev/ericw-tools');e=r/'deliverables/thin_brush_phase4_evidence';e.mkdir(parents=True,exist_ok=True)
for name in ['terminal.json','terminal-cap.json','witness-paths.json','actor-route.json','actor-source-route.json','actor-points.json','instrument.py','extend.py','target-actor.py','analyze.py','terminal.py','cap-terminal.py','actor.py','source-route.py','probe-points.py','configure.log','build.log','build-retry.log','build-retry2.log','build-extended.log','build-target.log']:
 if (r/name).exists():shutil.copyfile(r/name,e/name)
# Selected source-supported hull-0 path, independent of huge temporary dumps.
ns=json.load(open(r/'nodes.json'));small=[]
for n in ns:
 if n['pass_']!=1:continue
 n['sides']={k:v for k,v in n['sides'].items() if k in ['-1','15143']};small.append(n)
(e/'hull0-path.json').write_text(json.dumps(small,indent=2))
# Preserve instrumentation as inert diff against preserved prior diagnostic.
for f in ['brushbsp.cc','outside.cc']:
 old=(Path('/tmp/qqbsp-phase3/source/qbsp')/f).read_text().splitlines(True);new=(r/'source/qbsp'/f).read_text().splitlines(True)
 (e/(f+'.instrumentation.patch')).write_text(''.join(difflib.unified_diff(old,new,fromfile='phase3/'+f,tofile='phase4/'+f)))
# Original data receipts for both frozen maps, cap, sky, portal, matrix and CSG.
links={
 'first-cap':['thin_brush_phase3_evidence/cap-oracle.json','thin_brush_phase3_evidence/root-diff.json'],
 'sky-gap':['thin_brush_phase3_evidence/sky-ancestors.json','thin_brush_phase3_evidence/leak-detour.json','thin_brush_phase3_evidence/leak-bsp.json'],
 'false-solids':['thin_brush_phase3_evidence/witness-gate.json','thin_brush_phase2_evidence/map-witnesses.json'],
 'portal-containment':['thin_brush_phase3_evidence/leak-oracle.json','thin_brush_phase3_evidence/instrumented-logs/uniform-full-on.log'],
 'thin-csg':['thin_brush_evidence/trace.log','thin_brush_phase2_evidence/actor-witnesses.json','thin_brush_phase2_evidence/matrix-comparison.json','thin_brush_phase2_evidence/uniform-epsilon-matrix.json','thin_brush_phase2_evidence/traces'],
}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
index={}
for k,paths in links.items():
 rows=[]
 for name in paths:
  p=repo/'qartographer'/name
  if p.is_file():rows.append(dict(path='../'+name,sha256=sha(p)))
  elif p.is_dir():
   rows.extend(dict(path='../'+str(q.relative_to(repo/'qartographer')),sha256=sha(q)) for q in sorted(p.rglob('*')) if q.is_file())
 index[k]=rows
index['frozen_maps']=[dict(path='../fixtures/'+mode+'.map',sha256=sha(repo/'qartographer/fixtures'/f'{mode}.map')) for mode in ['full-on','full-off']]
(e/'witness-index.json').write_text(json.dumps(index,indent=2))
for name in ['ancestor-cap.json','cap-ancestor.py','final-ids.json','final-ids.py']:
 shutil.copyfile(r/name,e/name)
for stage in ['source','post-csg']:
 src=r/f'off-extended/input.bsp.p4-{stage}2.tsv';(e/f'actor-{stage}-blocker.tsv').write_text(''.join(l for l in src.open() if l.split('\t')[1] in ['13366','13174']))
for name in ['off','off-extended','off-target']:
 src=r/name
 for f in ['time.txt','stdout.log']:
  if f=='time.txt':shutil.copyfile(src/f,e/(name+'-time.txt'))
  else:
   needles=['P3 SNAP','P3 PORTALS','P3 LEAKPORTAL','Processing hull','Reached occupant','outside leafs filled','outside leafs','P4 CLIP','P4 CHECK','P4 ROUTE path=110001001000 ', 'seconds elapsed']
   (e/(name+'-events.log')).write_text(''.join(l for l in (src/f).open() if any(x in l for x in needles)))
# Keep full direct fragment-routing sequence for the independently certified box.
(e/'actor-blocker-route.log').write_text(''.join(l for l in (r/'off-target/stdout.log').open() if 'P4 ROUTE ' in l and 'line=13366 ' in l))
# compact actual node/leaf routes, partition geometry and initial leaf contents.
paths={4:set(),5:set()}
a=json.load(open(r/'actor-points.json'))
for p in a['points']:
 ps=p['pass_'];path=p['path'];paths[ps].update(path[:d] for d in range(len(path)+1))
for row in (r/'off/input.bsp.p4-leak2.tsv').read_text().splitlines()[1:]:
 a=row.split('\t')
 for path in a[1:3]:paths[5].update(path[:d] for d in range(len(path)+1))
for ps in [4,5]:
 src=r/f'off-target/input.bsp.tree{ps}.tsv';(e/f'actor-tree{ps}.tsv').write_text(''.join(l for l in src.open() if l.split('\t')[0] in paths[ps]))
(e/'actor-contents.tsv').write_text(''.join(l for l in (r/'off-target/input.bsp.p4-contents.tsv').open() if (a:=l.split('\t')) and int(a[0]) in paths and a[1] in paths[int(a[0])]))
shutil.copyfile(r/'off/input.bsp.p4-leak2.tsv',e/'actor-leak-portals.tsv')
index['portal-containment'].append(dict(path='../thin_brush_phase3_evidence/instrumented-logs/trace-uniform/stdout.log',sha256=sha(repo/'qartographer/thin_brush_phase3_evidence/instrumented-logs/trace-uniform/stdout.log')))
(e/'witness-index.json').write_text(json.dumps(index,indent=2))
# Bound exact instrumented execution identities; no performance comparison asserted.
receipts=[]
for name in ['off','off-extended','off-target']:
 src=r/name;b=src/'input.bsp';data=b.read_bytes();import struct
 lumps=[struct.unpack_from('<ii',data,4+8*i)[1] for i in range(15)]
 counts={}
 for ps in range(1,6):
  nodes=leaves=0
  for l in (src/f'input.bsp.tree{ps}.tsv').open():
   if l.split('\t')[3]=='L':leaves+=1
   else:nodes+=1
  counts[str(ps)]=dict(nodes=nodes,leaves=leaves)
 receipts.append(dict(directory=str(src),map_sha256=sha(src/'input.map'),bsp_sha256=sha(b),bytes=len(data),lump_bytes=lumps,nodes=lumps[5]//44,leaves=lumps[10]//44,faces=lumps[7]//28,clipnodes=lumps[9]//12,tree_counts=counts,time_receipt=name+'-time.txt'))
(e/'trace-receipts.json').write_text(json.dumps(receipts,indent=2))
