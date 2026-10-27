from pathlib import Path
import json,re,struct,hashlib,sys
r=Path('/tmp/qqbsp-phase3');rows=json.load(open(r/'reproduction.json'))
for row in rows:
 d=r/(row['compiler']+('-nofill' if row['nofill'] else ''))/row['mode'];txt=re.sub(r'\x1b\[[0-9;]*m','',(d/'stdout.log').read_text())
 row['peak_rss_kib']=int(re.search(r'Maximum resident set size \(kbytes\): (\d+)',(d/'time.txt').read_text())[1]);row['compiler_reported_seconds']=float(re.search(r'([\d.]+)s seconds elapsed',txt)[1]);row['leak_warnings']=re.findall(r'WARNING: Reached occupant[^\n]*',txt)
 # first two world hull0 trees stop before entity1; raw complete logs retained
 row['first_tree']={}
 first=txt.split('---- BrushBSP ----')[1]
 for key,pattern in [('nodes',r'([\d,]+) nodes\n'),('leaves',r'([\d,]+) leafs total'),('portals',r'([\d,]+) tree portals'),('tiny_portals',r'([\d,]+) tiny portals')]:
  m=re.search(pattern,first);row['first_tree'][key]=int(m[1].replace(',','')) if m else None
(r/'reproduction.json').write_text(json.dumps(rows,indent=2)+'\n')
def bsp(p):
 b=p.read_bytes();return dict(bytes=len(b),lumps=[struct.unpack_from('<ii',b,4+8*i)[1] for i in range(15)],sha256=hashlib.sha256(b).hexdigest())
a=bsp(r/'target-p1/full-on.bsp');b=bsp(r/'nofill-hull0/full-on.bsp');c=bsp(r/'target-uniform/full-on.bsp')
out=dict(p1_filled=a,p1_nofill=b,uniform_leaking=c,fill_control_bytes=b['bytes']-a['bytes'],split_control_bytes=c['bytes']-b['bytes'],total=c['bytes']-a['bytes'],fill_control_fraction=(b['bytes']-a['bytes'])/(c['bytes']-a['bytes']))
(r/'growth.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ['p1_filled','p1_nofill','uniform_leaking']})
