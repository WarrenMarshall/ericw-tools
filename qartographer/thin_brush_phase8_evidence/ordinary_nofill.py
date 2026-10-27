from pathlib import Path
import sys,subprocess,shutil,json,hashlib,struct
sys.dont_write_bytecode=True
base=Path('/tmp/qqbsp-phase8');e=base/'evidence/ordinary-nofill';e.mkdir(exist_ok=False)
# Reuse the comparison's BSP29 reader and oracle setup without invoking its runner.
s=Path('/tmp/qqbsp-phase8/ordinary_compare.py').read_text();reader=s[s.index('class BSP29'):s.index('installed=Path(')]
sys.path.insert(0,str(base/'source/qartographer'))
import spline_smooth_collision_compile as c
from wildspline_bsp_collision_compile import brushes,expanded
exec(reader)
source=base/'source/testmaps/qbsp_simple_sealed2.map';geometry=brushes(source.read_text());readers={};rows=[]
for label,binary in [('accepted',Path('/mnt/fb91e326-b6dc-4352-b43c-7517fcce8b77/Dropbox/Quake/Utils/linux/qqbsp')),('candidate',base/'final-qqbsp')]:
 d=e/label;d.mkdir();m=d/'input.map';shutil.copyfile(source,m);cmd=[str(binary),'-nofill','-notex','-nopercent','-threads','1',str(m)]
 with (d/'compile.log').open('w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=55)
 assert p.returncode==0;readers[label]=BSP29(m.with_suffix('.bsp'));rows.append(dict(name=label,command=cmd,binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest()))
vertices=[v for _,vs,_ in geometry for v in vs];report={}
for hull,radius,offset in [(0,(0,0,0),0),(1,(16,16,28),4),(2,(32,32,44),20)]:
 cells=[expanded(g,radius) for g in geometry];lo=[min(v[i] for v in vertices)-radius[i]-4 for i in range(3)];hi=[max(v[i] for v in vertices)+radius[i]+4 for i in range(3)];failures=[];diff=[];checked=0
 for k in range(1,513):
  point=tuple(lo[i]+c.halton(k,[2,3,5][i])*(hi[i]-lo[i]) for i in range(3));margin=c.margin(point,cells)
  if abs(margin)<1e-6:continue
  checked+=1;want=-2 if margin<0 else -1;engine=(point[0],point[1],point[2]-offset);a=readers['accepted'].contents(engine,hull=hull);b=readers['candidate'].contents(engine,hull=hull)
  if b!=want:failures.append(dict(point=point,margin=margin,want=want,actual=b))
  if a!=b:diff.append(dict(point=point,accepted=a,candidate=b))
 report[str(hull)]=dict(samples=checked,source_failures=failures,baseline_differences=diff)
result=dict(compiles=rows,hulls=report,pass_=all(not h['source_failures'] and not h['baseline_differences'] for h in report.values()))
(e/'results.json').write_text(json.dumps(result,indent=2)+'\n');assert result['pass_'];print('PASS', {h:v['samples'] for h,v in report.items()})
