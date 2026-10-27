import json,sys,pathlib
sys.dont_write_bytecode=True
sys.path.insert(0,'/home/warrenmarshall/dev/ericw-tools/qartographer')
import spline_smooth_collision_compile as c
r=pathlib.Path('/tmp/qqbsp-phase3');data=json.load(open(r/'leak-detour.json'));rows={}
for mode,v in data.items():
 bs={n:c.BSP(r/d/mode/(mode+'.bsp')) for n,d in [('stock','stock'),('p1','p1'),('p1-nofill','p1-nofill'),('uniform','uniform')] if (r/d/mode/(mode+'.bsp')).exists()}
 rows[mode]=[dict(s,contents={n:b.contents(s['point'],hull=0) for n,b in bs.items()}) for s in v['samples']]
(r/'leak-bsp.json').write_text(json.dumps(rows,indent=2))
for m,v in rows.items():
 print(m,[(s['segment'],s['t'],s['point'],s['source_margin'],s['contents']) for s in v if s['contents'].get('p1-nofill')==-2][:5])
