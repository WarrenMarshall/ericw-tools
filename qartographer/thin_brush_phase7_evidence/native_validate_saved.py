from pathlib import Path
import sys,json,re,hashlib,struct
sys.dont_write_bytecode=True
base=Path('/tmp/qqbsp-phase7');e=base/'evidence/native-ordinary-final';game=e/'game/id1'
result=json.loads((e/'results.json').read_text());result['states']={}
for name in ['start','end']:
 text=(game/(name+'.sav')).read_text();player=next(b for b in re.findall(r'\{[^{}]*\}',text) if '"classname" "player"' in b)
 kv=dict(re.findall(r'"([^"\n]+)" "([^"\n]*)"',player))
 result['states'][name]={k:kv.get(k,'0') for k in ['origin','velocity','movetype','flags','health']}
 result['states'][name]['server_time']=float(text.splitlines()[20])
assert result['exit']==0 and 'QQBSP_PHASE7_NATIVE_DONE' in (e/'engine.log').read_text()
a,b=[list(map(float,result['states'][n]['origin'].split())) for n in ['start','end']]
assert b[0]-a[0]>100 and abs(b[1]-a[1])<.01 and abs(b[2]-a[2])<.01
for state in result['states'].values():assert int(float(state['flags']))&512 and float(state['health'])>0 and float(state['movetype'])==3
assert result['states']['end']['server_time']>result['states']['start']['server_time']
sys.path.insert(0,str(base/'source/qartographer'))
import spline_smooth_collision_compile as c
from wildspline_bsp_collision_compile import brushes,expanded
geometry=brushes((base/'source/testmaps/qbsp_simple_sealed2.map').read_text());cells=[expanded(g,(16,16,28)) for g in geometry]
ray_origin=(a[0],a[1],a[2]+4);entries=[]
for cell in cells:
 lo,hi=-float('inf'),float('inf')
 for n,d in cell:
  v=d-c.dot(n,ray_origin)
  if n[0]==0:
   if v<0:break
  elif n[0]>0:hi=min(hi,v/n[0])
  else:lo=max(lo,v/n[0])
 else:
  if hi>=max(lo,0):entries.append(max(lo,0))
entry=a[0]+min(entries)
assert abs((entry-b[0])-1/32)<1e-6,(entry,b)
result['source_predicted_wall_entry_x']=entry
result['source_checks']=[]
for label,point,want in [('start',a,False),('end',b,False),('past_wall',[entry+.1,b[1],b[2]],True)]:
 point=(point[0],point[1],point[2]+4);margin=c.margin(point,cells);assert (margin<0)==want
 result['source_checks'].append(dict(name=label,oracle_point=point,source_margin=margin,solid=want))
raw=(e/'ordinary.bsp').read_bytes();lumps=[struct.unpack_from('<ii',raw,4+8*i) for i in range(15)]
original=(base/'evidence/campaign/ordinary-L-room/input.bsp').read_bytes();original_lumps=[struct.unpack_from('<ii',original,4+8*i) for i in range(15)]
for i in [1,5,9,14]:
 off,n=lumps[i];old,m=original_lumps[i];assert raw[off:off+n]==original[old:old+m]
assert lumps[4][1] and lumps[8][1]
result['visibility_bytes']=lumps[4][1];result['light_bytes']=lumps[8][1]
result['acceptance']='PASS';result['scope']='Ordinary L-room native player/hull1 only; not Halloween, thin blockers or native hull2 acceptance.'
result['test_setup_correction']='Initial handwritten expected X=-32 belonged to another room; saved runtime was not rerun. Source/Minkowski ray intersection independently gives first blocker X=80.'
(e/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
